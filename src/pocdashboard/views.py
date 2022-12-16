from tempfile import NamedTemporaryFile, TemporaryFile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import pdb; #pdb.set_trace()
from pocdashboard.forms import CsvImportForm
import pandas as pd
import io, time, re, os
from django.http.response import HttpResponse
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import mimetypes
from pocdashboard.models import * #Country, Detailfacture, Invoice, Product
from django.db.models import Count
from django.conf import settings
import sqlalchemy
from django.http import JsonResponse
from django.db import connection

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
        return render(request, 'login/login.html', {})

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
        csv_file = request.FILES["csv_upload"].temporary_file_path()                   # Get the sent file                              
        # dataframe = pd.read_csv(csv_file, chunksize=300000, delimiter=',', encoding= 'unicode_escape')
        dataframe = pd.read_csv(csv_file, delimiter=',', encoding= 'unicode_escape')  
        infos=getInfos(dataframe)                                                      # Get information about the dataset
        err, countErr, dataframe = cleaningPhase(dataframe)                            # Performs a dataset cleaning phase and return:
                                                                                       #    - a dataframe containing unwanted line
                                                                                       #    - a list count each unwanted data according to the condition 
                                                                                       #    - a dataframe with drop unwanted data 
        resInfos, lInfos=getInfos(dataframe, isCleaned=True)
        countErr["Total"] = str(sum(countErr.values())) + " (" + str("{:.1f}".format(  # Calculates the percentage of data set aside and keeps only the first decimal
            (sum(countErr.values())*100)/infos["Nombre de ligne"])) + "%)"
        #fileErr(request, object=err)
        # df = pd.DataFrame(data={"ColumnWithé": ["éà"]})
        fileErr(request, object=err)                                                   # Write in a temp file the dataframe containing unwanted line
        addDataInDB(dataframe)                                                       # Add in the data base the data from the cleaned dataframe
        return render(request, 'dashboard/dashboard.html', {"form"     : form,
                                                            "infos"    : infos,
                                                            "resInfos" : resInfos,
                                                            "lInfos"   : lInfos,
                                                            "countErr" : countErr}
                      )
    else: return render(request, 'dashboard/dashboard.html', {"form": form})

# ** Extract information about the dataset
# dataframe{pandas.DataFrame} data 
# return infos{dict} dataframe information
def getInfos(dataframe, isCleaned=False):
    infos = {}
    l     = {}
    # Dimension    
    infos["Nombre de ligne"]   = dataframe.shape[0]
    infos["Nombre de colonne"] = dataframe.shape[1]
    # Column type    
    if(isCleaned):
        # Countries
        l["lPays"] = dataframe["Country"].unique(),
        infos["Pays"]  = dataframe["Country"].unique().shape[0]
        # Description
        l["ldescription"] = dataframe["Description"].unique(),
        infos["StockCode"]  = dataframe["StockCode"].unique().shape[0]
        return infos, l
    else:
        ltype = ""
        for c, n in zip(range(0, dataframe.shape[1]), dataframe.columns.values):
            ltype += str(n) + ": " + str(type(dataframe._get_value(0,c, takeable=True))) + "\n"
        infos["Type de données"] = re.sub("[<>']|class", '', ltype) 
        return infos

#** Count and remove unwanted line from dataframe
# dataframe{pandas.DataFrame} data from input csv file
# return err{pandas.DataFrame} unwanted line with a comment column
#        countErr{dict} count each error according to the condition
#        dataframe{pandas.DataFrame} the input dataframe with unwanted elements removed
def cleaningPhase(dataframe):
    err      = pd.DataFrame() # Met les erreurs dans un tableau
    countErr = {}             # Comptabilise les erreurs 

    # Set aside duplicates relative to columns InvoiceNo and StockCode
    err, countErr, dataframe = dropLine(err, countErr, dataframe,
                                        booldf=dataframe.duplicated(subset = ['InvoiceNo', 'StockCode']), # return a boolean vector
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
    # Process the Quantity column
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
                                        booldf=~dataframe["InvoiceNo"].str.match("^\d{6}$"),
                                        comment= "InvoiceNo ne correspond pas au motif", name = "InvoiceNo")
       
    return err, countErr, dataframe
    
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
    if(booldf.any()):        
        errX = dataframe[booldf==True].copy()
        errX["Erreur"] = comment
        dataframe = dataframe[booldf==False]
        countErr[name] = errX.shape[0] + (0 if countErr.get(name)==None else countErr.get(name))
        err = pd.concat([err, errX])
    return err, countErr, dataframe

# from django import template
# register = template.Library()
# @register.filter
# def percentage(value, arg):
#     return format((value*100)/arg, "%")

