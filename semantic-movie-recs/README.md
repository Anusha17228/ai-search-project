# CinemaMind: AI Semantic Movie Search 🎬

CinemaMind is an AI-powered search engine that understands the meaning behind your movie queries.

---

## 💻 How to Run (Web Interface)

### 1. Unified Startup
Run the master script to start both the Vector DB and the Web App:
```bash
python semantic-movie-recs/run_all.py
```

### 2. Access the Web UI
Open your browser and go to:
👉 **[http://localhost:5000](http://localhost:5000)**

### 3. Ingest Data (One-time)
If this is your first time or the server is empty, run:
```bash
python semantic-movie-recs/ingest.py
```
*Note: The Mock server now persists data, so you won't lose your index on restart.*

---

## 🧪 Search Examples
- "A journey through space and time"
- "Mind-bending dream secrets"
- "A computer hacker discovers the truth"
