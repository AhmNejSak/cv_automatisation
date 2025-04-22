from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv()
project_path = os.getenv('PROJECT_PATH')

def clean_excel_file():
    # output_file = '/home/ahsak/Bureau/IA_projet/output/resultats.xlsx' ## modif'
    output_file = f'{project_path}/output/resultats.xlsx' ## modif'

    # Lire le fichier Excel existant
    df = pd.read_excel(output_file)

    # Trier par Nom et Entreprise pour regrouper les entrées similaires
    df = df.sort_values(by=['Nom']) # gérer les doublons voir comment faire pour ne perdre que très peu d'informations

    # Supprimer les doublons exacts
    df_cleaned = df.drop_duplicates()

    # Sauvegarder le fichier nettoyé en gardant l'organisation cohérente
    df_cleaned.to_excel(output_file, index=False)

    print(f"Fichier Excel nettoyé et mis à jour : {output_file}")

if __name__ == "__main__":
    clean_excel_file()
