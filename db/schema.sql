CREATE TABLE violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_poursuite TEXT,
    business_id TEXT,
    date TEXT,
    description TEXT,
    adresse TEXT,
    date_jugement TEXT,
    etablissement TEXT,
    montant REAL,
    proprietaire TEXT,
    ville TEXT,
    statut TEXT,
    date_statut TEXT,
    categorie TEXT
);

CREATE TABLE plaintes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_etablissement TEXT,
    adresse TEXT,
    ville TEXT,
    date_visite TEXT,
    nom_prenom_client TEXT,
    description_probleme TEXT
);

CREATE TABLE violations_supprimees (
    id_poursuite TEXT PRIMARY KEY
);


CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prenom TEXT NOT NULL,
    nom TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profils (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_complet TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    mot_de_passe TEXT NOT NULL,
    salt TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS surveillances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profil_id INTEGER NOT NULL,
    nom_etablissement TEXT NOT NULL,
    FOREIGN KEY (profil_id) REFERENCES profils(id)
);


