from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, logout
from django.contrib import messages

# Create your views here.
def login_user(request):
    if request.method == "POST":
        matricule = request.POST['matricule']
        password = request.POST['password']
        user = authenticate(request, username=matricule, password=password)
        if user is not None:
            return redirect('p1')
        else:
            messages.success(request, ("Erreur d'identifiant ou de mot de passe, veuillez ressayer"))
            return redirect('login')
    else:
        return render(request, 'login.html', {})
    
def logout_user(request):
    logout(request)
    messages.success(request, ("Session deconnectée"))
    return redirect('login')

def p1(request):
    return render(request, 'p1.html')