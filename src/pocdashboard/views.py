from tempfile import NamedTemporaryFile, TemporaryFile
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import pdb; #pdb.set_trace()
from pocdashboard.forms import CsvImportForm
import pandas as pd
import io, time, re, os
from django.http.response import HttpResponse, HttpResponseRedirect
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
import mimetypes
from pocdashboard.models import * #Country, Detailfacture, Invoice, Product
from django.db.models import Count
from django.conf import settings
import sqlalchemy
from sqlalchemy.sql import text
from django.http import JsonResponse
from django.db import connection

# Connexion
from django.views.decorators.csrf import csrf_protect
@csrf_protect
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
@csrf_protect
def dashboard(request):
    # pdb.set_trace()
    form = CsvImportForm() 
    if request.method == "POST":
        csv_file = request.FILES["csv_upload"].temporary_file_path()                   # Get the sent file   
        if(re.search(r".csv",csv_file)):                   
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
            addDataInDB(dataframe)                                                         # Add in the data base the data from cleaning phase
            return render(request, 'dashboard/dashboard.html', {"form"     : form,
                                                                "infos"    : infos,
                                                                "resInfos" : resInfos,
                                                                "lInfos"   : lInfos,
                                                                "countErr" : countErr}
                          )
        # else: messages.success(request, ("fichier non conforme"))
    return render(request, 'dashboard/dashboard.html', {"form": form})

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
    # Description
    dataframe["Description"].replace('\s*$', '', regex=True, inplace=True) # remove white space at the end of string
       
    return err, countErr, dataframe
    
# ** Set aside unwanted data 
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

# ** Send a temp file containing data set aside when the
#**  customer clicks the downloaded button
# request{django.core.handlers.wsgi.WSGIRequest}
# object{pandas.Dataframe} containing errors set aside from the cleaningPhase
#                            if it is none it means that the client is making a 
#                            request to download the data set aside                        
# return reponse{django.http.response.StreamingHttpResponse} if it is a download request
def fileErr(request, object=None):
    # Create a temp file
    if(isinstance(object, pd.DataFrame)):
        # pdb.set_trace()
        f = NamedTemporaryFile(delete=False)  #  If delete is true (the default), the file is deleted as soon as it is closed
        object.to_csv(f, sep=',')
        request.session["errpath"] = f.name.replace("\\","/") # save the path of the temp file 
    # Send the temp file when the user click on button
    else:
        if(request.session.get("errpath") != None):
            # pdb.set_trace()
            filename="err.csv"
            file_path = request.session.get("errpath") 
            # StreamingHttpResponse is used to stream a response from Django to the browser.
            # This can be used to generate a response that takes a long time or uses a lot of memory.
            # For example, this is useful for generating large CSV files.
            response = StreamingHttpResponse(FileWrapper(open(file_path, 'rb')),
                                            content_type=mimetypes.guess_type(file_path)[0])
            response['Content-Length']      = os.path.getsize(file_path)
            response['Content-Disposition'] = "Attachment;filename=%s" % filename
            # f.close()
            # os.remove(file_path)
            return response
        else: return redirect('dashboard')


