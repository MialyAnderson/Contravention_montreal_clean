#!/bin/bash

echo "📦 Installation des dépendances Python..."
pip install -r requirements.txt

echo "📥 Téléchargement de la base de données..."
mkdir -p db
curl -L -o db/violations_mtl.db "https://drive.google.com/uc?export=download&id=1-yxUYao-6xF_p40qrvKnUxZiO_5Lvxnl"

echo "✅ Build terminé avec succès."


