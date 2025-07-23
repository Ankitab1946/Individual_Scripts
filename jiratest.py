import requests

JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_USERNAME = "your-username"
JIRA_TOKEN = "your-api-token"

headers = {
    "Authorization": f"Bearer {JIRA_TOKEN}",
    "Accept": "application/json"
}

response = requests.get(f"{JIRA_BASE_URL}/rest/api/3/myself", headers=headers)

print(response.status_code)
print(response.json())
