from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv
import time
from langchain_mistralai import ChatMistralAI
import pandas as pd

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
project_path = os.getenv('PROJECT_PATH')


def get_pdf_text(pdf_path):
    """Extrait le texte d'un fichier PDF."""
    text = ""
    pdf_reader = PdfReader(pdf_path)
    for page in pdf_reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"
    return text.strip()


def process_pdf_files():
    """Processus principal pour traiter les fichiers PDF et extraire les données."""
    # Initialisation du modèle IA
    llm = ChatMistralAI(model='mistral-large-latest', temperature=0)

    # Définition des chemins
    pdf_folder = f"{project_path}/data"
    output_folder = f"{project_path}/output"
    excel_path = f"{project_path}/output/resultats.xlsx"

    # Création du dossier de sortie si nécessaire
    os.makedirs(output_folder, exist_ok=True)

    # Récupérer les fichiers PDF
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    
    # Liste pour stocker les données extraites
    data = []

    # Parcours des fichiers PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"📄 Traitement du fichier : {pdf_file}")

        # Extraire le texte du PDF
        text = get_pdf_text(pdf_path)

        if not text:
            print(f"⚠️ Aucun texte extrait du fichier {pdf_file}, il pourrait être vide ou mal scanné.")
            continue

        # Construction du message pour l'IA
        message = [
            ("system",
            """Je vais te fournir un texte décrivant le parcours professionnel d'une personne. 
            Ton objectif est d'extraire **de manière fidèle** les informations suivantes, **sans modifier ni interpréter** les données d'origine :

            ### **Informations à extraire :**
            1. **Nom du candidat**  
            2. **Les entreprises dans lesquelles la personne a travaillé** et leur classification :
               - Si c'est une **ESN**, indique-le clairement et liste ses clients.
               - Si c'est une **entreprise classique**, indique-le clairement également.

            3. **Les technologies utilisées** :
               - Associe chaque entreprise (ou client d'ESN) aux stacks techniques mentionnées dans le texte.
               - **Ne jamais inventer ou omettre une technologie** : si ce n’est pas précisé dans le texte, ne l'ajoute pas.

            4. **Si un client ESN est mentionné, précise à quelle ESN il est rattaché.**

            ### **Format de sortie attendu (exemple) :**
            
            ----
            **Nom du Candidat**  
            [Nom du candidat]  

            **Entreprise ESN**  
            [Nom de l'ESN]  

            **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
            - Technologie 1  
            - Technologie 2  

            **Client ESN : [Nom du client]** (ESN : [Nom de l'ESN])  
            - Technologie 3  
            - Technologie 4  

            ---
            **Entreprise classique**  
            [Nom de l'entreprise]  
            - Technologie 1  
            - Technologie 2  
            
            ----
            """
            ),
            ("human", text)
        ]

        try:
            # Appel au modèle IA pour obtenir la réponse
            ai_msg = llm.invoke(message)
            text_brute = ai_msg.content

            # Sauvegarde du texte brut dans un fichier
            output_file = os.path.join(output_folder, f"output_{pdf_file.replace('.pdf', '.txt')}")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text_brute)

            print(f"✅ Résultat sauvegardé dans {output_file}")

            # Traitement du texte brut pour en extraire les données structurées
            lines = text_brute.split("\n")
            nom_candidat = ""
            entreprise = ""
            status = ""
            esn_nom = "-"
            stacks = []

            for i, line in enumerate(lines):
                line = line.strip()
                
                if line.startswith("**Nom du Candidat**"):
                    nom_candidat = lines[i + 1].strip() if i + 1 < len(lines) else ""
                
                elif line.startswith("**Entreprise ESN**"):
                    entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    status = "ESN"
                    esn_nom = "-"
                
                elif line.startswith("**Client ESN :"):
                    parts = line.replace("**Client ESN :", "").replace("**", "").strip().split("(ESN :")
                    entreprise = parts[0].strip()
                    esn_nom = parts[1].replace(")", "").strip() if len(parts) > 1 else "-"
                    status = "Client ESN"
                
                elif line.startswith("**Entreprise classique**"):
                    entreprise = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    status = "Entreprise Classique"
                    esn_nom = "-"
                
                elif line.startswith("- "):  # Ligne contenant une stack technique
                    stacks.append(line.replace("- ", "").strip())

                # Sauvegarde lorsque l'on change d'entreprise
                elif entreprise and status and stacks:
                    data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])
                    stacks = []

            # Sauvegarde de la dernière entreprise rencontrée
            if entreprise and status and stacks:
                data.append([nom_candidat, entreprise, status, esn_nom, ", ".join(stacks)])

        except Exception as e:
            print(f"❌ Erreur lors du traitement de {pdf_file} : {e}")

        # Pause pour éviter de surcharger l'API
        time.sleep(1)

    # Génération du fichier Excel avec les données extraites
    print("📊 Génération du fichier Excel...")

    df = pd.DataFrame(data, columns=["Nom", "Entreprise", "Status", "ESN", "Stacks Techniques"])

    # Sauvegarde en Excel (ajout de nouvelles données si le fichier existe)
    if os.path.exists(excel_path):
        df_existing = pd.read_excel(excel_path)
        df = pd.concat([df_existing, df], ignore_index=True)

    df.to_excel(excel_path, index=False)

    print(f"🎉 Fichier Excel mis à jour : {excel_path}")


if __name__ == "__main__":
    process_pdf_files()
