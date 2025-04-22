# import os
# import shutil
# def move_processed_files(src_folder, dest_folder):

#     # créer le dossier de destination s'il n'existe pas
#     if not os.path.exists(dest_folder):
#         os.makedirs(dest_folder)
#         print(f"Dossier créé : {dest_folder}")

#     # deplacement des cv traités dans le dossier data_processed
#     for filename in os.listdir(src_folder):
#         file_path = os.path.join(src_folder,filename)
#         if filename.endwith(".pdf"):
#             shutil.move(file_path, os.path.join(dest_folder,filename))
#         print(f"Fichier {filename} traité et deplacé vers {dest_folder}")

# if __name__ == "__main__":
#     move_processed_files('/home/ahsak/Bureau/IA_projet/data', '/home/ahsak/Bureau/IA_projet/data_processed')



import os
import shutil
from dotenv import load_dotenv

load_dotenv()
project_path = os.getenv('PROJECT_PATH')


def move_processed_file(src_folder, dest_folder):
    """Déplacer les fichiers traités dans un dossier différent."""
    
    # Vérifier si le dossier de destination existe, sinon le créer
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
        print(f"Dossier créé : {dest_folder}")

    # Déplacer les fichiers
    for filename in os.listdir(src_folder):
        file_path = os.path.join(src_folder, filename)
        
        # Vérifier si c'est un fichier et si c'est un fichier PDF
        if os.path.isfile(file_path) and filename.endswith(".pdf"):
            try:
                # Déplacer le fichier vers le dossier de destination
                shutil.move(file_path, os.path.join(dest_folder, filename))
                print(f"Fichier {filename} déplacé vers : {dest_folder}")
            except Exception as e:
                print(f"Erreur lors du déplacement du fichier {filename}: {e}")
        else:
            print(f"Le fichier {filename} n'est pas un PDF ou n'est pas un fichier valide.")

if __name__ == "__main__":
    # Chemins d'exemple (à adapter selon tes besoins)
    # move_processed_files('/home/ahsak/Bureau/IA_projet/data', '/home/ahsak/Bureau/IA_projet/data_processed') ## modif'
    move_processed_file(f'{project_path}/data', f'{project_path}/data_processed') ##modif'
