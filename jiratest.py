import streamlit as st
import pandas as pd
import requests
import base64
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# -----------------------
# Jira Configuration
# -----------------------

JIRA_BASE_URL = "https://your-domain.atlassian.net"  # Update this to your Jira base URL
JIRA_USERNAME = "your-username-or-email"             # Update this
JIRA_PASSWORD = "your-password-or-api-token"         # Use API token if you're using Jira Cloud

# Custom field ID for story points (update this if yours is different)
STORY_POINT_FIELD = "customfield_10016"

# -----------------------
# Helper Functions
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
# Reporting Functions
# -----------------------

def generate_sprint_report(sprint_data):
    return pd.DataFrame(sprint_data)

# def plot_velocity_chart(sprint_reports):
#     plt.figure(figsize=(10, 5))
#     sprint_names = [r['sprint_name'] for r in sprint_reports]
#     committed = [r['committed'] for r in sprint_reports]
#     delivered = [r['delivered'] for r in sprint_reports]

#     plt.bar(sprint_names, committed, color='lightblue', label='Committed')
#     plt.bar(sprint_names, delivered, color='green', label='Delivered')
#     plt.ylabel("Story Points")
#     plt.title("Velocity Chart")
#     plt.legend()
#     st.pyplot(plt)

def plot_velocity_chart(sprint_reports):
    sprint_names = [r['sprint_name'] for r in sprint_reports]
    committed = [r['committed'] for r in sprint_reports]
    delivered = [r['delivered'] for r in sprint_reports]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=sprint_names,
        y=committed,
        name='Committed',
        marker_color='lightblue',
        hovertemplate='Sprint: %{x}<br>Committed: %{y}<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=sprint_names,
        y=delivered,
        name='Delivered',
        marker_color='green',
        hovertemplate='Sprint: %{x}<br>Delivered: %{y}<extra></extra>'
    ))

    fig.update_layout(
        title="Velocity Chart",
        xaxis_title="Sprint",
        yaxis_title="Story Points",
        barmode='group',
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)
    
def plot_combined_chart(sprint_reports):
    sprint_names = [r['sprint_name'] for r in sprint_reports]
    committed = [r['committed'] for r in sprint_reports]
    delivered = [r['delivered'] for r in sprint_reports]
    say_do = [round((r['delivered'] / r['committed']), 2) if r['committed'] else 0 for r in sprint_reports]

    fig = go.Figure()

    # Bar: Committed
    fig.add_trace(go.Bar(
        x=sprint_names,
        y=committed,
        name='Committed',
        marker_color='steelblue',
        text=committed,
        textposition='outside'
    ))

    # Bar: Delivered
    fig.add_trace(go.Bar(
        x=sprint_names,
        y=delivered,
        name='Delivered',
        marker_color='orangered',
        text=delivered,
        textposition='outside'
    ))

    # Line: Say-Do Ratio
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

    # Layout
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


def generate_say_do_chart(sprint_reports):
    sprints = [r['sprint_name'] for r in sprint_reports]
    ratios = [(r['delivered'] / r['committed']) if r['committed'] > 0 else 0 for r in sprint_reports]

    plt.figure(figsize=(10, 4))
    plt.plot(sprints, ratios, marker='o', color='blue')
    plt.title("Say-Do Ratio per Sprint")
    plt.ylabel("Ratio")
    plt.ylim(0, max(ratios) + 0.5)
    st.pyplot(plt)

def to_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'

# -----------------------
# Streamlit App UI
# -----------------------

def main():
    st.title("📊 Jira Sprint Reporting Tool")

    project_key = st.text_input("Enter Jira Project Code/Name:")

    if project_key:
        boards = get_boards(project_key)
        if not boards:
            st.error("No boards found for this project.")
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

                committed, delivered = 0, 0
                issue_rows = []

                for issue in issues:
                    fields = issue['fields']
                    story_points = fields.get(STORY_POINT_FIELD, 0) or 0
                    status = fields['status']['name']

                    committed += story_points
                    if status.lower() in ['done', 'closed', 'resolved']:
                        delivered += story_points

                    issue_rows.append({
                        'Issue Key': issue['key'],
                        'Summary': fields.get('summary', ''),
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

            # Charts
            st.subheader("📈 Velocity Chart")
            plot_velocity_chart(sprint_reports)
            
            st.subheader("📈 Sprint Statistics (Committed vs Delivered + Say-Do Ratio)")
            plot_combined_chart(sprint_reports)

            st.subheader("📉 Say-Do Ratio")
            generate_say_do_chart(sprint_reports)

            # Summary Table
            st.subheader("📊 Summary Table")
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
