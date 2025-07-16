# 🚀 Streamlit SQL Explorer for Large Files

This project is a lightweight Streamlit web app powered by [DuckDB](https://duckdb.org/), allowing users to:
- Upload large `.csv`, `.dat`, `.parquet`, or `.icr` files
- Execute interactive SQL queries (`SELECT`, `JOIN`, `GROUP BY`, etc.)
- Download filtered data using custom delimiters
- Deploy in Docker and share over the network

---

## 🧱 Project Structure

streamlit-sql-app/
│
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── Dockerfile # Docker container config
├── .gitlab-ci.yml # GitLab CI/CD pipeline
├── README.md # This documentation
├── .dockerignore # Optional Docker cleanup
└── data/ # Optional test data folder


---

## ▶️ How to Run Locally

```bash
# Step 1: Clone repo
git clone https://gitlab.com/your-org/streamlit-sql-app.git
cd streamlit-sql-app

# Step 2: Create and activate virtual env (optional)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run the app
streamlit run app.py

## DOCKER Setup
# Build Docker image
docker build -t streamlit-sql .

# Run Docker container (default port 8501)
docker run -p 8501:8501 streamlit-sql
