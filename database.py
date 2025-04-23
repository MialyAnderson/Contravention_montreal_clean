import sqlite3
import csv
import requests
from io import StringIO
import hashlib
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db", "violations_mtl.db")
CSV_URL = ("https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/"
           "resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv")


# Importe les données depuis le fichier CSV vers la base de données
# en évitant les doublons et en respectant les suppressions
def import_data():
    if not os.path.exists(DB_PATH):
        return
    response = requests.get(CSV_URL)
    content = response.content.decode('utf-8')
    csv_data = csv.DictReader(StringIO(content))
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count = 0
    for row in csv_data:
        id_poursuite = row.get("id_poursuite")
        cursor.execute(
            "SELECT 1 FROM violations_supprimees WHERE id_poursuite = ?",
            (id_poursuite,)
        )
        if cursor.fetchone():
            continue
        cursor.execute(
            "SELECT 1 FROM violations WHERE id_poursuite = ?",
            (id_poursuite,)
        )
        if cursor.fetchone():
            continue
        try:
            cursor.execute("""
                INSERT INTO violations (
                    id_poursuite,
                    business_id,
                    date,
                    description,
                    adresse,
                    date_jugement,
                    etablissement,
                    montant,
                    proprietaire,
                    ville,
                    statut,
                    date_statut,
                    categorie
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_poursuite,
                row.get("business_id"),
                row.get("date"),
                row.get("description"),
                row.get("adresse"),
                row.get("date_jugement"),
                row.get("etablissement"),
                float(row.get("montant") or 0),
                row.get("proprietaire"),
                row.get("ville"),
                row.get("statut"),
                row.get("date_statut"),
                row.get("categorie")
            ))
            count += 1
        except Exception as e:
            print("Ligne fautive :", row)

    conn.commit()
    conn.close()
    print(f"Importation terminée. {count} nouvelles lignes insérées.")


# Retourne toutes les violations enregistrées dans la base de données
def get_all_violations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM violations")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Recherche des violations selon nom, propriétaire et rue
def search_violations(nom=None, proprietaire=None, rue=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = "SELECT * FROM violations WHERE 1=1"
    params = []
    if nom:
        query += " AND LOWER(etablissement) LIKE ?"
        params.append(f"%{nom.lower()}%")
    if proprietaire:
        query += " AND LOWER(proprietaire) LIKE ?"
        params.append(f"%{proprietaire.lower()}%")
    if rue:
        query += " AND LOWER(adresse) LIKE ?"
        params.append(f"%{rue.lower()}%")
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# Retourne les contraventions entre deux dates
def get_contraventions_date(du, au):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    query = """
        SELECT * FROM violations
        WHERE date >= ? AND date <= ?
    """
    cursor.execute(query, (du, au))
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result


# Retourne toutes les infractions pour un établissement donné
def get_infractions_by_nom(nom_etablissement):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = """
        SELECT * FROM violations
        WHERE etablissement = ?
    """
    cur.execute(query, (nom_etablissement,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Enregistre une plainte dans la base de données
def enregistrer_plainte(data):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO plaintes (
            nom_etablissement, adresse, ville, date_visite,
            nom_prenom_client, description_probleme
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data['nom_etablissement'],
        data['adresse'],
        data['ville'],
        data['date_visite'],
        data['nom_prenom_client'],
        data['description_probleme']
    ))
    conn.commit()
    conn.close()


# Retourne toutes les plaintes enregistrées
def get_all_plaintes():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plaintes ORDER BY date_visite DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# Supprime une plainte selon son identifiant
def supprimer_plainte(plainte_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM plaintes WHERE id = ?", (plainte_id,))
    conn.commit()
    conn.close()


# Modifie le nom d'un établissement dans toutes les violations
def modifier_nom(ancien_nom, nouveau_nom):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "UPDATE violations SET etablissement = ? WHERE etablissement = ?",
            (nouveau_nom, ancien_nom)
        )
        conn.commit()
        conn.close()
        return True, "Nom modifié avec succès"
    except Exception as e:
        return False, str(e)


# Supprime un contrevenant et enregistre son id pour empêcher sa réinsertion
def delete_contrevenant(nom):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id_poursuite FROM violations WHERE etablissement = ?", (nom,))
    ids = c.fetchall()
    for id_row in ids:
        c.execute(
            "INSERT OR IGNORE INTO violations_supprimees (id_poursuite) VALUES (?)",
            (id_row[0],)
        )
    c.execute("DELETE FROM violations WHERE etablissement = ?", (nom,))
    conn.commit()
    conn.close()


# Génère un sel aléatoire pour le hachage des mots de passe
def generer_salt():
    return os.urandom(16).hex()


# Hache un mot de passe avec un sel donné
def hash_mot_de_passe(mot_de_passe, salt):
    return hashlib.sha256((salt + mot_de_passe).encode()).hexdigest()


# Authentifie un administrateur via son username et mot de passe
def authentifier_utilisateur(username, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    utilisateur = cursor.fetchone()
    if utilisateur:
        mot_de_passe_hache = hash_mot_de_passe(password, utilisateur['salt'])
        if mot_de_passe_hache == utilisateur['mot_de_passe']:
            return dict(utilisateur)
    conn.close()
    return None


# Crée un utilisateur admin avec hachage du mot de passe
def creer_utilisateur(prenom, nom, username, email, mot_de_passe, role):
    salt = generer_salt()
    mot_de_passe_hache = hash_mot_de_passe(mot_de_passe, salt)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (prenom, nom, username, email, mot_de_passe, salt, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (prenom, nom, username, email, mot_de_passe_hache, salt, role))
        conn.commit()
        return True, "Inscription réussie"
    except sqlite3.IntegrityError:
        return False, "Email ou nom d'utilisateur déjà utilisé"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# Ajoute un profil utilisateur avec les établissements surveillés associés
def ajouter_profil_utilisateur(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    salt = generer_salt()
    mot_de_passe_hache = hash_mot_de_passe(data['mot_de_passe'], salt)
    try:
        cursor.execute("""
            INSERT INTO profils (nom_complet, email, mot_de_passe, salt)
            VALUES (?, ?, ?, ?)
        """, (
            data['nom_complet'],
            data['email'],
            mot_de_passe_hache,
            salt
        ))
        profil_id = cursor.lastrowid
        for nom in data['etablissements_surveilles']:
            cursor.execute("""
                INSERT INTO surveillances (profil_id, nom_etablissement)
                VALUES (?, ?)
            """, (profil_id, nom))
        conn.commit()
        return True, profil_id
    except sqlite3.IntegrityError:
        return False, "Cet email est déjà utilisé."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# Récupère la liste des noms d'établissements uniques depuis la table violations
def get_noms_etablissements_uniques():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT etablissement FROM violations ORDER BY etablissement ASC"
    )
    etablissements = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return etablissements


# Vérifie les identifiants d'un utilisateur à partir de l'email et du mot de passe
def authentifier_profil_utilisateur(email, password):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM profils WHERE email = ?", (email,))
    profil = cur.fetchone()
    if profil:
        mot_de_passe_hache = hash_mot_de_passe(password, profil['salt'])
        if mot_de_passe_hache == profil['mot_de_passe']:
            return dict(profil)
    conn.close()
    return None


# Récupère la liste des établissements surveillés par un utilisateur donné
def get_etablissements_surveilles(profil_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nom_etablissement FROM surveillances
        WHERE profil_id = ?
    """, (profil_id,))
    rows = cursor.fetchall()
    conn.close()
    return [row["nom_etablissement"] for row in rows]


