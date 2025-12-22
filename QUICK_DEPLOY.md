# Quick Deploy Guide

## Push Project to GitHub

Execute these commands in your terminal:

```bash
cd /Users/maximdoroshenko/Documents/DocBot

# Option 1: Use the automated script
./deploy_to_github.sh

# Option 2: Manual commands
git init
git add .
git commit -m "Initial commit: LangGraph DocBot with Conversational Requirements Agent"
git remote add origin https://github.com/NikolaienkoIgor/it_documentation_agent.git
git branch -M main
git push -u origin main --force
```

## Important Notes

⚠️ **If repository already has content:**
- Use `--force` flag to overwrite (as shown above)
- Or pull first: `git pull origin main --allow-unrelated-histories` then push

🔐 **Authentication:**
- You may need to authenticate with GitHub
- Use personal access token or SSH keys if prompted

✅ **After push:**
- Check repository: https://github.com/NikolaienkoIgor/it_documentation_agent
- README.md will be automatically included

