from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import pdb; #pdb.set_trace()
from pocdashboard.forms import CsvImportForm
import pandas as pd
import io
from dask import dataframe as dd
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
        dataframe = pd.read_csv(csv_file, chunksize=300000, delimiter=',', encoding= 'unicode_escape')
        print(dataframe)
        dataframe[""]
    return render(request, 'dashboard.html', {"form": form})