# Récupère les établissements disponibles à surveiller pour un utilisateur
def get_etablissements_disponibles(profil_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT etablissement FROM violations")
    tous = {row[0] for row in cur.fetchall()}
    cur.execute(
        "SELECT nom_etablissement FROM surveillances WHERE profil_id = ?",
        (profil_id,)
    )
    surveilles = {row[0] for row in cur.fetchall()}
    disponibles = list(tous - surveilles)
    conn.close()
    return sorted(disponibles)


# Supprime un établissement de la liste surveillée par un utilisateur
def supprimer_etablissement_surveille(profil_id, nom_etablissement):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM surveillances
        WHERE profil_id = ? AND nom_etablissement = ?
    """, (profil_id, nom_etablissement))
    conn.commit()
    conn.close()


# Ajoute un établissement à la liste des établissements surveillés par un utilisateur
def ajouter_etablissement_surveille(profil_id, nom_etablissement):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO surveillances (profil_id, nom_etablissement)
        VALUES (?, ?)
    """, (profil_id, nom_etablissement))
    conn.commit()
    conn.close()


# Enregistre le nom du fichier de la photo de profil d'un utilisateur
def ajouter_photo_profil(profil_id, nom_fichier):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE profils SET photo = ? WHERE id = ?", (nom_fichier, profil_id))
    conn.commit()
    conn.close()


# Récupère le nom du fichier de la photo de profil d'un utilisateur
def get_photo_profil(profil_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT photo FROM profils WHERE id = ?", (profil_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else None