# ** Create or Send a temp file
# containing errors set aside
# request{django.core.handlers.wsgi.WSGIRequest}
# object{pandas.Dataframe} containing errors set aside from the cleaningPhase
# return reponse{django.http.response.StreamingHttpResponse} if it is a download request
def fileErr(request, object=None):
    # Create a temp file
    if(isinstance(object, pd.DataFrame)):
        print("========== IF ==========")
        # pdb.set_trace()
        f = NamedTemporaryFile(delete=False) 
        object.to_csv(f, sep=',')
        request.session["errpath"] = f.name.replace("\\","/") # save the path of the temp file 
    # Send the temp file when the user click on button
    else:
        print("========== ELSE ==========")
        # pdb.set_trace()
        filename="err.csv"
        file_path = request.session.get("errpath") 
        # StreamingHttpResponse est utilisée pour diffuser une réponse en flux de Django vers le navigateur. 
        # Ceci peut être utilisé pour générer une réponse qui prend beaucoup de temps ou qui utilise beaucoup de mémoire. 
        # Par exemple, c’est utile pour générer de gros fichiers CSV.
        response = StreamingHttpResponse(FileWrapper(open(file_path, 'rb')),
                                        content_type=mimetypes.guess_type(file_path)[0])
        response['Content-Length']      = os.path.getsize(file_path)
        response['Content-Disposition'] = "Attachment;filename=%s" % filename
        # f.close()
        # os.remove(file_path)
        return response


# ** Add data from dataframe to database
# dataframe{pandas.Dataframe} data from cleaningPhase()
def addDataInDB(dataframe):
    # pdb.set_trace()
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']
    db_url = 'postgresql://{user}:{password}@localhost:5432/{database_name}'.format(user=user, 
    password=password, database_name=database_name)
    engine = sqlalchemy.create_engine(db_url, echo=False)

    # country 
    country = pd.DataFrame(data=dataframe["Country"].unique(), columns = ["country_name"])
    country.to_sql(name="country", con = engine, index=False, if_exists='append')
  
    # invoice
    bool = ~dataframe.duplicated(subset = ["InvoiceNo"])        
    invoiceno = dataframe[bool][["InvoiceNo", "InvoiceDate", "CustomerID", "Country"]]
    invoiceno["CustomerID"] = invoiceno["CustomerID"].astype(str).replace('\.\d+', '', regex=True)
    invoiceno.columns = ["invoice_no", "invoice_date", "customer_id", "country_name"]
    invoiceno.to_sql(name="invoice", con = engine, index=False, if_exists='append')
    
    # product
    bool = ~dataframe.duplicated(subset = ["StockCode"])
    product = dataframe[bool][["StockCode", "Description"]]
    product.columns = ["stock_code", "description"]
    product.to_sql(name="product", con = engine, index=False, if_exists='append')
    
    # detailfacture
    detailfacture = dataframe[["UnitPrice", "Quantity", "InvoiceNo", "StockCode"]]
    detailfacture.columns = ["unit_price", "quantity", "invoice_no", "stock_code"]
    detailfacture.to_sql(name="detailfacture", con = engine, index=False, if_exists='append')

def getDataForChart(request):
    
    if request.POST.get("result")   == "pr":
        resultat = requeteDB(venteParProduit())
        resultat = dict(resultat[:10])
        return JsonResponse({"data": resultat, "graph": "pr"})
    
    elif request.POST.get("result") == "pa":
        resultat = requeteDB(venteParPays())
        resultat = dict(resultat[:10])
        return JsonResponse({"data": resultat, "graph": "pa"})
    
    elif request.POST.get("result") == "prpa":
        res1 = requeteDB(venteParProduit())
        res2 = requeteDB(venteParPays())
        res1 = dict(res1[:10])
        res2 = dict(res2[:10])
        return JsonResponse({"dataPr": res1, "dataPa": res2, "graph": "prpa"})
    else:
        pass


def requeteDB(sql_request):
    with connection.cursor() as cursor:
        cursor.execute(sql_request)
        row = cursor.fetchall()
    return row

# ================== QUERIES ==================

def venteParProduit():
    return("""
        SELECT description, nb
        FROM (
                SELECT stock_code, COUNT(*) as nb 
                FROM detailfacture 
                GROUP BY stock_code
            ) as cpr, product as pr
        WHERE cpr.stock_code = pr.stock_code 
        ORDER BY nb DESC
            """)

def venteParPays():
    return("""
        Select country_name, Count(stock_code)
        From (
        	Select stock_code, country_name
        	From detailfacture as df, 
            (
        		Select invoice_no, country_name From invoice
        	) as i
        	Where df.invoice_no = i.invoice_no
        ) as pp
        Group By country_name
            """)
