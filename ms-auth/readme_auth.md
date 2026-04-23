# Commande Docker :
- lancer l'appliaction
> docker compose up --build

- arrêter l'application
> docker compose down

- stopper l'application
> docker compose start

- starter l'application
> docker compose stop

- lancer le test de dockerfile.test
> docker compose run --rm test

# commande Dockerfile.test (il faut être au niveau du dossier ms-auth):
- depuis le dossier ms-auth :
> docker build -f Dockerfile.test -t ms-auth-test .


- puis exécuter le conteneur :
> docker run --rm ms-auth-test

- combinaison des deux commandes :
> docker build -f Dockerfile.test -t ms-auth-test . && docker run --rm ms-auth-test
---------------------------------
Dockerfile pointe vers authentification.main:app et copie le bon pyproject.toml.


# Compte de test 
1- USER
    email: user@urbanhub.tn
    password: Password1!

2- CELLULE_DECISIONNEL
    email: cellule@urbanhub.tn
    password: Password2!

3- OPERATEUR
    email: operateur@urbanhub.tn
    password: Password3!


# port de l'application : 8001

# structure de l'application :
- domains/ : validation métier login + enum UserRole
- dtos/ : LoginDTO ((email, password) et TokenDTO)
- repositories/: SQLAlchemy (engine/session/Base + modèles + repos)
- controllers/: route POST /auth/login
- security/: bcrypt + JWT (inspiré de ton ancien projet) (Couche `security`: JWT et hachage des mots de passe.)
- config.py: settings par variables d’environnement

# données de test :
ms-auth/authentification/database/db_auth.sql 
contient la table users + 3 utilisateurs (1 par rôle) avec mots de passe hachés bcrypt, et est monté automatiquement par Postgres via docker-compose.yml.

# Endpoint Swagger
POST /auth/login

Body:
    email
    password

>> Réponse: { "access_token": "...", "token_type": "bearer" }
Swagger: http://localhost:8001/docs (pour voir l'interface API)
