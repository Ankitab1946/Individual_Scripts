import streamlit as st
import pandas as pd
import requests
import base64
import plotly.graph_objects as go

# -----------------------
# Jira Configuration
# -----------------------
JIRA_BASE_URL = "https://your-domain.atlassian.net"  # ✅ Update this
JIRA_USERNAME = "your-username"                      # ✅ Update this
JIRA_PASSWORD = "your-api-token"                     # ✅ Use API token for Jira Cloud

STORY_POINT_FIELD = "customfield_10016"  # ✅ Update if your Jira uses different field

# -----------------------
# Authentication
# -----------------------
def get_auth_header():
    auth_str = f"{JIRA_USERNAME}:{JIRA_PASSWORD}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    return {
        "Authorization": f"Basic {b64_auth}",
        "Accept": "application/json"
    }

def jira_get(url):
    headers = get_auth_header()
    full_url = f"{JIRA_BASE_URL}{url}"
    response = requests.get(full_url, headers=headers)
    response.raise_for_status()
    return response.json()

# -----------------------
# Jira API Functions
# -----------------------
def get_boards(project_key):
    result = jira_get(f"/rest/agile/1.0/board?projectKeyOrId={project_key}")
    return result.get('values', [])

def get_sprints(board_id):
    result = jira_get(f"/rest/agile/1.0/board/{board_id}/sprint")
    return result.get('values', [])

def get_issues_in_sprint(sprint_id):
    result = jira_get(f"/rest/agile/1.0/sprint/{sprint_id}/issue?maxResults=1000")
    return result.get('issues', [])

# -----------------------
# Chart: Committed, Delivered, Say-Do Ratio
# -----------------------
def plot_combined_chart(sprint_reports):
    sprint_names = [r['sprint_name'] for r in sprint_reports]
    committed = [r['committed'] for r in sprint_reports]
    delivered = [r['delivered'] for r in sprint_reports]
    say_do = [round((r['delivered'] / r['committed']), 2) if r['committed'] else 0 for r in sprint_reports]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sprint_names,
        y=committed,
        name='Committed',
        marker_color='steelblue',
        text=committed,
        textposition='outside'
    ))

    fig.add_trace(go.Bar(
        x=sprint_names,
        y=delivered,
        name='Delivered',
        marker_color='orangered',
        text=delivered,
        textposition='outside'
    ))

    fig.add_trace(go.Scatter(
        x=sprint_names,
        y=say_do,
        name='Say-Do Ratio',
        yaxis='y2',
        mode='lines+markers+text',
        line=dict(color='orange', width=3),
        text=say_do,
        textposition='top center'
    ))

    fig.update_layout(
        title="Sprint Statistics",
        xaxis=dict(title='Sprint'),
        yaxis=dict(title='Story Points'),
        yaxis2=dict(
            title='Say-Do Ratio',
            overlaying='y',
            side='right',
            range=[0, 1.2]
        ),
        barmode='group',
        legend=dict(x=0.5, y=1.2, orientation='h'),
        margin=dict(t=60, b=50),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# Utility
# -----------------------
def generate_sprint_report(sprint_data):
    return pd.DataFrame(sprint_data)

def to_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

# -----------------------
# Streamlit UI
# -----------------------
def main():
    st.title("📊 Jira Sprint Report Generator")

    project_key = st.text_input("Enter Jira Project Code:")

    if project_key:
        boards = get_boards(project_key)
        if not boards:
            st.error("No boards found.")
            return

        board_map = {b['name']: b['id'] for b in boards}
        board_name = st.selectbox("Select Board:", list(board_map.keys()))
        board_id = board_map[board_name]

        sprints = get_sprints(board_id)
        sprint_map = {s['name']: s['id'] for s in sprints}
        selected_sprints = st.multiselect("Select Sprint(s):", list(sprint_map.keys()))

        if selected_sprints:
            sprint_reports = []

            for sprint_name in selected_sprints:
                sprint_id = sprint_map[sprint_name]
                issues = get_issues_in_sprint(sprint_id)

                committed = delivered = 0
                issue_rows = []

                for issue in issues:
                    fields = issue['fields']
                    story_points = fields.get(STORY_POINT_FIELD, 0) or 0
                    status = fields['status']['name'].lower()

                    committed += story_points
                    if status in ['done', 'closed', 'resolved', 'rejected']:  # ✅ Rejected treated as Delivered
                        delivered += story_points

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
                    'delivered': delivered,
                    'issues': issue_rows
                })

                # Issue Table
                st.subheader(f"📋 Sprint Report: {sprint_name}")
                df = generate_sprint_report(issue_rows)
                st.dataframe(df)
                st.markdown(to_csv_download_link(df, f"{sprint_name}_report.csv"), unsafe_allow_html=True)

            # Combined Chart
            st.subheader("📈 Sprint Statistics (Committed, Delivered + Say-Do Ratio)")
            plot_combined_chart(sprint_reports)

            # Summary Table
            st.subheader("📊 Say-Do Summary")
            summary_df = pd.DataFrame([{
                'Sprint': r['sprint_name'],
                'Committed': r['committed'],
                'Delivered': r['delivered'],
                'Say-Do Ratio': round(r['delivered'] / r['committed'], 2) if r['committed'] else 0
            } for r in sprint_reports])

            st.dataframe(summary_df)
            st.markdown(to_csv_download_link(summary_df, "Summary_Report.csv"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
