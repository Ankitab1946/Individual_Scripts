import streamlit as st
import pandas as pd
import requests
import base64
import plotly.graph_objects as go

# -----------------------
# Jira Configuration
# -----------------------
JIRA_BASE_URL = "https://your-domain.atlassian.net"
JIRA_USERNAME = "your-username"
JIRA_PASSWORD = "your-password-or-api-token"
STORY_POINT_FIELD = "customfield_10016"  # update if different

# -----------------------
# Authentication
# -----------------------
def get_auth_header():
    auth = f"{JIRA_USERNAME}:{JIRA_PASSWORD}"
    b64_auth = base64.b64encode(auth.encode()).decode()
    return {"Authorization": f"Basic {b64_auth}", "Accept": "application/json"}

def jira_get(url):
    headers = get_auth_header()
    full_url = f"{JIRA_BASE_URL}{url}"
    response = requests.get(full_url, headers=headers, verify=False)  # allow self-signed certs
    response.raise_for_status()
    return response.json()

# -----------------------
# Jira Data Fetching
# -----------------------
def get_all_boards():
    boards = []
    start_at = 0
    while True:
        data = jira_get(f"/rest/agile/1.0/board?startAt={start_at}&maxResults=50")
        boards += data.get("values", [])
        if data["isLast"]:
            break
        start_at += 50
    return boards

def get_sprints(board_id):
    sprints = []
    start_at = 0
    while True:
        data = jira_get(f"/rest/agile/1.0/board/{board_id}/sprint?startAt={start_at}&maxResults=50")
        sprints += data.get("values", [])
        if data.get("isLast", True):
            break
        start_at += 50
    return sprints

def get_issues_in_sprint(sprint_id):
    issues = []
    start_at = 0
    while True:
        data = jira_get(f"/rest/agile/1.0/sprint/{sprint_id}/issue?startAt={start_at}&maxResults=50")
        issues += data.get("issues", [])
        if start_at + 50 >= data.get("total", 0):
            break
        start_at += 50
    return issues

# -----------------------
# Reporting and Charts
# -----------------------
def generate_sprint_report(issue_rows):
    return pd.DataFrame(issue_rows)

def plot_velocity_chart(sprint_reports):
    sprints = [r['sprint_name'] for r in sprint_reports]
    committed = [r['committed'] for r in sprint_reports]
    completed = [r['completed'] for r in sprint_reports]
    rejected = [r['rejected'] for r in sprint_reports]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=sprints, y=committed, name='Committed', marker_color='lightblue',
                         hovertemplate='Sprint: %{x}<br>Committed: %{y}<extra></extra>'))
    fig.add_trace(go.Bar(x=sprints, y=completed, name='Completed', marker_color='green',
                         hovertemplate='Sprint: %{x}<br>Completed: %{y}<extra></extra>'))
    fig.add_trace(go.Bar(x=sprints, y=rejected, name='Rejected', marker_color='red',
                         hovertemplate='Sprint: %{x}<br>Rejected: %{y}<extra></extra>'))

    fig.update_layout(
        title="Velocity Chart with Completed and Rejected",
        barmode='group',
        xaxis_title="Sprint",
        yaxis_title="Story Points",
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def to_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

# -----------------------
# Streamlit UI
# -----------------------
def main():
    st.title("📊 Jira Multi-Project Sprint Report")

    all_boards = get_all_boards()
    project_keys = sorted(list({board['location']['projectKey'] for board in all_boards}))

    selected_projects = st.multiselect("Select Project(s):", project_keys)

    if selected_projects:
        filtered_boards = [b for b in all_boards if b['location']['projectKey'] in selected_projects]
        board_map = {f"{b['location']['projectKey']} - {b['name']}": b['id'] for b in filtered_boards}
        selected_boards = st.multiselect("Select Board(s):", list(board_map.keys()))

        if selected_boards:
            all_sprints = []
            for bname in selected_boards:
                bid = board_map[bname]
                all_sprints += get_sprints(bid)

            sprint_map = {s['name']: s['id'] for s in all_sprints}
            selected_sprints = st.multiselect("Select Sprint(s):", list(sprint_map.keys()))

            if selected_sprints:
                sprint_reports = []
                for sprint_name in selected_sprints:
                    sprint_id = sprint_map[sprint_name]
                    issues = get_issues_in_sprint(sprint_id)

                    committed = completed = rejected = 0
                    issue_rows = []

                    for issue in issues:
                        fields = issue['fields']
                        story_points = fields.get(STORY_POINT_FIELD, 0) or 0
                        status = fields['status']['name'].lower()

                        committed += story_points
                        if status in ['done', 'closed', 'resolved']:
                            completed += story_points
                        elif status in ['cancelled', 'rejected', 'dropped']:
                            rejected += story_points

                        issue_rows.append({
                            'Issue Key': issue['key'],
                            'Summary': fields.get('summary', ''),
                            'Status': fields['status']['name'],
                            'Story Points': story_points,
                            'Sprint': sprint_name
                        })

                    sprint_reports.append({
                        'sprint_name': sprint_name,
                        'committed': committed,
                        'completed': completed,
                        'rejected': rejected,
                        'issues': issue_rows
                    })

                    # Table
                    st.subheader(f"📋 Sprint Report: {sprint_name}")
                    df = generate_sprint_report(issue_rows)
                    st.dataframe(df)
                    st.markdown(to_csv_download_link(df, f"{sprint_name}_report.csv"), unsafe_allow_html=True)

                # Charts
                st.subheader("📈 Velocity Chart")
                plot_velocity_chart(sprint_reports)

                # Say-Do Summary
                st.subheader("📊 Summary Table")
                summary_df = pd.DataFrame([{
                    'Sprint': r['sprint_name'],
                    'Committed': r['committed'],
                    'Completed': r['completed'],
                    'Rejected': r['rejected'],
                    'Say-Do Ratio': round(r['completed'] / r['committed'], 2) if r['committed'] else 0
                } for r in sprint_reports])

                st.dataframe(summary_df)
                st.markdown(to_csv_download_link(summary_df, "Sprint_Summary_Report.csv"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