# ** Add data from dataframe to database
# dataframe{pandas.Dataframe} data from cleaningPhase()
def addDataInDB(dataframe):
    # pdb.set_trace()
    user = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']
    host = settings.DATABASES['default']['HOST']
    db_url = 'postgresql://{user}:{password}@{host}:5432/{database_name}'.format(user=user, 
    password=password, host=host, database_name=database_name)
    engine = sqlalchemy.create_engine(db_url, echo=False)
    
    # country 
    country = pd.DataFrame(data=dataframe["Country"].unique(), columns = ["country_name"])
    country["zone_name"] = None
    country.to_sql(name="tempcountry", con = engine, index=False, if_exists='replace')
   
    res = requeteDB(setDifference(table="country", temptable="tempCountry", pk="country_name"))
    resdf = pd.DataFrame(list(map(list, res)), columns=["country_name", "zone_name"])
    resdf.to_sql(name="country", con = engine, index=False, if_exists='append')

    # invoice
    bool = ~dataframe.duplicated(subset = ["InvoiceNo"])        
    invoiceno = dataframe[bool][["InvoiceNo", "InvoiceDate", "CustomerID", "Country"]]
    invoiceno["CustomerID"] = invoiceno["CustomerID"].astype(str).replace('\.\d+', '', regex=True)
    invoiceno.columns = ["invoice_no", "invoice_date", "customer_id", "country_name"]
    invoiceno.to_sql(name="tempinvoice", con = engine, index=False, if_exists='replace')

    res = requeteDB(setDifference(table="invoice", temptable="tempinvoice", pk="invoice_no"))
    resdf = pd.DataFrame(list(map(list, res)), columns=["invoice_no", "invoice_date", "customer_id", "country_name"])
    resdf.to_sql(name="invoice", con = engine, index=False, if_exists='append')
    
    # product
    bool = ~dataframe.duplicated(subset = ["StockCode"])
    product = dataframe[bool][["StockCode", "Description"]]
    product.columns = ["stock_code", "description"]
    product.to_sql(name="tempproduct", con = engine, index=False, if_exists='replace')
   
    res = requeteDB(setDifference(table="product", temptable="tempproduct", pk="stock_code"))
    resdf = pd.DataFrame(list(map(list, res)), columns=["stock_code", "description"])
    resdf.to_sql(name="product", con = engine, index=False, if_exists='append')
    
    # detailfacture
    detailfacture = dataframe[["UnitPrice", "Quantity", "InvoiceNo", "StockCode"]]
    detailfacture.columns = ["unit_price", "quantity", "invoice_no", "stock_code"]
    detailfacture.to_sql(name="tempdetailfacture", con = engine, index=True, if_exists='replace')

    res = requeteDB(('''
                        SELECT temp.unit_price, temp.quantity, temp.invoice_no, temp.stock_code
                        FROM tempdetailfacture temp
                        WHERE NOT EXISTS (SELECT 1
                        FROM detailfacture t
                        WHERE t.invoice_no = temp.invoice_no AND t.stock_code = temp.stock_code) ;
                    ''',)
                    )
    resdf = pd.DataFrame(list(map(list, res)), columns=["unit_price", "quantity", "invoice_no", "stock_code"])
    resdf.to_sql(name="detailfacture", con = engine, index=False, if_exists='append')
    
    trunctable()

#** Switch the claim send by the client to the corresponding 
#** functions to get the desired data from the database 
def getDataForChart(request):
    
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~ Graphe principal ~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    if request.POST.get("result[claim]")   == "pr":
        resultat = dict(requeteDB(venteParProduit(request.POST.get("result[choice]"), 
                                                  request.POST.get("result[limit]"))))
    elif request.POST.get("result[claim]") == "pa":
        resultat = dict(requeteDB(venteParPays(request.POST.get("result[choice]"), 
                                               request.POST.get("result[limit]"))))
    elif request.POST.get("result[claim]") == "_date":
        resultat = dict(requeteDB(venteDesProduitParDate()))
        
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~ Graphe de detail ~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        
    elif request.POST.get("result[claim]") == "prpa":
        resultat = dict(requeteDB(detailProduit(request.POST.get('result[data]'), 
                                                request.POST.get("result[choice]"), 
                                                request.POST.get("result[limit]"))))
    elif request.POST.get("result[claim]") == "papr":
        resultat = dict(requeteDB(detailPays(request.POST.get('result[data]'), 
                                             request.POST.get("result[choice]"), 
                                             request.POST.get("result[limit]"))))
    elif request.POST.get("result[claim]") == "dprpa":
        resultat1 = dict(requeteDB(detailProduitParDate(request.POST.get('result[data]'),
                                                       request.POST.get("result[choice]"),
                                                       request.POST.get("result[limit]"))))
        resultat2 = dict(requeteDB(detailPaysParDate(request.POST.get('result[data]'),
                                                     request.POST.get("result[choice]"),
                                                     request.POST.get("result[limit]"))))
        resultat = [resultat1, resultat2]
    else:
        resultat = None
    return JsonResponse({"data": resultat, "claim": request.POST.get("result[claim]")})
    
# ================== QUERIES ==================

#** Connection with the database
# sql_request{tuple} sql query and and these parameters
# return row{queryset} sql query result data
def requeteDB(sql_request):
    with connection.cursor() as cursor:
        cursor.execute(*sql_request)
        row = cursor.fetchall()
    return row

# ** Quantity of each product sold
# choice{str} 'DESC' or 'ASC'
# limit{str|int} number of rows that we keep from the query
# return {tuple} sql query and these parameters
def venteParProduit(choice, limit):
    return("""
        SELECT description, nb
        FROM (
                SELECT stock_code, SUM(quantity*unit_price) as nb
                FROM detailfacture 
                GROUP BY stock_code
            ) as cpr, product as pr
        WHERE cpr.stock_code = pr.stock_code 
        ORDER BY nb {0}
        LIMIT %s
            """.format(choice), [limit])

# ** Quantity sold in each country
# choice{str} 'DESC' or 'ASC'
# limit{str|int} number of rows that we keep from the query
# return {tuple} sql query and these parameters
def venteParPays(choice, limit):
    return('''
            SELECT country_name, Sum(quantity*unit_price) as nb
        	FROM detailfacture as df, 
            (
        		SELECT invoice_no, country_name 
                FROM invoice
        	) as i
        	WHERE df.invoice_no = i.invoice_no
			Group By country_name
            Order by nb {0}
            Limit %s
           '''.format(choice),[limit])

