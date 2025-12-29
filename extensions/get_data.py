import json
import subprocess
from jinja2.ext import Extension

class GCloudExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)

        def get_projects():
            try:
                result = subprocess.run(
                    ["gcloud", "projects", "list", "--format=json"],
                    capture_output=True, text=True, check=True
                )
                return [proj['projectId'] for proj in json.loads(result.stdout)]
            except Exception:
                return ["fallback-project"]

        def get_service_accounts(project_id):
            try:
                # Fetches SAs specifically for the chosen project
                result = subprocess.run(
                    ["gcloud", "iam", "service-accounts", "list", 
                     f"--project={project_id}", "--format=json"],
                    capture_output=True, text=True, check=True
                )
                return [sa['email'] for sa in json.loads(result.stdout)]
            except Exception:
                return [f"no-sa-found-for-{project_id}"]

        # Inject these functions into the Jinja environment
        environment.globals.update(
            gcloud_projects=get_projects(),
            fetch_sas=get_service_accounts
        )