import streamlit as st
import pandas as pd
import requests
import base64
import matplotlib.pyplot as plt

# -----------------------
# Jira API Configuration
# -----------------------
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_USERNAME = "your-username-here"
JIRA_TOKEN = "your-jira-token-here"

# Path to your client certificate (.crt file)
CLIENT_CERT_PATH = "jira.crt"
# Optional: If your private key is separate, specify the tuple below:
# CLIENT_CERT_PATH = ("jira.crt", "jira.key")

# Optional: Custom field id for Story Points in your Jira
STORY_POINT_FIELD = "customfield_10016"

# -----------------------
# Jira API Helper Functions
# -----------------------
def get_auth_header():
    return {
        "Authorization": f"Bearer {JIRA_TOKEN}",
        "X-User-Name": JIRA_USERNAME,
        "Accept": "application/json"
    }

def jira_get(url):
    headers = get_auth_header()
    full_url = f"{JIRA_BASE_URL}{url}"
    response = requests.get(full_url, headers=headers, cert=CLIENT_CERT_PATH)
    response.raise_for_status()
    return response.json()

def get_boards(project_key):
    result = jira_get(f"/rest/agile/1.0/board?projectKeyOrId={project_key}")
    return result.get('values', [])

def get_sprints(board_id):
    result = jira_get(f"/rest/agile/1.0/board/{board_id}/sprint")
    return result.get('values', [])

def get_issues_in_sprint(sprint_id):
    result = jira_get(f"/rest/agile/1.0/sprint/{sprint_id}/issue?maxResults=1000")
    return result.get('issues', [])

# Continue with rest of the reporting functions and Streamlit UI as in the earlier full code
