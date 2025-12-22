# Deployment Instructions

## Push to GitHub Repository

Follow these steps to push the project to the GitHub repository:

### 1. Initialize Git Repository (if not already initialized)

```bash
cd /Users/maximdoroshenko/Documents/DocBot
git init
```

### 2. Add All Files

```bash
git add .
```

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: LangGraph DocBot with Conversational Requirements Agent"
```

### 4. Add Remote Repository

```bash
git remote add origin https://github.com/NikolaienkoIgor/it_documentation_agent.git
```

### 5. Set Main Branch

```bash
git branch -M main
```

### 6. Push to Repository

**Option A: If repository is empty or you want to force push:**
```bash
git push -u origin main --force
```

**Option B: If repository has content and you want to merge:**
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### 7. Verify

Check the repository at: https://github.com/NikolaienkoIgor/it_documentation_agent

## Important Notes

- Make sure you have write access to the repository
- If you encounter authentication issues, you may need to set up SSH keys or use a personal access token
- The `--force` flag will overwrite any existing content in the repository

## Files to Include

The following files will be pushed:
- All source code in `langgraph_docbot/`
- Configuration files (`.env.example`, `requirements.txt`)
- Documentation files (README.md, CONVERSATIONAL_AGENT.md, GEMINI_ENTERPRISE_INTEGRATION.md)
- Scripts (`run_streamlit.sh`)

## Files to Exclude (if .gitignore exists)

- `.env` (contains sensitive API keys)
- `__pycache__/` directories
- `.venv/` or virtual environment directories
- `generated_docs/` (optional - can be included)
- `memory/` (optional - can be included)

