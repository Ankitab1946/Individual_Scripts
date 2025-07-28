# 📊 Streamlit Jira Sprint Reporting Tool

This is a Streamlit-based web application that connects to your Jira project and generates detailed sprint reports including:

- ✅ Issue-level Sprint Reports
- 📈 Velocity Charts
- 🔁 Committed vs Delivered Tracking
- 📉 Say-Do Ratio Charts
- ✏️ Editable Reports with Correction Comments

---

## 🚀 Key Features

- 🔐 Secure Jira authentication via UI (no hardcoding)
- 🗂️ Fetch Boards, Sprints, and Issues from Jira Agile API
- 📋 Sprint-level reports with story points and statuses
- 📉 Visualizations:
  - Velocity Chart (Committed vs Delivered)
  - Say-Do Ratio per Sprint
  - Combined dual-axis chart (Story Points + Ratio)
- 📤 CSV download of raw and summary reports
- ✏️ User can edit committed/delivered points and leave comments
- 🗓️ Weekly automation support
- 🐳 Dockerized for portability
- 🤖 GitLab CI/CD ready

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://gitlab.com/your-username/your-repo-name.git
cd your-repo-name


### 2. Install Dependencies (Locally)

