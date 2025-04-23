from flask import (
    Flask, render_template, request, redirect,
    url_for, jsonify, session, flash
)
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from jsonschema import validate, ValidationError
import database
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {'jpg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extension_autorisee(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app.secret_key = "ma_cle_ultra_secrete_123"
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

inspection_schema = {
    "type": "object",
    "properties": {
        "nom_etablissement": {"type": "string"},
        "adresse": {"type": "string"},
        "ville": {"type": "string"},
        "date_visite": {"type": "string", "format": "date"},
        "nom_prenom_client": {"type": "string"},
        "description_probleme": {"type": "string"}
    },
    "required": [
        "nom_etablissement", "adresse", "ville",
        "date_visite", "nom_prenom_client", "description_probleme"
    ]
}

profil_utilisateur_schema = {
    "type": "object",
    "properties": {
        "nom_complet": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "mot_de_passe": {"type": "string"},
        "etablissements_surveilles": {
            "type": "array",
            "items": {"type": "string"}
        },
    },
    "required": ["nom_complet", "email", "mot_de_passe", "etablissements_surveilles"]
}


# Effectue une mise à jour quotidienne des données depuis la source CSV
def mise_a_jour_quotidienne():
    print(f"[{datetime.now()}] 🔄 Mise à jour des données...")
    database.import_data()


scheduler = BackgroundScheduler()
scheduler.add_job(mise_a_jour_quotidienne, trigger='cron', hour=0, minute=0)
scheduler.start()

import atexit
atexit.register(lambda: scheduler.shutdown())


# Affiche la page d'accueil de l'application
@app.route('/')
def index():
    return render_template("index.html")


# Effectue une recherche d'infractions en fonction du nom, du propriétaire ou de la rue
@app.route('/recherche', methods=['GET'])
def recherche():
    nom = request.args.get("nom")
    proprio = request.args.get("proprietaire")
    rue = request.args.get("rue")
    resultats = database.search_violations(nom, proprio, rue)
    return render_template("resultats.html", violations=resultats)


# Retourne la liste des contraventions entre deux dates spécifiées (au format JSON)
@app.route('/contrevenants', methods=['GET'])
def liste_contraventions():
    du = request.args.get('du')
    au = request.args.get('au')

    if not du or not au:
        return jsonify({"error": "Paramètres 'du' et 'au' requis"}), 400

    try:
        resultats = database.get_contraventions_date(du, au)
        return jsonify(resultats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Affiche la documentation RAML du service REST en HTML
@app.route('/doc')
def documentation():
    with open("static/documentation.raml", "r", encoding="utf-8") as f:
        contenu_raml = f.read()
    return render_template("doc.html", raml=contenu_raml)


# Retourne toutes les infractions associées à un nom d'établissement
@app.route('/infractions')
def infractions_par_nom():
    nom = request.args.get('nom')
    if not nom:
        return jsonify({"error": "Nom requis"}), 400
    try:
        resultats = database.get_infractions_by_nom(nom)
        return jsonify(resultats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Enregistre une nouvelle demande d'inspection après validation du schéma JSON
@app.route('/demande-inspection', methods=['POST'])
def demande_inspection():
    try:
        data = request.get_json()
        validate(instance=data, schema=inspection_schema)
        database.enregistrer_plainte(data)
        print("📬 Demande d'inspection reçue :", data)
        return jsonify({"message": "Demande d'inspection enregistrée."}), 200
    except ValidationError as e:
        return jsonify({"error": "Validation échouée", "details": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Supprime une plainte existante en fonction de son identifiant
@app.route('/supprime-inspection/<int:id>', methods=['DELETE'])
def supprimer_plainte(id):
    try:
        database.supprimer_plainte(id)
        return jsonify({"message": "Plainte supprimée avec succès."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Retourne toutes les plaintes enregistrées sous forme de JSON
@app.route('/api/plaintes')
def api_plaintes():
    try:
        plaintes = database.get_all_plaintes()
        return jsonify(plaintes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Modifie le nom d'un contrevenant dans la base de données
@app.route('/api/contrevenant/<nom>', methods=['PUT'])
def modifier_contrevenant(nom):
    try:
        data = request.get_json()
        nouveau_nom = data.get("nouveau_nom")
        if not nouveau_nom:
            return jsonify({"error": "Nouveau nom manquant"}), 400

        success, message = database.modifier_nom(nom, nouveau_nom)
        if success:
            return jsonify({"message": "Contrevenant modifié avec succès"})
        else:
            return jsonify({"error": message}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Supprime un contrevenant et ses contraventions associées
@app.route('/api/contrevenant/<nom>', methods=['DELETE'])
def supprimer_contrevenant(nom):
    try:
        database.delete_contrevenant(nom)
        return jsonify({"message": "Contrevenant et contraventions supprimés"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Gère la connexion d'un administrateur via un formulaire (GET/POST)
@app.route('/connexion', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        utilisateur = database.authentifier_utilisateur(username, password)
        if utilisateur:
            session.clear()
            session['user_id'] = utilisateur['id']
            session['prenom'] = utilisateur['prenom']
            session['username'] = utilisateur['username']
            session['role'] = utilisateur['role']
            flash("Connexion réussie", "success")
            return redirect(url_for('index'))
        else:
            flash("Courriel ou mot de passe incorrect", "danger")
    return render_template("connexion.html")


# Gère l'inscription d'un administrateur avec hachage du mot de passe
@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        username = request.form['username']
        email = request.form['email']
        mot_de_passe = request.form['password']
        role = request.form['role']
        success, message = database.creer_utilisateur(
            prenom, nom, username, email, mot_de_passe, role
        )
        if success:
            flash(message, "success")
            return redirect(url_for('connexion'))
        else:
            flash(message, "danger")
    return render_template("inscription.html")


# Crée un profil utilisateur (utilisateur normal) via une API REST avec validation JSON Schema
@app.route('/api/creer-profil', methods=['POST'])
def creer_profil():
    from jsonschema import validate, ValidationError
    try:
        data = request.get_json()
        validate(instance=data, schema=profil_utilisateur_schema)
        success, resultat = database.ajouter_profil_utilisateur(data)
        if success:
            session['profil_id'] = resultat
            session['nom_complet'] = data['nom_complet']
            session['email'] = data['email']
            session['etablissements_surveilles'] = data['etablissements_surveilles']
            return jsonify({"message": "Profil utilisateur créé avec succès."}), 201
        else:
            return jsonify({"error": resultat}), 400
    except ValidationError as e:
        return jsonify({"error": "Validation échouée", "details": e.message}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Gère la connexion d'un utilisateur normal à partir du formulaire
@app.route('/connexion_utilisateur', methods=['POST'])
def connexion_utilisateur():
    email = request.form['email']
    mot_de_passe = request.form['password']
    utilisateur = database.authentifier_profil_utilisateur(email, mot_de_passe)
    if utilisateur:
        session.clear()
        session['profil_id'] = utilisateur['id']
        session['nom_complet'] = utilisateur['nom_complet']
        flash("Connexion réussie", "success")
        return redirect(url_for('profil_utilisateur'))
    else:
        flash("Courriel ou mot de passe incorrect", "danger")
        return redirect(url_for('connexion'))


# Déconnecte un utilisateur (admin ou normal) en vidant la session
@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie", "success")
    return redirect(url_for('index'))


# Affiche la page de création de profil utilisateur avec les établissements disponibles
@app.route('/creer-profil', methods=['GET'])
def creer_profil_page():
    etablissements = database.get_noms_etablissements_uniques()
    return render_template("creer_profil.html", etablissements=etablissements)


# Affiche la page de profil utilisateur avec les établissements surveillés et la photo de profil
@app.route('/profil-utilisateur')
def profil_utilisateur():
    if 'profil_id' not in session:
        flash("Vous devez être connecté.", "danger")
        return redirect(url_for('connexion_utilisateur'))
    surveilles = database.get_etablissements_surveilles(session['profil_id'])
    disponibles = database.get_etablissements_disponibles(session['profil_id'])
    photo = database.get_photo_profil(session['profil_id'])
    session['photo'] = photo
    return render_template(
        "profil_utilisateur.html",
        etablissements_surveilles=surveilles,
        etablissements_disponibles=disponibles
    )


# Supprime un établissement surveillé pour le profil utilisateur courant
@app.route('/supprimer_etablissement', methods=['POST'])
def supprimer_etablissement():
    if 'profil_id' not in session:
        flash("Veuillez vous connecter.", "danger")
        return redirect(url_for('connexion'))
    etab = request.form.get('etablissement')
    try:
        database.supprimer_etablissement_surveille(session['profil_id'], etab)
        flash("Établissement supprimé.", "success")
    except Exception as e:
        flash(f"Erreur lors de la suppression : {str(e)}", "danger")
    return redirect(url_for('profil_utilisateur'))


# Ajoute un ou plusieurs établissements surveillés pour le profil utilisateur courant
@app.route('/ajouter_etablissements', methods=['POST'])
def ajouter_etablissements():
    if 'profil_id' not in session:
        flash("Veuillez vous connecter.", "danger")
        return redirect(url_for('connexion'))
    profil_id = session['profil_id']
    etablissements = request.form.getlist('etablissements')
    try:
        for nom in etablissements:
            database.ajouter_etablissement_surveille(profil_id, nom)
        flash("Établissements ajoutés avec succès.", "success")
    except Exception as e:
        flash(f"Erreur lors de l'ajout : {str(e)}", "danger")
    return redirect(url_for('profil_utilisateur'))


# Gère le téléversement de la photo de profil de l'utilisateur (jpg ou png)
@app.route('/televerser_photo', methods=['POST'])
def televerser_photo():
    if 'profil_id' not in session:
        flash("Vous devez être connecté pour téléverser une photo.", "danger")
        return redirect(url_for('connexion'))
    fichier = request.files.get('photo')
    if not fichier or fichier.filename == '':
        flash("Aucun fichier sélectionné.", "warning")
        return redirect(url_for('profil_utilisateur'))
    if not extension_autorisee(fichier.filename):
        flash("Format non supporté. Seuls JPG et PNG sont acceptés.", "danger")
        return redirect(url_for('profil_utilisateur'))
    filename = secure_filename(f"{session['profil_id']}_{fichier.filename}")
    chemin = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    fichier.save(chemin)
    database.ajouter_photo_profil(session['profil_id'], filename)
    session['photo'] = filename
    flash("Photo téléversée avec succès.", "success")
    return redirect(url_for('profil_utilisateur'))


# Affiche le formulaire de dépôt de plainte (vue utilisateur)
@app.route('/plainte')
def page_plainte():
    return render_template('plainte.html')


# Affiche toutes les plaintes enregistrées (vue admin)
@app.route('/plaintes')
def afficher_plaintes():
    plaintes = database.get_all_plaintes()
    return render_template("plaintes.html", plaintes=plaintes)


if __name__ == '__main__':
    app.run(debug=True)