FROM python:3.12.2-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Étape 5 : Positionnement du répertoire de travail dans le conteneur
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Crée le projet seulement s'il n'existe pas déjà en invite de commande
# docker-compose run mapservice django-admin startproject project . 
# RUN test -f manage.py || django-admin startproject app .

# Étape 4 : Copie des fichiers sur windows dans le conteneur
COPY . .

RUN test -f manage.py || django-admin startproject app .

EXPOSE 80


# CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
