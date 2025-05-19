from auth_utils import get_drive_service
import os

def get_pdf_ids_in_folder(service, folder_id):
    """
    Récupère les IDs des fichiers PDF dans un dossier Google Drive.
    """
    query = f"'{folder_id}' in parents and mimeType = 'application/pdf'"
    results = service.files().list(q=query, fields="files(id)").execute()
    return [file['id'] for file in results.get('files', [])]

def move_processed_files_to_archive(service, input_folder_id, archive_folder_id):
    """
    Déplace les fichiers PDF traités du dossier input vers le dossier archive.
    """
    file_ids = get_pdf_ids_in_folder(service, input_folder_id)

    if not file_ids:
        print("ℹ️ Aucun fichier PDF trouvé dans le dossier input.")
        return 0

    print(f"🚚 Déplacement de {len(file_ids)} fichiers PDF vers le dossier archive...")

    for file_id in file_ids:
        try:
            service.files().update(
                fileId=file_id,
                addParents=archive_folder_id,
                removeParents=input_folder_id,
                fields='id, parents'
            ).execute()
        except Exception as e:
            print(f"❌ Échec du déplacement du fichier {file_id} : {e}")

    print(f"✅ {len(file_ids)} fichiers déplacés.")
    return len(file_ids)

if __name__ == "__main__":
    # Récupère le service Google Drive
    service = get_drive_service()

    # Récupère les IDs des dossiers depuis .env
    input_folder_id = os.getenv("INPUT_FOLDER_ID")
    archive_folder_id = os.getenv("ARCHIVE_FOLDER_ID")

    if not input_folder_id or not archive_folder_id:
        print("❌ Les IDs des dossiers ne sont pas définis dans .env")
        exit(1)

    # Déplace les fichiers traités
    moved_count = move_processed_files_to_archive(service, input_folder_id, archive_folder_id)
    print(f"✅ {moved_count} fichiers déplacés vers l'archive.")