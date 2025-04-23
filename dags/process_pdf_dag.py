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

#
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
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'pdf_processing_dag',
    default_args=default_args,
    description='Traitement automatique des nouveaux PDF et nettoyage du fichier de sortie',
    schedule_interval=timedelta(minutes=5),  
)

# file_sensor_task = FileSensor(
#     task_id='detect_new_pdf',
#     filepath= f'{project_path}/data/*.pdf',  
#     poke_interval=30,  
#     timeout=300,  
#     mode='poke',  
#     dag=dag
# )

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

process_task >> move_files_task >> clean_output_task
