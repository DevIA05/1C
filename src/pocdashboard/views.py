from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import pdb; #pdb.set_trace()
from pocdashboard.forms import CsvImportForm
import pandas as pd
import io
import time

# Connexion
def login_user(request):
    # Récupération des identifiants
    if request.method == "POST":
        matricule = request.POST['matricule'] 
        password = request.POST['password']
        user = authenticate(request, username=matricule, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.success(request, ("Erreur d'identifiant ou de mot de passe, veuillez ressayer"))
            return redirect('login')
    else:
        return render(request, 'login.html', {})

# Déconnexion
def logout_user(request):
    logout(request)
    messages.success(request, ("Session deconnectée"))
    return redirect('login')

# Dashboard
def dashboard(request):
    # pdb.set_trace()
    form = CsvImportForm() 
    if request.method == "POST":
        csv_file = request.FILES["csv_upload"].temporary_file_path()
        # dataframe = pd.read_csv(csv_file, chunksize=300000, delimiter=',', encoding= 'unicode_escape')
        dataframe = pd.read_csv(csv_file, delimiter=',', encoding= 'unicode_escape')
        infos=getInfos(dataframe)
        cleaningPhase(dataframe)
        return render(request, 'dashboard.html', {"form": form,
                                                  "l": infos["shape"]["line"], "c": infos["shape"]["col"],
                                                  "type": infos["type"],
                                                  "country": infos["country"]["lcountry"], "nbC": infos["country"]["nbcountry"],
                                                  "description": infos["description"]["ldescription"], "nbD": infos["description"]["nbdescription"]})
    else: return render(request, 'dashboard.html', {"form": form})

# ** Extract information about the dataset
# dataframe{pandas.DataFrame} data
# return infos{dict} dataframe information
def getInfos(dataframe):
    infos = {}
    # Dimension    
    infos["shape"] = {"line": dataframe.shape[0],
                      "col" : dataframe.shape[1]}
    # Column type
    ltype = {}
    for c, n in zip(range(0, dataframe.shape[1]), dataframe.columns.values):
        ltype[str(n)] = str(type(dataframe._get_value(0,c, takeable=True)))
    infos["type"] = ltype
    # Countries
    infos["country"] = {"lcountry" : dataframe["Country"].unique(),
                         "nbcountry": dataframe["Country"].unique().shape[0]}
    # Description
    infos["description"] = {"ldescription" : dataframe["Description"].unique(),
                            "nbdescription": dataframe["Description"].unique().shape[0]}
    return infos

def cleaningPhase(dataframe):
    err      = pd.DataFrame() # Met les erreurs dans un tableau
    countErr = {}             # Comptabilise les erreurs 

    # Set aside duplicates relative to columns InvoiceNo and StockCode
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe.duplicated(subset = ['InvoiceNo', 'StockCode']),
                                        comment="Doublon", name = "Duplicate")
    # Process the country column
    ##  Unspecified
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe['Country'] == "Unspecified",
                                        comment="Unspecified", name = "Country")
    ## None
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe['Country'] == None,
                                        comment="Pays: None", name = "Country")
    # Process the InvoiceDate column
    date_pattern = "^([0]{0,1}[1-9]|1[012])\/([1-9]|([012][0-9])|(3[01]))\/((\d\d\d\d)) [012]{0,1}[0-9]:[0-6][0-9]$"
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=~dataframe['InvoiceDate'].str.match(date_pattern),
                                        comment="La date est incorrecte", name = "Date")
    # Process the InvoiceDate column
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe["Quantity"] < 0,
                                        comment="Quantité négatif", name = "Quantity")
    # Process the UnitPrice column
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe["UnitPrice"] <= 0,
                                        comment="UnitPrice négatif ou 0", name = "UnitPrice")
    # Process the StockCode column
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe["StockCode"].str.match("^[a-zA-Z]"),
                                        comment= "StockCode ne correspond pas au motif", name = "StockCode")
    # Process the InvoiceNo column
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe["InvoiceNo"].str.match("^\d{6}$"),
                                        comment= "InvoiceNo ne correspond pas au motif", name = "InvoiceNo")

# ** Set aside duplicates 
# ** relative to columns InvoiceNo and StockCode
# err{pandas.Dataframe} stores rows set aside
# countErr{dict} stores the number of rows matched by a filter 
# dataframe{pandas.Dataframe} data
# booldf{pandas.Dataframe} boolean vector corresponding to the test result
# comment{str} comment
# name{str} dictionary key name
# return err, countErr, dataframe from which unwanted data has been removed
def dropLine(err, countErr, dataframe,
             booldf, comment, name):
    pdb.set_trace()
    errX = dataframe[booldf==True].copy()
    errX["Erreur"] = comment
    dataframe = dataframe[booldf==False]
    countErr[name] = errX.shape[0] + (0 if countErr.get(name)==None else countErr.get(name))
    err = pd.concat([err, errX])
    return err, countErr, dataframe

