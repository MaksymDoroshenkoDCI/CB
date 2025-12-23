# How to Start the Server

## Quick Start

### Option 1: Using the script

```bash
cd /Users/maximdoroshenko/Documents/DocBot/langgraph_docbot
./start_server.sh
```

### Option 2: Manual start

```bash
cd /Users/maximdoroshenko/Documents/DocBot/langgraph_docbot
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Start in background

```bash
cd /Users/maximdoroshenko/Documents/DocBot/langgraph_docbot
source .venv/bin/activate
nohup uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```

## Start Streamlit UI

In a new terminal:

```bash
cd /Users/maximdoroshenko/Documents/DocBot/langgraph_docbot
source .venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8501
```

## Check if server is running

```bash
curl http://localhost:8000/health
```

Should return: `{"status":"healthy"}`

## Troubleshooting

If you get permission errors, try:
```bash
chmod -R u+w .venv
```

Or reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

