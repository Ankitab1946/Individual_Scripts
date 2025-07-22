import streamlit as st
import pandas as pd
import requests
import base64
import matplotlib.pyplot as plt
import io
import json

# -----------------------
# Jira API Configuration
# -----------------------
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token-or-public-key"

# Optional: Custom field id for Story Points in your Jira
STORY_POINT_FIELD = "customfield_10016"


# -----------------------
# Jira API Helper Functions
# -----------------------
def get_auth_header():
    auth_string = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    return {"Authorization": f"Basic {b64_auth}",
            "Accept": "application/json"}


def get_boards(project_key):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board?projectKeyOrId={project_key}"
    response = requests.get(url, headers=get_auth_header())
    return response.json().get('values', [])


def get_sprints(board_id):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint"
    response = requests.get(url, headers=get_auth_header())
    return response.json().get('values', [])


def get_issues_in_sprint(sprint_id):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}/issue?maxResults=1000"
    response = requests.get(url, headers=get_auth_header())
    return response.json().get('issues', [])


# -----------------------
# Reporting Functions
# -----------------------
def generate_sprint_report(sprint_data):
    df = pd.DataFrame(sprint_data)
    return df


def plot_velocity_chart(sprint_reports):
    plt.figure(figsize=(10, 5))
    for report in sprint_reports:
        sprint_name = report['sprint_name']
        committed = report['committed']
        delivered = report['delivered']
        plt.bar(sprint_name, committed, color='lightblue', label='Committed')
        plt.bar(sprint_name, delivered, color='green', label='Delivered')

    plt.ylabel("Story Points")
    plt.xlabel("Sprints")
    plt.title("Velocity Chart")
    plt.legend(["Committed", "Delivered"])
    st.pyplot(plt)


def generate_say_do_chart(sprint_reports):
    sprints = [r['sprint_name'] for r in sprint_reports]
    say_do_ratio = [
        (r['delivered'] / r['committed'] if r['committed'] > 0 else 0)
        for r in sprint_reports
    ]

    plt.figure(figsize=(10, 4))
    plt.plot(sprints, say_do_ratio, marker='o')
    plt.ylabel("Say-Do Ratio")
    plt.xlabel("Sprints")
    plt.title("Say-Do Ratio per Sprint")
    plt.ylim(0, 1.5)
    st.pyplot(plt)


def to_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV Report</a>'
    return href


# -----------------------
# Streamlit UI
# -----------------------
def main():
    st.title("📊 Jira Sprint Reporting Tool")

    project_key = st.text_input("Enter Project Code/Project Name:")

    if project_key:
        boards = get_boards(project_key)
        if not boards:
            st.error("No boards found for this project.")
            return

        board_options = {board['name']: board['id'] for board in boards}
        board_name = st.selectbox("Select Board:", list(board_options.keys()))
        board_id = board_options[board_name]

        sprints = get_sprints(board_id)
        sprint_options = {sprint['name']: sprint['id'] for sprint in sprints}

        selected_sprints = st.multiselect("Select Sprint(s):", list(sprint_options.keys()))

        if selected_sprints:
            sprint_reports = []

            for sprint_name in selected_sprints:
                sprint_id = sprint_options[sprint_name]
                issues = get_issues_in_sprint(sprint_id)

                committed = 0
                delivered = 0
                issue_rows = []

                for issue in issues:
                    story_points = issue['fields'].get(STORY_POINT_FIELD, 0) or 0
                    status = issue['fields']['status']['name']

                    committed += story_points
                    if status.lower() in ['done', 'closed', 'resolved']:
                        delivered += story_points

                    issue_rows.append({
                        'Issue Key': issue['key'],
                        'Summary': issue['fields']['summary'],
                        'Status': status,
                        'Story Points': story_points,
                        'Sprint': sprint_name
                    })

                sprint_reports.append({
                    'sprint_name': sprint_name,
                    'committed': committed,
                    'delivered': delivered,
                    'issues': issue_rows
                })

                st.subheader(f"📋 Sprint Report: {sprint_name}")
                df = generate_sprint_report(issue_rows)
                st.dataframe(df)
                st.markdown(to_csv_download_link(df, f"{sprint_name}_report.csv"), unsafe_allow_html=True)

            # Velocity Chart
            st.subheader("📈 Velocity Chart")
            plot_velocity_chart(sprint_reports)

            # Say-Do Ratio Chart
            st.subheader("📉 Say-Do Ratio")
            generate_say_do_chart(sprint_reports)

            # Summary Table: Committed vs Delivered Story Points
            st.subheader("📊 Summary Report")
            summary_df = pd.DataFrame([
                {
                    'Sprint': r['sprint_name'],
                    'Committed Story Points': r['committed'],
                    'Delivered Story Points': r['delivered'],
                    'Say-Do Ratio': round(r['delivered'] / r['committed'], 2) if r['committed'] else 0
                }
                for r in sprint_reports
            ])

            st.dataframe(summary_df)
            st.markdown(to_csv_download_link(summary_df, "Sprint_Summary_Report.csv"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
