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
    if request.method == "POST":
        csv_file = request.FILES["csv_upload"].temporary_file_path()
        # dataframe = pd.read_csv(csv_file, chunksize=300000, delimiter=',', encoding= 'unicode_escape')
        dataframe = pd.read_csv(csv_file, delimiter=',', encoding= 'unicode_escape')
        infos = dataProcessing(dataframe)
        print(infos)
        return render(request, 'dashboard.html', {"infos": infos})
    else:
        form = CsvImportForm() 
        return render(request, 'dashboard.html', {"form": form})

# ** Extract information about the dataset
# dataframe{pandas.DataFrame} data
# return infos{dict} dataframe information
def getInfos(dataframe):
    infos = {}
    infos["shape"] = {"line": dataframe.shape[0],
                      "col" : dataframe.shape[1]}
    ltype = []                          
    for c, n in zip(range(0, dataframe.shape[1]), dataframe.columns.values):
        ltype.append(str(n)+": " + str(type(dataframe._get_value(0,c, takeable=True))))
    infos["type"] = ltype
    return infos



def dataProcessing(dataframe):
    infos = getInfos(dataframe)
    return infos
