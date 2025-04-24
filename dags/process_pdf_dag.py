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

# file_sensor_task = FileSensor(
#     task_id='detect_new_pdf',
#     filepath= f'{project_path}/data/*.pdf',  
#     poke_interval=30,  
#     timeout=300,  
#     mode='poke',  
#     dag=dag
# )

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

# file_sensor_task >> process_task >> move_files_task >> clean_output_task



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




######## solution qwen ai #########


import os
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
# Ajoute le chemin racine à PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv


load_dotenv()

# Configuration du DAG
default_args = {
    'owner': 'Ahmed',
    'depends_on_past': False,
    'start_date': datetime(2025, 3, 3),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'pdf_processing_dag',
    default_args=default_args,
    description='Traitement automatique des nouveaux PDF et nettoyage du fichier de sortie',
    schedule_interval=timedelta(minutes=5),  
)

# Tâche 1 : Processus principal
def run_process_pdf():
    token_path = Variable.get("GOOGLE_DRIVE_TOKEN_PATH")
    input_folder_id = os.getenv('INPUT_FOLDER_ID')
    output_folder_id = os.getenv('OUTPUT_FOLDER_ID')
    archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')

    # Importez votre script principal ici
    from process_pdf import process_pdf_files
    process_pdf_files(token_path, input_folder_id, output_folder_id, archive_folder_id)

process_task = PythonOperator(
    task_id='process_new_pdf',
    python_callable=run_process_pdf,
    dag=dag
)

# Tâche 2 : Déplacer les fichiers traités
def run_move_processed_files():
    token_path = Variable.get("GOOGLE_DRIVE_TOKEN_PATH")
    input_folder_id = os.getenv('INPUT_FOLDER_ID')
    archive_folder_id = os.getenv('ARCHIVE_FOLDER_ID')

    # Importez votre script de déplacement ici
    from move_processed_files import move_files_to_archive
    move_files_to_archive(token_path, input_folder_id, archive_folder_id)

move_files_task = PythonOperator(
    task_id='move_processed_files',
    python_callable=run_move_processed_files,
    dag=dag
)

# Tâche 3 : Nettoyer le fichier Excel
def run_clean_excel_output():
    token_path = Variable.get("GOOGLE_DRIVE_TOKEN_PATH")
    output_folder_id = os.getenv('OUTPUT_FOLDER_ID')

    # Importez votre script de nettoyage ici
    from clean_output import clean_excel_on_drive
    clean_excel_on_drive(token_path, output_folder_id)

clean_output_task = PythonOperator(
    task_id='clean_excel_output',
    python_callable=run_clean_excel_output,
    dag=dag
)

# Dépendances entre les tâches
process_task >> move_files_task >> clean_output_task