# ** Quantity of product sold in each country
# produit{str} product name (product.description)
# choice{str} 'DESC' or 'ASC'
# limit{str|int} number of rows that we keep from the query
# return {tuple} sql query and these parameters
def detailProduit(produit, choice, limit):
    return('''
           SELECT i.country_name, SUM(iq.quantity*iq.unit_price) as total
           FROM invoice as i, (
               SELECT invoice_no, quantity, unit_price
               FROM detailfacture as df, (
                   SELECT stock_code
                   FROM product
                   WHERE description = %s
	           ) as sc
               WHERE sc.stock_code = df.stock_code
           ) as iq
           WHERE iq.invoice_no = i.invoice_no
           GROUP BY country_name
           ORDER BY total {0}
           LIMIT %s
           '''.format(choice), [produit, limit])

# ** Quantity of each product sold in this country
# pays{str} country name (product.description)
# choice{str} 'DESC' or 'ASC'
# limit{str|int} number of rows that we keep from the query
# return {tuple} sql query and these parameters    
def detailPays(pays, choice, limit):
    return('''
           Select description, SUM(quantity*unit_price) as total
           From product as p, (
               Select df.stock_code, df.quantity, df.unit_price
               From detailfacture as df, (
                   Select i.country_name, i.invoice_no
                   From invoice as i
                   Where country_name = %s
                ) as ci
                Where ci.invoice_no = df.invoice_no
            ) as sq
            Where sq.stock_code = p.stock_code
            Group By description
            ORDER BY total {0} 
            LIMIT %s
           '''.format(choice), [pays, limit])

# ** Quantity sold per month
# return {tuple} sql query and these parameters
def venteDesProduitParDate():
    return('''
                Select to_char(_date, 'MM/YYYY'), nb
                From (
	                Select _date, Sum(quantity*unit_price) as nb
	                From detailfacture as df, (
		                Select invoice_no, TO_DATE(to_char(TO_DATE(invoice_date, 'MM/DD/YYYY'), 'MM/YYYY'), 'MM/YYYY') as _date
		                From invoice) as invd
	                Where df.invoice_no = invd.invoice_no
	                Group By _date
	                Order By _date
                ) as tab
           ''', )

# **Quantity of each product sold in this month (_date)
# _date{str} date (mm/yyyy)
# choice{str} 'DESC' or 'ASC'
# limit{str|int} number of rows that we keep from the query
# return {tuple} sql query and these parameters    
def detailProduitParDate(_date, choice, limit):
    return('''
                Select description, Sum(quantity*unit_price) as nb
                From product as p, (
	                Select stock_code, quantity, unit_price
	                From detailfacture as df, (
		                Select invoice_no
		                From(
			                Select invoice_no,  to_char(TO_DATE(invoice_date, 'MM/DD/YYYY'), 'MM/YYYY') as _date
			                From invoice) as invd
		                Where invd._date = %s ) as subt
	                Where subt.invoice_no = df.invoice_no) as stq
                Where stq.stock_code = p.stock_code
                Group By description
                Order By nb {0}
                Limit %s
           '''.format(choice), [_date, limit])

# ** quantity sold in each country in this month (_date)
# _date{str} date (mm/yyyy)
# choice{str} 'DESC' or 'ASC'
# limit{str|int} number of rows that we keep from the query
# return {tuple} sql query and these parameters    
def detailPaysParDate(_date, choice, limit):
    return('''
                Select country_name, Sum(quantity*unit_price) as nb
                From detailfacture as df, (
                    Select invoice_no, country_name
                    From(
                        Select invoice_no, country_name, to_char(TO_DATE(invoice_date, 'MM/DD/YYYY'), 'MM/YYYY') as _date
                        From invoice) as invd
                    Where invd._date = %s)  as subt
                Where subt.invoice_no = df.invoice_no
                Group By country_name
                Order By nb {0} 
                Limit %s
           '''.format(choice), [_date, limit])

#** Set difference table \ temptable
# table{str} table name
# temptable{str} temp table name
# return {tuple} sql query and these parameters 
def setDifference(table, temptable, pk): # table nor column names as parameter arguments
    return('''
                SELECT temp.*
                FROM {1} temp
                WHERE NOT EXISTS (SELECT 1 FROM {0} t WHERE t.{2} = temp.{2});
           '''.format(table, temptable, pk), )

#** Removes all rows from a set of tables
def trunctable():
    tempProduct.objects.all().delete()
    tempInvoice.objects.all().delete()
    tempDetailfacture.objects.all().delete()
    tempCountry.objects.all().delete()