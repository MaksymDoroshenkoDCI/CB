# 🧾 LangGraph DocBot

> **AI-powered technical documentation generator for IT systems**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.1+-orange.svg)](https://langchain-ai.github.io/langgraph/)

---

## ✨ Features

- 💬 **Conversational Requirements Agent** - Multi-turn dialog for gathering requirements before documentation generation
- 📋 **JSON-based Dialog Structure** - Questions loaded from JSON file, easy to customize
- 🤖 **Simplified Architecture** - LangGraph workflow: Conversation → Documentation → Save
- 🧠 **Gemini 2.5-pro** - Powered by Google Gemini via langchain-google-genai
- 🚀 **FastAPI Backend** - Fast and modern REST API with conversation endpoints
- 🎨 **Streamlit UI** - Intuitive web interface with interview mode
- 💾 **Auto-save** - Results saved to .txt files
- 📝 **Session Memory** - Generation history tracking and conversation state management
- 🎯 **Project Support** - Specify project name (e.g., fintom8)

---

## 🏗️ Architecture

```
┌─────────────┐
│  Streamlit  │  ← Web interface for users
│     UI      │  (Direct mode / Interview mode)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   FastAPI   │  ← REST API server
│   Backend   │  (/generate, /conversation/*)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────┐
│        LangGraph Workflow                   │
│                                             │
│  ┌──────────────────────┐                   │
│  │ Conversation Agent  │  ← Reads questions│
│  │  (Q&A Dialog)       │    from JSON file  │
│  │                     │    Collects answers│
│  └──────────┬───────────┘                   │
│             │ when complete                  │
│             ▼                                │
│  ┌──────────────────────┐                   │
│  │ Documentation Agent  │  ← Generates     │
│  │  (Gemini 2.5-pro)    │    complete doc   │
│  └──────────┬───────────┘                   │
│             │                                │
│             ▼                                │
│  ┌──────────────────────┐                   │
│  │   Save Node          │  ← Saves to       │
│  │                      │    generated_docs│
│  └──────────────────────┘                   │
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Gemini    │  ← Google Gemini 2.5-pro
│     API     │
└─────────────┘
```

---

## 📦 Installation

### 1️⃣ Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd langgraph_docbot

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configure API Key

```bash
# Copy example configuration
cp .env.example .env

# Edit .env and add your GOOGLE_API_KEY
nano .env  # or use any editor
```

### 🔑 How to Get Google API Key (GOOGLE_API_KEY):

#### Method 1: Google AI Studio (Recommended) ⭐

1. 🌐 Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 🔐 Sign in with your Google account
3. ➕ Click **"Create API Key"**
4. 📋 Copy the generated key
5. 📝 Paste it into your `.env` file:
   ```env
   GOOGLE_API_KEY=your_key_here
   ```

#### Method 2: Google Cloud Console

1. 🌐 Go to [Google Cloud Console](https://console.cloud.google.com/)
2. 📁 Create a new project or select an existing one
3. ⚙️ Enable **"Generative Language API"**
4. 🔧 Navigate to **"APIs & Services"** → **"Credentials"**
5. ➕ Create an **"API Key"** and copy it

---

## 🚀 Running

### 🌐 API Server

```bash
cd langgraph_docbot
uvicorn api.main:app --reload
```

API will be available at:
- 📍 **Main URL**: `http://localhost:8000`
- 📚 **Swagger Documentation**: `http://localhost:8000/docs`
- 🔍 **Alternative Documentation**: `http://localhost:8000/redoc`

**Available Endpoints:**
- `POST /generate` - Direct documentation generation
- `POST /conversation/start` - Start new conversation
- `POST /conversation/continue` - Continue conversation with answer
- `POST /conversation/generate` - Generate documentation from conversation

### 🎨 Streamlit UI (Recommended)

```bash
# Option 1: Using script
./run_streamlit.sh

# Option 2: Direct run
streamlit run ui/streamlit_app.py
```

UI will be available at: `http://localhost:8501`

---

## 📖 Usage

### Via Streamlit UI 🖥️

#### Mode 1: Direct Mode
1. ✏️ Enter **project name** (e.g., `fintom8`)
2. 📝 Describe the system or documentation request
3. 🚀 Click **"Generate Documentation"**
4. ⏳ Wait for generation to complete
5. 📄 Review the generated document

#### Mode 2: Interview Mode ⭐ Recommended
1. 🎯 Select **"Interview (dialog)"** mode in sidebar
2. ✏️ Enter **project name** (optional)
3. 🚀 Click **"Start Interview"**
4. 💬 Answer questions about your system (multi-turn dialog)
   - 🌍 **You can answer in ANY language** (English, Ukrainian, Russian, etc.)
   - The system will understand and process your answers regardless of language
   - Final documentation will be generated in English
5. ✅ When all requirements collected, click **"Generate Documentation"**
6. 📄 Review the generated documentation

### Via API 🔌

#### Direct Generation (without dialog)

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Description of your IT system...",
    "project_name": "fintom8",
    "session_id": "optional-session-id"
  }'
```

#### Conversational Mode (with dialog) ⭐ Recommended

```bash
# 1. Start dialog
curl -X POST "http://localhost:8000/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "fintom8"
  }'

# 2. Continue dialog (repeat for each question)
curl -X POST "http://localhost:8000/conversation/continue" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-id-from-step-1",
    "answer": "Your answer to the question"
  }'

