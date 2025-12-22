#!/bin/bash

# Script to deploy LangGraph DocBot to GitHub repository
# Repository: https://github.com/NikolaienkoIgor/it_documentation_agent.git

set -e  # Exit on error

echo "🚀 Starting deployment to GitHub..."

# Check if we're in the right directory
if [ ! -d "langgraph_docbot" ]; then
    echo "❌ Error: langgraph_docbot directory not found. Please run this script from the project root."
    exit 1
fi

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add remote (remove if exists, then add)
if git remote get-url origin &>/dev/null; then
    echo "🔄 Updating remote origin..."
    git remote set-url origin https://github.com/NikolaienkoIgor/it_documentation_agent.git
else
    echo "➕ Adding remote origin..."
    git remote add origin https://github.com/NikolaienkoIgor/it_documentation_agent.git
fi

# Add all files
echo "📝 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "💾 Creating commit..."
    git commit -m "Initial commit: LangGraph DocBot with Conversational Requirements Agent

- Added Conversational Requirements Agent for multi-turn dialog
- Integrated with LangGraph workflow
- FastAPI backend with conversation endpoints
- Streamlit UI with interview mode
- Full English language support
- Ready for Gemini Enterprise integration"
fi

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main

# Push to repository
echo "⬆️  Pushing to GitHub..."
echo "⚠️  Note: You may need to authenticate. If the repository already has content, you may need to use --force"
read -p "Do you want to force push? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin main --force
else
    # Try normal push first
    if ! git push -u origin main 2>&1; then
        echo "⚠️  Normal push failed. You may need to pull first or use --force"
        echo "   Try: git pull origin main --allow-unrelated-histories"
        echo "   Or:  git push -u origin main --force"
    fi
fi

echo "✅ Deployment complete!"
echo "🔗 Repository: https://github.com/NikolaienkoIgor/it_documentation_agent"

