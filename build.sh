#!/bin/bash

echo "📥 Téléchargement de violations_mtl.db depuis Google Drive..."
mkdir -p db
curl -L -o db/violations_mtl.db "https://drive.google.com/uc?export=download&id=1-yxUYao-6xF_p40qrvKnUxZiO_5Lvxnl"
echo "✅ Base de données téléchargée avec succès."

