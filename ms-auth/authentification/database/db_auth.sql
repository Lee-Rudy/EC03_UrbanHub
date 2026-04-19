-- bdd type : postgreSQL
-- le rôle de l'authetification est de gérer les distrubutions des jetons des connexions des utilisateurs , pour l'accès aux rôles il y a déjà le microservice User
-- Pour la simulation de test Swagger, on ajoute une table `users` minimale (email + hash + role).

DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('USER', 'CELLULE_DECISIONNEL', 'OPERATEUR');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS users
(
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    name VARCHAR(120) NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE auth_tokens 
(
    id SERIAL PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_id ON auth_tokens (user_id);

CREATE TABLE IF NOT EXISTS logs_authentification
(
    id SERIAL PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    action VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Données de test (emails + mots de passe + rôles)
-- Mot de passe en clair (pour tests Swagger uniquement):
-- - USER: Password1!
-- - CELLULE_DECISIONNEL: Password2!
-- - OPERATEUR: Password3!

INSERT INTO users (email, password_hash, role, name)
VALUES
('user@urbanhub.tn', '$2b$12$qjVLiD9uQURAmcswRQUgVeNGqd39hyPf5y.bmB.KX4oYvd.1uSyO6', 'USER', 'Utilisateur Test'),
('cellule@urbanhub.tn', '$2b$12$Zv3514zPVKPh1f.XAX32du66d/q4PSYcTOqcRO6xzAQDNKT8h.z0G', 'CELLULE_DECISIONNEL', 'Cellule Test'),
('operateur@urbanhub.tn', '$2b$12$L5493PFn/nXxQIZFTDoG/.SIJlmfs6SBA467BDF3n576jkdVxdM.6', 'OPERATEUR', 'Operateur Test')
ON CONFLICT (email) DO NOTHING;