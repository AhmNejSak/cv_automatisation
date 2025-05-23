import os
from dotenv import load_dotenv

ENV_FILE = ".env.lyon"  

print(f"🔄 Chargement du fichier {ENV_FILE}")
load_dotenv(dotenv_path=ENV_FILE)

print("🔍 Variables d'environnement chargées :")
print("INPUT_DIR  =", os.getenv("INPUT_FOLDER_ID"))
print("OUTPUT_DIR =", os.getenv("OUTPUT_FOLDER_ID"))
print("ARCHIVE_DIR =", os.getenv("ARCHIVE_FOLDER_ID"))


# Test d'écriture dans OUTPUT_DIR
output_dir = os.getenv("OUTPUT_FODLER_ID")
if output_dir:
    try:
        test_path = os.path.join(output_dir, "test_output.txt")
        with open(test_path, "w") as f:
            f.write("✅ Test d'écriture réussi depuis test_env.py")
        print(f"✍️ Écriture réussie dans : {test_path}")
    except Exception as e:
        print(f"❌ Erreur d'écriture dans OUTPUT_DIR : {e}")
else:
    print("❌ OUTPUT_FOLDER_ID non défini.")
