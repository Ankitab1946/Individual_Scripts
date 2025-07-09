## Folder: release_test_framework_gui_tool/

# config.py
JIRA_URL = "https://yourdomain.atlassian.net"
JIRA_USER = "your-email@example.com"
JIRA_TOKEN = "your_api_token"
PROJECT_KEY = "ABC"
TEST_INDICATOR_FIELD = "customfield_12345"  # Field for 'Indicator Testing Required'


# gui_input.py
import tkinter as tk
from tkinter import messagebox

def get_user_input():
    def submit():
        mode_val = mode.get()
        value_val = value.get()
        if not mode_val or not value_val:
            messagebox.showwarning("Input Required", "Please select a mode and enter a name.")
        else:
            root.mode = mode_val
            root.value = value_val
            root.destroy()

    root = tk.Tk()
    root.title("Test Plan Generator")

    tk.Label(root, text="Select Mode (Release/Sprint):").grid(row=0, column=0)
    mode = tk.StringVar()
    tk.OptionMenu(root, mode, "release", "sprint").grid(row=0, column=1)

    tk.Label(root, text="Enter Name:").grid(row=1, column=0)
    value = tk.Entry(root)
    value.grid(row=1, column=1)

    tk.Button(root, text="Generate", command=submit).grid(row=2, columnspan=2)
    root.mainloop()

    return root.mode, root.value


# jira_utils.py
from jira import JIRA
from config import *

def connect_to_jira():
    return JIRA(server=JIRA_URL, basic_auth=(JIRA_USER, JIRA_TOKEN))

def get_target_user_stories(jira, mode, value):
    if mode == 'release':
        jql = f'project = {PROJECT_KEY} AND fixVersion = "{value}" AND issuetype = Story AND "{TEST_INDICATOR_FIELD}" = "Yes"'
    elif mode == 'sprint':
        jql = f'project = {PROJECT_KEY} AND Sprint = "{value}" AND issuetype = Story AND "{TEST_INDICATOR_FIELD}" = "Yes"'
    else:
        raise ValueError("Invalid mode. Choose 'release' or 'sprint'")
    return jira.search_issues(jql, maxResults=100)


# test_plan_utils.py
def create_test_plan(jira, name):
    issue_dict = {
        'project': {'key': PROJECT_KEY},
        'summary': name,
        'issuetype': {'name': 'Test Plan'}
    }
    return jira.create_issue(fields=issue_dict)

def create_test_set(jira, story):
    issue_dict = {
        'project': {'key': PROJECT_KEY},
        'summary': f"Test Set for {story.key}",
        'issuetype': {'name': 'Test Set'}
    }
    return jira.create_issue(fields=issue_dict)

def create_test_cases(jira, story, count=3):
    test_cases = []
    for i in range(count):
        test = jira.create_issue(fields={
            'project': {'key': PROJECT_KEY},
            'summary': f"Test Case {i+1} for {story.key}",
            'issuetype': {'name': 'Test'}
        })
        jira.create_issue_link(type="Tests", inwardIssue=test.key, outwardIssue=story.key)
        test_cases.append(test)
    return test_cases

def create_test_execution(jira, test_plan, test_set):
    exec_issue = jira.create_issue(fields={
        'project': {'key': PROJECT_KEY},
        'summary': f"Execution for {test_set.key}",
        'issuetype': {'name': 'Test Execution'}
    })
    jira.create_issue_link("Test Plan", test_plan.key, exec_issue.key)
    jira.create_issue_link("Tests", test_set.key, exec_issue.key)
    return exec_issue


# traceability.py
import pandas as pd

def export_traceability(user_stories, test_sets, test_cases_map, executions, file_path):
    rows = []
    for story in user_stories:
        tset = test_sets[story.key]
        cases = test_cases_map[story.key]
        exec = executions[story.key]
        for tc in cases:
            rows.append({
                "User Story": story.key,
                "Test Set": tset.key,
                "Test Case": tc.key,
                "Execution": exec.key
            })
    df = pd.DataFrame(rows)
    df.to_excel(file_path, index=False)


# main.py
from gui_input import get_user_input
from jira_utils import connect_to_jira, get_target_user_stories
from test_plan_utils import create_test_plan, create_test_set, create_test_cases, create_test_execution
from traceability import export_traceability

def main():
    mode, value = get_user_input()
    jira = connect_to_jira()
    stories = get_target_user_stories(jira, mode, value)

    plan_name = f"Test Plan for {value}"
    test_plan = create_test_plan(jira, plan_name)

    test_sets = {}
    test_cases_map = {}
    executions = {}

    for story in stories:
        tset = create_test_set(jira, story)
        test_sets[story.key] = tset

        tcs = create_test_cases(jira, story)
        test_cases_map[story.key] = tcs

        exec = create_test_execution(jira, test_plan, tset)
        executions[story.key] = exec

    export_traceability(
        stories, test_sets, test_cases_map, executions,
        f"data/traceability_{value.replace(' ', '_')}.xlsx"
    )

if __name__ == "__main__":
    main()


# requirements.txt
jira
pandas
openpyxl
tk
