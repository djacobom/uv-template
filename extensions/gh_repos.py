import json
import urllib.request
from jinja2.ext import Extension

class GitHubRepoExtension(Extension):
    def __init__(self, environment):
        super().__init__(environment)
        # Fetch repos (e.g., from your Org)
        # Use a token if your repos are private
        url = "https://api.github.com/orgs/YOUR_ORG/repos?per_page=100"
        
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                # Extract repo names
                repo_names = [repo['name'] for repo in data]
                # Inject the list into the Jinja context
                environment.globals.update(github_repos=repo_names)
        except Exception:
            # Fallback if offline or API fails
            environment.globals.update(github_repos=["fallback-repo-1", "fallback-repo-2"])