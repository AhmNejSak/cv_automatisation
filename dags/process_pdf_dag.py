import os
from dotenv import load_dotenv
import sys
from airflow.models import Variable

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta


load_dotenv()
project_path = os.getenv('PROJECT_PATH')

# Configuration du DAG
default_args = {
    'owner': 'Ahmed',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 3),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'pdf_processing_dag',
    default_args=default_args,
    description='Traitement automatique des nouveaux PDF et nettoyage du fichier de sortie',
    schedule_interval=timedelta(minutes=5),  
)

file_sensor_task = FileSensor(
    task_id='detect_new_pdf',
    filepath= f'{project_path}/data/*.pdf',  
    poke_interval=30,  
    timeout=300,  
    mode='poke',  
    dag=dag
)

process_task = BashOperator(
    task_id='process_new_pdf',
    bash_command=f'bash {project_path}/wrapper_script.sh ', 
    env = {'MISTRAL_API_KEY': Variable.get("MISTRAL_API_KEY")},
    dag=dag
)

move_files_task = PythonOperator(
    task_id = 'move_processed_files',
    python_callable=lambda: os.system(f'python3 {project_path}/move_processed_files.py'), 
    dag=dag
)

clean_output_task = BashOperator(
    task_id='clean_excel_output',
    bash_command=f'python3 {project_path}/clean_output.py',
    dag=dag
)

file_sensor_task >> process_task >> move_files_task >> clean_output_task



########

# import os
# from dotenv import load_dotenv
# import sys
# from airflow.models import Variable

# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# from airflow import DAG
# from airflow.operators.bash import BashOperator
# from airflow.operators.python import PythonOperator
# from airflow.sensors.filesystem import FileSensor
# from datetime import datetime, timedelta

# #
# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')

# # Configuration du DAG
# default_args = {
#     'owner': 'Ahmed',
#     'depends_on_past': False,
#     'start_date': datetime(2025, 3, 3),
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'pdf_processing_dag',
#     default_args=default_args,
#     description='Traitement automatique des nouveaux PDF et nettoyage du fichier de sortie',
#     schedule_interval=timedelta(minutes=5),  
# )

# # file_sensor_task = FileSensor(
# #     task_id='detect_new_pdf',
# #     filepath= f'{project_path}/data/*.pdf',  
# #     poke_interval=30,  
# #     timeout=300,  
# #     mode='poke',  
# #     dag=dag
# # )

# process_task = BashOperator(
#     task_id='process_new_pdf',
#     bash_command=f'bash {project_path}/wrapper_script.sh ', 
#     env = {'MISTRAL_API_KEY': Variable.get("MISTRAL_API_KEY")},
#     dag=dag
# )

# move_files_task = PythonOperator(
#     task_id = 'move_processed_files',
#     python_callable=lambda: os.system(f'python3 {project_path}/move_processed_files.py'), 
#     dag=dag
# )

# clean_output_task = BashOperator(
#     task_id='clean_excel_output',
#     bash_command=f'python3 {project_path}/clean_output.py',
#     dag=dag
# )

# process_task >> move_files_task >> clean_output_task




## qwen v2


# import os
# from dotenv import load_dotenv
# import sys
# from airflow.models import Variable
# from airflow import DAG
# from airflow.operators.bash import BashOperator
# from airflow.operators.python import PythonOperator
# from datetime import datetime, timedelta
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request

# # Charger les variables d'environnement
# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')
# token_path = f"{project_path}/token.pickle"
# credentials_path = f"{project_path}/credentials_oauth.json"

# # Fonction pour générer ou rafraîchir le token
# def generate_or_refresh_token():
#     creds = None
#     if os.path.exists(token_path):
#         with open(token_path, 'rb') as token:
#             creds = pickle.load(token)

#     # Si les credentials sont invalides ou expirés mais ont un refresh token, rafraîchissez-les
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#     elif not creds or not creds.valid:
#         # Générer de nouveaux credentials si nécessaire
#         flow = InstalledAppFlow.from_client_secrets_file(
#             credentials_path,
#             scopes=['https://www.googleapis.com/auth/drive']
#         )
#         creds = flow.run_local_server(port=0)  # Utilisez run_local_server() ici

#         # Sauvegarder les nouveaux credentials dans token.pickle
#         with open(token_path, 'wb') as token:
#             pickle.dump(creds, token)

#     print("Token OAuth généré ou rafraîchi avec succès.")

# # Configuration du DAG
# default_args = {
#     'owner': 'Ahmed',
#     'depends_on_past': False,
#     'start_date': datetime(2025, 3, 3),
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'pdf_processing_dag',
#     default_args=default_args,
#     description='Traitement automatique des nouveaux PDF et nettoyage du fichier de sortie',
#     schedule_interval=timedelta(minutes=5),  
# )

