import json
import subprocess
from jinja2.ext import Extension


class GCloudExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        # Internal cache to store fetched artifacts per project data
        self.ar_cache = {}

        def get_projects():
            try:
                result = subprocess.run(
                    ["gcloud", "projects", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return [proj["projectId"] for proj in json.loads(result.stdout)]
            except Exception:
                return ["fallback-project"]

        def get_service_accounts(project_id):
            try:
                # Fetches SAs specifically for the chosen project
                result = subprocess.run(
                    [
                        "gcloud",
                        "iam",
                        "service-accounts",
                        "list",
                        f"--project={project_id}",
                        "--format=json",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return [sa["email"] for sa in json.loads(result.stdout)]
            except Exception:
                return [f"no-sa-found-for-{project_id}"]

        def get_artifact_labels(project_id):
            try:
                print(f"⬇️  Fetching artifact repositories for project: {project_id}")
                # 1. Run gcloud command
                result = subprocess.run(
                    [
                        "gcloud", "artifacts", "repositories", "list",
                        f"--project={project_id}", "--location=all", "--format=json",
                    ],
                    capture_output=True, text=True, check=True,
                )
                repos = json.loads(result.stdout)

                # 2. Clear cache and build the labels list
                self.ar_cache = {}
                if not repos:
                    return ["No repositories found"]
                for repo in repos:
                    parts = repo['name'].split('/')
                    region = parts[3]
                    repo_id = parts[5]
                    
                    label = f"{repo_id} ({region})"
                    # Store the data indexed by the label string
                    self.ar_cache[label] = {
                        "name": repo_id,
                        "region": region
                    }
                    print(f"✅ Found repository: {label}")
                return list(self.ar_cache.keys())
            
            except Exception as e:
                # Return a list with one string so the UI doesn't crash
                return ["No repositories found (Check gcloud auth or Project ID)"]

        def get_cached_artifact_value(label, key):
            """Returns 'name' or 'region' from the cache based on the selected label."""
            artifact = self.ar_cache.get(label, {})
            return artifact.get(key, "")

        # Register the functions for use in copier.yml
        environment.globals.update({
            "get_artifact_labels": get_artifact_labels,
            "get_artifact_value": get_cached_artifact_value,
        })

        environment.globals.update(
            gcloud_projects=get_projects(),
            fetch_sas=get_service_accounts,
            fetch_artifacts=get_artifact_labels,
        )
