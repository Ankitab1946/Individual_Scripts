# 📊 Streamlit Jira Sprint Reporting Tool

This is a **Streamlit-based web application** that connects to your Jira project and generates detailed sprint reports, metrics, and charts. It supports both interactive use and weekly automation, with full GitLab CI/CD and Docker integration.

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

## 🧱 Folder Structure

```
jira-reporting-app/
├── jira_report_app.py          # Main Streamlit UI
├── generate_weekly_report.py   # Script for weekly automation (optional)
├── requirements.txt
├── Dockerfile
├── .gitlab-ci.yml
└── README.md
```

---

## 💻 Local Setup

### 1. Clone the Repository

```bash
git clone https://gitlab.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the App

```bash
streamlit run jira_report_app.py
```

> You’ll be prompted for your **Jira username/email** and **API token** in the Streamlit sidebar.

---

## 🐳 Docker Setup

### Build Image

```bash
docker build -t jira-report-app .
```

### Run Container

```bash
docker run -p 8501:8501 jira-report-app
```

Then open your browser at: [http://localhost:8501](http://localhost:8501)

---

## 🤖 GitLab CI/CD Setup

This project includes a `.gitlab-ci.yml` to:

- Build Docker image
- Push to GitLab Container Registry
- (Optional) Deploy

### Prerequisites

Go to GitLab → Project → Settings → CI/CD → Variables and add:

- `CI_REGISTRY_USER`: your GitLab username
- `CI_REGISTRY_PASSWORD`: GitLab personal access token

### CI/CD Flow

1. **Push to GitLab**
2. **GitLab runner** triggers:
   - Docker image build
   - Push to GitLab registry
3. **Deploy step** (manual or extend with auto-deploy)

---

## 🔁 Weekly Report Automation

To automate report generation every week:

### Step 1: Configure `generate_weekly_report.py`
- Automatically fetches latest sprint
- Generates CSV and graphs
- Saves output in `/weekly_reports/`

### Step 2: Schedule

#### Windows (Task Scheduler):
Run weekly:  
```
python generate_weekly_report.py
```

#### Linux/macOS (Cron):
Add to crontab:
```
0 8 * * 1 /usr/bin/python3 /path/to/generate_weekly_report.py
```

---

## 🔐 Security Best Practices

- ❌ Do NOT hardcode Jira credentials
- ✅ Use Streamlit sidebar input for login
- ✅ Use `.env` or secrets manager in production
- ✅ Protect Docker endpoints if deploying publicly

---

## 🧠 Future Enhancements (Optional)

- 🔄 OAuth2 login with Atlassian
- 🔄 Export reports to Confluence
- 📧 Email weekly reports
- 📊 Multi-project dashboard support
- 🧪 Add unit testing

---

## 📬 Contact / Feedback

Made with ❤️ by [Your Name]  
🔗 [LinkedIn](https://linkedin.com/in/your-profile) | ✉️ your.email@example.com

Have an idea or feature request? Open an issue or contribute via GitLab!

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).