# # Tâche pour générer ou rafraîchir le token OAuth
# generate_token_task = PythonOperator(
#     task_id='generate_or_refresh_token',
#     python_callable=generate_or_refresh_token,
#     dag=dag
# )

# # Tâche principale : Traitement des PDF
# process_task = BashOperator(
#     task_id='process_new_pdf',
#     bash_command=f'bash {project_path}/wrapper_script.sh ', 
#     env={'MISTRAL_API_KEY': Variable.get("MISTRAL_API_KEY")},
#     dag=dag
# )

# # Tâche pour déplacer les fichiers traités
# move_files_task = PythonOperator(
#     task_id='move_processed_files',
#     python_callable=lambda: os.system(f'python3 {project_path}/move_processed_files.py'), 
#     dag=dag
# )

# # Tâche pour nettoyer le fichier Excel
# clean_output_task = BashOperator(
#     task_id='clean_excel_output',
#     bash_command=f'python3 {project_path}/clean_output.py',
#     dag=dag
# )

# # Dépendances entre les tâches
# generate_token_task >> process_task >> move_files_task >> clean_output_task




##########
# ##########

# from airflow import DAG
# from airflow.operators.python import PythonOperator
# from airflow.operators.bash import BashOperator
# from datetime import datetime, timedelta
# import os
# import pickle
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from dotenv import load_dotenv

# load_dotenv()
# project_path = os.getenv('PROJECT_PATH')
# token_path = os.getenv('TOKEN_PATH')# generate_token_task >> process_task >> move_files_task >> clean_output_task
# credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')


# # Fonction pour générer ou rafraîchir le token OAuth
# def generate_or_refresh_token():
#     creds = None
#     if os.path.exists(token_path):
#         with open(token_path, 'rb') as token:
#             creds = pickle.load(token)

#     # Rafraîchir les credentials si nécessaire
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#     elif not creds or not creds.valid:
#         flow = InstalledAppFlow.from_client_secrets_file(
#             credentials_path,
#             scopes=['https://www.googleapis.com/auth/drive']
#         )
#         creds = flow.run_local_server(port=0)  # Utilisez run_local_server()

#         # Sauvegarder les nouveaux credentials dans token.pickle
#         with open(token_path, 'wb') as token:
#             pickle.dump(creds, token)

#     print("Token OAuth généré ou rafraîchi avec succès.")


# # def generate_or_refresh_token():
# #     creds = None
# #     if os.path.exists(token_path):
# #         with open(token_path, 'rb') as token:
# #             creds = pickle.load(token)

# #     if creds and creds.expired and creds.refresh_token:
# #         creds.refresh(Request())
# #         with open(token_path, 'wb') as token:
# #             pickle.dump(creds, token)
# #         print("✅ Token rafraîchi avec succès.")
# #     elif not creds or not creds.valid:
# #         raise Exception("❌ Token manquant ou invalide. Générez-le avec le script `generate_token.py`.")
# #     else:
# #         print("✅ Token déjà valide.")


# # Configuration du DAG
# default_args = {
#     'owner': 'Ahmed',
#     'depends_on_past': False,
#     'start_date': datetime(2025, 3, 3),
#     'email_on_failure': False,
#     'email_on_retry': False,
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }

# dag = DAG(
#     'pdf_processing_dag',
#     default_args=default_args,
#     description='Traitement automatique des nouveaux PDF et nettoyage du fichier de sortie',
#     schedule_interval=timedelta(minutes=5),
# )

# # Tâche pour générer ou rafraîchir le token OAuth
# generate_token_task = PythonOperator(
#     task_id='generate_or_refresh_token',
#     python_callable=generate_or_refresh_token,
#     dag=dag
# )

# # Tâche principale : Traitement des PDF
# process_task = BashOperator(
#     task_id='process_new_pdf',
#     bash_command=f'bash {project_path}/wrapper_script.sh ',
#     env={'MISTRAL_API_KEY': '{{ var.value.MISTRAL_API_KEY }}'},  # Utilisez Airflow Variables pour Mistral API Key
#     dag=dag
# )

# # Tâche pour déplacer les fichiers traités
# move_files_task = BashOperator(
#     task_id='move_processed_files',
#     bash_command=f'python3 {project_path}/move_processed_files.py',
#     dag=dag
# )

# # Tâche pour nettoyer le fichier Excel
# clean_output_task = BashOperator(
#     task_id='clean_excel_output',
#     bash_command=f'python3 {project_path}/clean_output.py',
#     dag=dag
# )

# # Dépendances entre les tâches
# generate_token_task >> process_task >> move_files_task >> clean_output_task