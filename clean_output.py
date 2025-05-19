from dotenv import load_dotenv
import os
import pandas as pd
from auth_utils import get_drive_service, download_file, upload_file_to_drive, get_file_id_by_name

load_dotenv()

def clean_excel_file(service):
    """
    Nettoie le fichier Excel 'resultats.xlsx' en supprimant les doublons
    basés sur la colonne 'Nom', puis met à jour le fichier sur Google Drive.
    """

    output_folder_id = os.getenv("OUTPUT_FOLDER_ID")
    excel_file_name = "resultats.xlsx"

    excel_file_id = get_file_id_by_name(service, excel_file_name, output_folder_id)

    if not excel_file_id:
        print(f"❌ Le fichier '{excel_file_name}' n’a pas été trouvé dans le dossier de sortie.")
        return

    print("📥 Téléchargement du fichier Excel en cours...")

    file_path = download_file(service, excel_file_id)

    if not os.path.exists(file_path):
        print(f"❌ Échec du téléchargement du fichier {excel_file_name}.")
        return

    try:
        df = pd.read_excel(file_path)

        df_cleaned = df.drop_duplicates()
        df_cleaned = df.drop('Date Ingestion')

        cleaned_path = "/tmp/resultats_cleaned.xlsx"
        df_cleaned.to_excel(cleaned_path, index=False)
        print("🧼 Fichier Excel nettoyé localement.")

        
        upload_file_to_drive(service, cleaned_path, excel_file_id)
        print(f"📤 Fichier Excel mis à jour sur Google Drive (ID: {excel_file_id})")

    except Exception as e:
        print(f"❌ Erreur lors du nettoyage du fichier Excel : {e}")

if __name__ == "__main__":
    service = get_drive_service()  
    clean_excel_file(service)      