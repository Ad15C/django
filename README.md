# Présentation du projet

Ce projet est une application web développée avec Python et Django permettant de gérer une médiathèque.
L’objectif est de moderniser le système de gestion interne de la médiathèque « Notre livre, notre média », qui utilisait auparavant un système papier.

L’application permet :

- la gestion des membres

- la gestion des médias

- la gestion des emprunts

- la consultation publique des médias disponibles

Le projet est réalisé dans le cadre d’un devoir académique visant à mettre en pratique le développement d’une application web avec Django, l’architecture orientée objet, et les tests automatisés.

# Attentes pédagogiques

Grâce à ce projet, les compétences suivantes sont mises en œuvre :

- Développer dans un langage orienté objet

- Développer une application web dynamique

- Utiliser des composants serveur Django

- Accéder et manipuler une base de données

- Appliquer les principes de programmation orientée objet

- Implémenter une stratégie de tests automatisés

- Structurer un projet avec Git et GitHub

# Fonctionnalités

## Application Bibliothécaire (Staff)

Accessible uniquement aux bibliothécaires.

Fonctionnalités :

- créer un membre
- afficher la liste des membres
- modifier un membre
- afficher la liste des médias
- ajouter un média
- créer un emprunt
- enregistrer le retour d’un emprunt

## Application Membre (Client)

Accessible aux utilisateurs inscrits.

Fonctionnalités :
- consulter la liste des médias disponibles
- voir ses emprunts en cours

# Types de médias gérés

L'application gère plusieurs types de médias :

📚 Livres

💿 CD

📀 DVD

🎲 Jeux de société

⚠️ Les jeux de société ne peuvent pas être empruntés.

# Contraintes métier

Les règles métier appliquées dans l'application :

- un membre ne peut pas avoir plus de 3 emprunts actifs
- la durée maximale d’un emprunt est 7 jours
- un membre ayant un retard ne peut plus emprunter
- les jeux de société ne peuvent pas être empruntés

# Tests

Le projet inclut des tests automatisés avec pytest.

Chaque fonctionnalité principale possède au moins un test :
- accès au dashboard client
- affichage des médias
- création des médias
- gestion des emprunts
- restrictions d’accès selon le rôle
- vérification du type de média

## Exécution des tests :
* installation de pytest-django : 
```pip install pytest pytest-django```

* installation BeautifulSoup
```pip install beautifulsoup4```

* lancement des tests
```pytest```

## Informations des rôles test
*Admin* 
- email: admin@exemple.com
- id: admin
- mot de passe: Azerty.123

*staff*
- email: staff@email.com
- id: staff
- mot de passe: Azerty.123!

*client*
- email: client@exemple.com
- id: client
- mot de passe: Azerty!123

# Technologies utilisées

## Technologies principales :

Python 3

Django 5.2

SQLite

Pytest

## Dépendances principales :

Django==5.2.1
pytest==8.3.5
asgiref==3.8.1
beautifulsoup4==4.13.4
sqlparse==0.5.3
tzdata==2025.2

# Base de données

L’application utilise :

SQLite

La base contient des données de test permettant :
- de tester les emprunts
- de tester les rôles utilisateurs
- de tester les médias

# Structure du projet

Structure simplifiée du projet :

mediatheque/
│
├── authentification/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── decorators.py
│
├── client/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── staff/
│   ├── models.py
│   ├── views/
│   └── urls.py
│
├── templates/
│
├── manage.py
└── settings.py

Le projet est divisé en trois applications Django principales :

authentification → gestion des utilisateurs

staff → gestion interne de la médiathèque

client → interface pour les emprunteurs

# Identité graphique

L’interface graphique est volontairement simple et minimale.

Elle repose principalement sur :
- HTML
- templates Django
- structure de pages basiques

Le design CSS sera amélioré ultérieurement par un designer web.

# Installation et lancement du projet
1️⃣ Cloner le projet
git clone https://github.com/USERNAME/mediatheque.git
cd mediatheque
2️⃣ Créer un environnement virtuel
python -m venv venv

## Activation :
### Windows

venv\Scripts\activate

### Linux / Mac

source venv/bin/activate

3️⃣ Installer les dépendances
pip install -r requirements.txt

4️⃣ Appliquer les migrations
python manage.py migrate

5️⃣ Créer un administrateur
python manage.py createsuperuser

6️⃣ Lancer le serveur
python manage.py runserver

## Accès à l’application :

http://127.0.0.1:8000

## Administration Django :

http://127.0.0.1:8000/admin

# Livrable attendu

Le livrable comprend :
- un repository GitHub
- le code source complet
- une base de données avec données test
- un rapport expliquant :
    - l’analyse du code existant
    - les corrections apportées
    - l’implémentation des fonctionnalités
    - la stratégie de tests
    - les instructions d’installation

# Contact

Pour toute question concernant le projet : ad15canon@gmail.com