# 🧾 LangGraph DocBot

> **AI-powered technical documentation generator for IT systems**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.1+-orange.svg)](https://langchain-ai.github.io/langgraph/)

---

## ✨ Features

- 💬 **Conversational Requirements Agent** - Multi-turn dialog for gathering requirements before documentation generation
- 🤖 **Multi-agent Architecture** - LangGraph with multiple agents (conversation, outline, draft, refine)
- 🧠 **Gemini AI** - Powered by Google Gemini via langchain-google-genai
- 🚀 **FastAPI Backend** - Fast and modern REST API with conversation endpoints
- 🎨 **Streamlit UI** - Intuitive web interface with interview mode
- 💾 **Auto-save** - Results saved to .txt files
- 📝 **Session Memory** - Generation history tracking and conversation state management
- 🎯 **Project Support** - Specify project name (e.g., fintom8)
- 🔗 **Gemini Enterprise Integration** - Ready for integration with Gemini Enterprise Agents

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
│  │ Conversation Agent  │  ← збирає вимоги  │
│  │  (Q&A Dialog)       │                   │
│  └──────────┬───────────┘                   │
│             │ коли готово                    │
│             ▼                                │
│  ┌──────────┐  ┌──────────┐                  │
│  │ Outline  │→ │  Draft   │→                │
│  │  Agent   │  │  Agent   │                 │
│  └──────────┘  └────┬─────┘                  │
│                     │                        │
│              ┌──────▼─────┐                 │
│              │  Refine    │                 │
│              │   Agent    │                 │
│              └──────┬─────┘                 │
│                     │                        │
│              ┌──────▼─────┐                 │
│              │  Persist  │                 │
│              │   Node     │                 │
│              └────────────┘                 │
└─────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   Gemini    │  ← Google AI Model
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

#### Режим 1: Прямий режим (Direct Mode)
1. ✏️ Enter **project name** (e.g., `fintom8`)
2. 📝 Describe the system or documentation request
3. 🚀 Click **"Generate Documentation"**
4. ⏳ Wait for generation to complete
5. 📄 Review the structure and final document

#### Режим 2: Інтерв'ю (Interview Mode) ⭐ NEW
1. 🎯 Select **"Інтерв'ю (діалог)"** mode in sidebar
2. ✏️ Enter **project name** (optional)
3. 🚀 Click **"Почати інтерв'ю"**
4. 💬 Answer questions about your system (multi-turn dialog)
5. ✅ When all requirements collected, click **"Згенерувати документацію"**
6. 📄 Review the generated documentation

### Via API 🔌

#### Direct Generation (без діалогу)

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Description of your IT system...",
    "project_name": "fintom8",
    "session_id": "optional-session-id"
  }'
```

#### Conversational Mode (з діалогом) ⭐ NEW

```bash
# 1. Почати діалог
curl -X POST "http://localhost:8000/conversation/start" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "fintom8"
  }'

# 2. Продовжити діалог (повторювати для кожного питання)
curl -X POST "http://localhost:8000/conversation/continue" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-id-from-step-1",
    "answer": "Your answer to the question"
  }'

# 3. Згенерувати документацію після завершення діалогу
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
│   ├── agents.py                # Agents (outline, draft, refine)
│   ├── conversation_agent.py    # ⭐ Conversational requirements agent
│   ├── graph.py                 # LangGraph workflow
│   ├── memory.py                # Memory management
│   ├── session_store.py         # ⭐ Conversation session management
│   ├── validators.py            # Input validation
│   ├── storage.py               # Document storage
│   └── prompts.py               # AI prompts
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
├── 📄 CONVERSATIONAL_AGENT.md   # ⭐ Conversational agent documentation
├── 📄 GEMINI_ENTERPRISE_INTEGRATION.md # ⭐ Gemini Enterprise integration guide
└── 🚀 run_streamlit.sh          # Streamlit launch script
```

---

## 🎯 Example Usage for fintom8 Project

Detailed example can be found in [`EXAMPLE_FINTOM8.md`](EXAMPLE_FINTOM8.md)

**Quick Start (Direct Mode):**
1. 🏷️ Enter project name: `fintom8`
2. 📝 Describe the system with technical details
3. 🎉 Get complete technical documentation!

**Quick Start (Interview Mode):**
1. 🏷️ Enter project name: `fintom8`
2. 💬 Start interview and answer questions
3. ✅ Complete the dialog
4. 🎉 Get complete technical documentation based on collected requirements!

---

## 🔧 Technologies

- **🐍 Python 3.11+** - Main programming language
- **⚡ FastAPI** - Modern web framework
- **🎨 Streamlit** - Interactive UI framework
- **🕸️ LangGraph** - Agent orchestration
- **🔗 LangChain** - LLM integration
- **🤖 Google Gemini** - AI model
- **📦 Pydantic** - Data validation

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

DocBot тепер підтримує **Conversational Requirements Agent** - інтерактивний діалог для збору вимог перед генерацією документації.

### Основні можливості:

- 🗣️ **Multi-turn Dialog** - Агент веде структурований діалог з користувачем
- 🧠 **Adaptive Questions** - Питання адаптуються на основі попередніх відповідей
- 💾 **Session Management** - Зберігання стану діалогу між запитами
- 🎯 **Requirements Gathering** - Збір всіх необхідних вимог перед генерацією
- ✅ **Flexible Completion** - Користувач може завершити діалог в будь-який момент

### Питання для збору вимог:

1. Опиши основну мету системи
2. Хто основні користувачі системи?
3. Які ключові функції повинні бути реалізовані?
4. Які технології плануються?
5. Які інтеграції потрібні?
6. Які вимоги до безпеки?
7. Опиши архітектуру системи
8. Які вимоги до розгортання?

Детальна документація: [`CONVERSATIONAL_AGENT.md`](CONVERSATIONAL_AGENT.md)

---

## 🔗 Integration with Gemini Enterprise Agents

DocBot готовий до інтеграції з **Gemini Enterprise Agents** для створення повноцінного conversational агента.

### Переваги інтеграції:

- ✅ Використання LangGraph як backend workflow engine
- ✅ Gemini Enterprise як фронтовий conversational agent
- ✅ API endpoints для multi-turn діалогу
- ✅ Session management для збереження стану

Детальна інструкція з налаштування: [`GEMINI_ENTERPRISE_INTEGRATION.md`](GEMINI_ENTERPRISE_INTEGRATION.md)

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
