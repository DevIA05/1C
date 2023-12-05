# Utilisez une image de base Python 3
FROM python:3.10

# Définissez l'emplacement de travail dans le conteneur
WORKDIR /app

# Copiez les fichiers de l'application dans le conteneur
COPY ./src /app/src
COPY ./img /app/img

# Installez les dépendances
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Exposez le port sur lequel l'application s'exécute
EXPOSE 8000

# Définissez la commande pour exécuter l'application
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
