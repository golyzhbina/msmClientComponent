import requests
import datetime
from requests.auth import HTTPBasicAuth

class DAGHttpClient:

    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
    
    
    def trigger_dag(self, dag_id, home_dir):
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns"
        headers = {
            "Content-Type": "application/json"
        }
        
        now = datetime.datetime.now()
        execution_date = now - datetime.timedelta(days=1)

        payload = {
            "conf": {"home_dir" : home_dir},
            "logical_date": execution_date.isoformat() + "Z",
            "execution_date": execution_date.isoformat() + "Z",
            "data_interval_start": execution_date.isoformat() + "Z",
            "data_interval_end": now.isoformat() + "Z",
            "dag_run_id": f"{dag_id}_{execution_date.strftime('%Y%m%dT%H%M%S')}"
        }
        
        response = requests.post(url, auth=HTTPBasicAuth(*self.auth), headers=headers, json=payload)
        return response.status_code, response.json()
    
    def get_state_dag(self, dag_id, dag_run_id):
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}"

        response = requests.get(url, auth=HTTPBasicAuth(*self.auth))
        return response.json()
    
    def get_dataset_events(self, dag_id, dag_run_id):
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/upstreamDatasetEvents"

        response = requests.get(url, auth=HTTPBasicAuth(*self.auth))
        return response.json()
    
    def get_dag_stats(self, dag_id):
        url = f"{self.base_url}/api/v1/dagStats"

        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(url, auth=HTTPBasicAuth(*self.auth), headers=headers, params={"dag_ids": [dag_id]})
        return response.json()

    def get_task_instances(self, dag_id, dag_run_id):
        url = f"{self.base_url}/api/v1/dags/{dag_id}/dagRuns/{dag_run_id}/taskInstances"
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.get(url, auth=HTTPBasicAuth(*self.auth), headers=headers)
        return response.json()
