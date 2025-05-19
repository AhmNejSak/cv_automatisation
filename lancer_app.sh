#!/bin/bash

# Aller dans le dossier où se trouve ce script
cd "$(dirname "$0")"

# activer l'environnement virtuel
source envVirtuel/bin/activate
# Lancer l'application Streamlit
streamlit run application.py
