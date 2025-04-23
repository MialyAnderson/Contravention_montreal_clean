# Recréation du fichier après réinitialisation de l'état
contenu = """
# Fichier de correction

**Nom** : Rakotondradano Mialy Anderson  
**Code permanent** : RAKM80300506  

## Tâches effectuées

- A1
- A2
- A3
- A4
- A5
- A6
- D1
- D2
- D3
- D4
- E1
- E2
- F1

## Connexion administrateur

- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `1234`

## Lien de déploiement

🔗 [https://contravention-montreal.onrender.com]

Le site qui est déployé n'est pas la version finale car il y a un fichier qui dépassé la limite de taille.
"""

# Sauvegarde du fichier correction.md
fichier = Path("/mnt/data/correction.md")
fichier.write_text(contenu.strip(), encoding="utf-8")
fichier.name