# 3. Generate documentation after completing dialog
curl -X POST "http://localhost:8000/conversation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-id-from-step-1"
  }'
```

Детальні приклади використання API доступні в [Swagger Documentation](http://localhost:8000/docs).

---

## 📁 Project Structure

```
langgraph_docbot/
├── 📂 app/                      # Core logic
│   ├── __init__.py
│   ├── config.py                # Configuration
│   ├── state.py                 # Application state
│   ├── agents.py                # Documentation generation agent
│   ├── conversation_agent.py    # ⭐ Conversational requirements agent
│   ├── dialog_structure.json    # ⭐ Dialog questions configuration
│   ├── graph.py                 # LangGraph workflow
│   ├── memory.py                # Memory management
│   ├── session_store.py         # ⭐ Conversation session management
│   ├── validators.py            # Input validation
│   └── storage.py               # Document storage
│
├── 📂 api/                      # FastAPI REST API
│   ├── __init__.py
│   └── main.py                  # Main API file (with conversation endpoints)
│
├── 📂 ui/                       # Streamlit UI
│   ├── __init__.py
│   └── streamlit_app.py        # Main UI file (with interview mode)
│
├── 📂 tests/                    # Tests
│   └── test_basic.py
│
├── 📂 memory/                   # Session storage
│   ├── session_memory.json      # Generation history
│   └── conversation_sessions.json # ⭐ Conversation sessions
│
├── 📂 generated_docs/           # Generated documentation files
│
├── 📄 .env.example              # Configuration example
├── 📄 requirements.txt          # Python dependencies
├── 📄 README.md                 # This file
├── 📄 EXAMPLE_FINTOM8.md        # Example usage
└── 🚀 run_streamlit.sh          # Streamlit launch script
```

---

## 🎯 Example Usage for fintom8 Project

Detailed example can be found in [`EXAMPLE_FINTOM8.md`](EXAMPLE_FINTOM8.md)

**Quick Start (Direct Mode):**
1. 🏷️ Enter project name: `fintom8`
2. 📝 Describe the system with technical details
3. 🚀 Click "Generate Documentation"
4. 🎉 Get complete technical documentation!

**Quick Start (Interview Mode):**
1. 🏷️ Enter project name: `fintom8`
2. 💬 Start interview and answer questions
3. ✅ Complete the dialog
4. 🚀 Generate documentation
5. 🎉 Get complete technical documentation based on collected requirements!

---

## 🔧 Technologies

- **🐍 Python 3.11+** - Main programming language
- **⚡ FastAPI** - Modern web framework
- **🎨 Streamlit** - Interactive UI framework
- **🕸️ LangGraph** - Agent orchestration
- **🔗 LangChain** - LLM integration
- **🤖 Google Gemini 2.5-pro** - AI model for documentation generation
- **📦 Pydantic** - Data validation
- **📋 JSON** - Dialog structure configuration

---

## 📝 Generated Documentation Includes

- 📋 Introduction and system overview
- 🏛️ System architecture (components, diagrams)
- 💻 Tech stack (languages, frameworks, databases)
- ⚙️ Functionality (modules, features)
- 🔌 API and integrations
- 🗄️ Database (schema, models)
- 🔒 Security (authentication, authorization)
- 🚀 Deployment and infrastructure
- 🧪 Testing
- 📊 Monitoring and logging
- 👨‍💻 Developer documentation

---

## 💬 Conversational Requirements Agent

DocBot features a **Conversational Requirements Agent** - an interactive dialog for gathering requirements before documentation generation.

### Key Features:

- 🗣️ **Multi-turn Dialog** - Agent conducts structured dialog with user
- 🌍 **Multi-language Support** - Users can answer questions in ANY language (English, Ukrainian, Russian, etc.)
- 📝 **English Output** - All documentation is generated in English, regardless of input language
- 📋 **JSON-based Configuration** - Questions loaded from `dialog_structure.json`
- 💾 **Session Management** - Dialog state stored between requests
- 🎯 **Requirements Gathering** - Collects all necessary requirements before generation
- ✅ **Flexible Completion** - User can complete dialog at any time
- 🚀 **Direct Generation** - Single prompt to Gemini 2.5-pro for complete documentation

### How It Works:

1. **Dialog Structure** - Questions are loaded from `app/dialog_structure.json`
2. **Question Flow** - Agent asks questions one by one
3. **Answer Collection** - User answers are stored
4. **Summary Creation** - All answers are formatted into requirements summary
5. **Documentation Generation** - Complete documentation generated via Gemini 2.5-pro
6. **Auto-save** - Result saved to `generated_docs/` folder

### Customizing Questions:

Edit `app/dialog_structure.json` to customize:
- Add/remove questions
- Change question text
- Mark questions as required/optional
- Add completion trigger phrases

No code changes needed!

---

## 🤝 Contributing

Contributions are welcome! Please:
1. 🍴 Fork the project
2. 🌿 Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push to the branch (`git push origin feature/AmazingFeature`)
5. 🔀 Open a Pull Request

---

## 📄 License

This project is distributed under the MIT license.

---

## 🙏 Acknowledgments

- [LangGraph](https://langchain-ai.github.io/langgraph/) for the amazing framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) for the powerful AI model
- [FastAPI](https://fastapi.tiangolo.com/) for the fast web framework
- [Streamlit](https://streamlit.io/) for the simple UI framework

---

<div align="center">

**Made with ❤️ to simplify technical documentation creation**

⭐ If this project was helpful, please give it a star!

</div>
