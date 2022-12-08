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
    err, countErr, dataframe = duplicated(err, countErr, dataframe)
    pdb.set_trace()

# ** Set aside duplicates 
# ** relative to columns InvoiceNo and StockCode
# err{pandas.Dataframe} stores rows set aside
# countErr{dict} stores the number of rows matched by a filter 
# dataframe{pandas.Dataframe} data
# return err, countErr, dataframe from which unwanted data has been removed
def duplicated(err, countErr, dataframe):
    d = dataframe.duplicated(subset = ['InvoiceNo', 'StockCode']) # return a boolean vector
    errDuplicated = dataframe[d==True]
    errDuplicated["Erreur"] = "Doublon"
    dataframe = dataframe[d==False] 
    countErr["Duplicate"] = errDuplicated.shape[0] + (0 if countErr.get('Duplicate')==None else countErr.get('Duplicate'))
    err = pd.concat(err, errDuplicated)
    return err, countErr, dataframe

# ** Process the country column
# err{pandas.Dataframe} stores rows set aside
# countErr{dict} stores the number of rows matched by a filter 
# dataframe{pandas.Dataframe} data
# return err, countErr, dataframe from which unwanted data has been removed
def country(err, countErr, dataframe):
    ## Unspecified
    c = dataframe['Country'] == "Unspecified" # return a boolean vector
    errCountry = dataframe[c==True]
    errCountry["Erreur"] = "Pays: Unspecified" 
    dataframe = dataframe[c==False] 
    countErr["Country"] = errCountry.shape[0] + (0 if countErr.get('Country')==None else countErr.get('Country'))
    err = pd.concat(err, errCountry)
    ## None
    c = dataframe['Country'] == None
    errCountry = dataframe[c==True]
    errCountry["Erreur"] = "Pays: None"
    dataframe = dataframe[c==False] 
    countErr["Country"] = errCountry.shape[0] + (0 if countErr.get('Country')==None else countErr.get('Country'))
    err = pd.concat(err, errCountry)
    return err, countErr, dataframe

# ** Process the InvoiceDate column
# err{pandas.Dataframe} stores rows set aside
# countErr{dict} stores the number of rows matched by a filter 
# dataframe{pandas.Dataframe} data
# return err, countErr, dataframe from which unwanted data has been removed
def invoicedate(err, countErr, dataframe):
    date_pattern = "^([0]{0,1}[1-9]|1[012])\/([1-9]|([012][0-9])|(3[01]))\/((\d\d\d\d)) [012]{0,1}[0-9]:[0-6][0-9]$"
    id = dataframe['InvoiceDate'].str.match(date_pattern) # return a boolean vector
    errDate = dataframe[id==False]
    errDate["Erreur"] = "La date est incorrecte"
    dataframe = dataframe[id==True]
    countErr["Date"] = errDate.shape[0]
    err = pd.concat(err, errDate)
    return err, countErr, dataframe

def quantity(err, countErr, dataframe):
    q = dataframe["Quantity"] < 0
    errQ = dataframe[q==True]
    errQ["Erreur"] = "Quantité négatif"
    dataframe = dataframe[id==False]
    countErr["Quantity"] = errQ.shape[0]
    err = pd.concat(err, errQ)
    return err, countErr, dataframe

def unitprice(err, countErr, dataframe):
    up = dataframe["UnitPrice"] <= 0
    errUp = dataframe[up==True]
    errUp["Erreur"] = "UnitPrice négatif ou 0"
    dataframe = dataframe[up==False]
    countErr["UnitPrice"] = errUp.shape[0]
    err = pd.concat(err, errUp)
    return err, countErr, dataframe

def stockcode(err, countErr, dataframe):
    sc_pattern = "^[a-zA-Z]" #"^\d{1,5}\d|[a-zA-Z]$"
    sc = dataframe['StockCode'].str.match(sc_pattern) # return a boolean vector
    errSc = dataframe[sc==True]
    errSc["Erreur"] = "StockCode ne correspond pas au motif suivant: ^\d{1,6}$|^\d{1,5}[a-zA-Z]$"
    dataframe = dataframe[sc==False]
    countErr["StockCode"] = errSc.shape[0]
    err = pd.concat(err, errSc)
    return err, countErr, dataframe

def invoiceno(err, countErr, dataframe):
    in_pattern = "^\d{6}$"
    _in = dataframe["InvoiceNo"].str.match(in_pattern)
    errIn = dataframe[_in==True]
    errIn["Erreur"] = "InvoiceNo ne correspond pas au motif suivant: ^\d{6}$"
    dataframe = dataframe[_in==False]
    countErr["InvoiceNo"] = errIn.shape[0]
    err = pd.concat(err, errIn)
    return err, countErr, dataframe




