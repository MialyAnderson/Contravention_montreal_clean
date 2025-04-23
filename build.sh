#!/bin/bash

echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt

echo "📁 Création du dossier db s'il n'existe pas..."
mkdir -p db

echo "📥 Téléchargement de la base de données via gdown..."
gdown --id 1-yxUYao-6xF_p40qrvKnUxZiO_5Lvxnl -O db/violations_mtl.db

echo "📂 Contenu du dossier db :"
ls -lh db

echo "✅ Build terminé avec succès."


