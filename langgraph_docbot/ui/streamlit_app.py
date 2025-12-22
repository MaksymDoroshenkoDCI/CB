import streamlit as st
import requests
import os

BASE_API_URL = os.getenv("API_URL", "http://localhost:8000")
API_URL = f"{BASE_API_URL}/generate"
CONV_START_URL = f"{BASE_API_URL}/conversation/start"
CONV_CONTINUE_URL = f"{BASE_API_URL}/conversation/continue"
CONV_GENERATE_URL = f"{BASE_API_URL}/conversation/generate"

st.set_page_config(page_title="DocBot (LangGraph + Gemini)", layout="wide")
st.title("🧾 IT Documentation Generator")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "conversation_mode" not in st.session_state:
    st.session_state["conversation_mode"] = False
if "conversation_answers" not in st.session_state:
    st.session_state["conversation_answers"] = []
if "current_question" not in st.session_state:
    st.session_state["current_question"] = None
if "conversation_complete" not in st.session_state:
    st.session_state["conversation_complete"] = False

# Mode selection
st.sidebar.header("⚙️ Work Mode")
mode = st.sidebar.radio(
    "Select mode:",
    ["Direct (one-time request)", "Interview (dialog)"],
    index=0 if not st.session_state["conversation_mode"] else 1
)

if mode == "Interview (dialog)":
    st.session_state["conversation_mode"] = True
else:
    st.session_state["conversation_mode"] = False
    # Reset dialog state when switching
    if st.session_state["conversation_complete"]:
        st.session_state["conversation_answers"] = []
        st.session_state["current_question"] = None
        st.session_state["conversation_complete"] = False

# ========== INTERVIEW MODE ==========
if st.session_state["conversation_mode"]:
    st.header("💬 Interview Mode")
    st.info("The agent will ask you several questions to gather requirements. After completing the dialog, documentation will be generated.")
    
    # Start dialog
    if not st.session_state["session_id"] or st.session_state["current_question"] is None:
        with st.form("start_conversation_form"):
            project_name = st.text_input(
                "Project name (optional):",
                placeholder="e.g., fintom8",
                value="fintom8"
            )
            start_btn = st.form_submit_button("Start Interview", use_container_width=True)
            
            if start_btn:
                with st.spinner("Initializing dialog..."):
                    try:
                        payload = {
                            "project_name": project_name.strip() if project_name else None,
                            "session_id": st.session_state.get("session_id"),
                        }
                        resp = requests.post(CONV_START_URL, json=payload, timeout=120)
                        
                        if resp.status_code != 200:
                            st.error(f"❌ Error: {resp.status_code}")
                            st.code(resp.text[:500], language="text")
                        else:
                            data = resp.json()
                            st.session_state["session_id"] = data["session_id"]
                            st.session_state["current_question"] = data["question"]
                            st.session_state["conversation_answers"] = []
                            st.session_state["conversation_complete"] = False
                            st.rerun()
                    except requests.exceptions.ConnectionError:
                        st.error("❌ Failed to connect to API server. Make sure the server is running on http://localhost:8000")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timeout. The server is taking too long to respond. Please try again or restart the API server.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # Continue dialog
    elif not st.session_state["conversation_complete"]:
        st.subheader("📝 Dialog")
        
        # Show dialog history
        if st.session_state["conversation_answers"]:
            st.markdown("### Answer History:")
            for i, (q, a) in enumerate(st.session_state["conversation_answers"], 1):
                with st.expander(f"Question {i}: {q[:50]}..."):
                    st.markdown(f"**Answer:** {a}")
        
        # Current question
        if st.session_state["current_question"]:
            st.markdown(f"### ❓ {st.session_state['current_question']}")
            
            with st.form("answer_form"):
                answer = st.text_area(
                    "Your answer:",
                    height=150,
                    placeholder="Enter your answer or type 'Done' to complete the dialog"
                )
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    submit_btn = st.form_submit_button("Submit Answer", use_container_width=True)
                with col2:
                    skip_btn = st.form_submit_button("Skip Question", use_container_width=True)
                
                if submit_btn and answer.strip():
                    with st.spinner("Processing answer..."):
                        try:
                            payload = {
                                "session_id": st.session_state["session_id"],
                                "answer": answer.strip()
                            }
                            resp = requests.post(CONV_CONTINUE_URL, json=payload, timeout=120)
                            
                            if resp.status_code != 200:
                                st.error(f"❌ Error: {resp.status_code}")
                                st.code(resp.text[:500], language="text")
                            else:
                                data = resp.json()
                                
                                # Save answer to history
                                st.session_state["conversation_answers"].append(
                                    (st.session_state["current_question"], answer.strip())
                                )
                                
                                if data["conversation_complete"]:
                                    st.session_state["conversation_complete"] = True
                                    st.session_state["current_question"] = None
                                    st.success("✅ All requirements collected! You can now generate documentation.")
                                    if data.get("collected_requirements"):
                                        with st.expander("📋 Collected Requirements"):
                                            st.markdown(data["collected_requirements"])
                                    st.rerun()
                                else:
                                    st.session_state["current_question"] = data.get("question")
                                    st.rerun()
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Failed to connect to API server. Make sure the server is running on http://localhost:8000")
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timeout. The server is taking too long to respond. Please try again or restart the API server.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                
                if skip_btn:
                    # Skip question (send empty answer)
                    with st.spinner("Skipping question..."):
                        try:
                            payload = {
                                "session_id": st.session_state["session_id"],
                                "answer": ""
                            }
                            resp = requests.post(CONV_CONTINUE_URL, json=payload, timeout=120)
                            
                            if resp.status_code == 200:
                                data = resp.json()
                                if data["conversation_complete"]:
                                    st.session_state["conversation_complete"] = True
                                    st.session_state["current_question"] = None
                                    st.rerun()
                                else:
                                    st.session_state["current_question"] = data.get("question")
                                    st.rerun()
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timeout. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    # Generate documentation after dialog completion
    if st.session_state["conversation_complete"]:
        st.subheader("🚀 Documentation Generation")
        
        if st.button("Generate Documentation", use_container_width=True, type="primary"):
            with st.spinner("Generating structure and documentation..."):
                try:
                    payload = {
                        "session_id": st.session_state["session_id"],
                        "force": False
                    }
                    resp = requests.post(CONV_GENERATE_URL, json=payload, timeout=120)
                    
                    if resp.status_code != 200:
                        st.error(f"❌ Error: {resp.status_code}")
                        st.code(resp.text[:500], language="text")
                    else:
                        data = resp.json()
                        
                        if data.get("outline"):
                            st.subheader("📋 Documentation Structure")
                            st.markdown(f"```markdown\n{data['outline']}\n```")
                        
                        if data.get("documentation"):
                            st.subheader("📄 Generated Document")
                            st.markdown(data["documentation"])
                        
                        st.success(data.get("message", "✅ Documentation generated!"))
                        
                        # Clear state for new dialog
                        st.session_state["session_id"] = None
                        st.session_state["current_question"] = None
                        st.session_state["conversation_answers"] = []
                        st.session_state["conversation_complete"] = False
                except requests.exceptions.ConnectionError:
                    st.error("❌ Failed to connect to API server.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Timeout. Generation takes too long.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ========== DIRECT MODE ==========
else:
    st.header("⚡ Direct Mode")
    st.info("Enter system description, and documentation will be generated immediately.")
    
    with st.form("doc_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            project_name = st.text_input(
                "Project name (optional):",
                placeholder="e.g., fintom8",
                value="fintom8"
            )
        
        with col2:
            st.write("")  # For alignment
            st.write("")  # For alignment
        
        user_input = st.text_area(
            "Describe the system or documentation request:",
            height=200,
            placeholder="e.g., Internal CRM system for sales department that integrates with ...\n\nOr detailed description of fintom8 project: technologies, architecture, functionality, API, database, etc.",
        )
        submitted = st.form_submit_button("Generate Documentation", use_container_width=True)
    
    if submitted:
        with st.spinner("Generating structure and documentation..."):
            try:
                payload = {
                    "query": user_input,
                    "project_name": project_name.strip() if project_name else None,
                    "session_id": st.session_state.get("session_id"),
                }
                resp = requests.post(API_URL, json=payload, timeout=120)
                
                # Check if response is successful
                if resp.status_code != 200:
                    st.error(f"❌ API Error: {resp.status_code}")
                    st.code(resp.text[:500], language="text")
                    st.stop()
                
                # Try to parse JSON
                try:
                    data = resp.json()
                except ValueError as e:
                    st.error(f"❌ Failed to parse JSON response")
                    st.code(f"Response text: {resp.text[:500]}", language="text")
                    st.stop()
                
                st.session_state["session_id"] = data.get("session_id")
                
                if data.get("outline"):
                    st.subheader("📋 Documentation Structure")
                    st.markdown(f"```markdown\n{data['outline']}\n```")
                
                if data.get("documentation"):
                    st.subheader("📄 Generated Document")
                    st.markdown(data["documentation"])
                
                st.success(data.get("message", "✅ Documentation generated!"))
                
            except requests.exceptions.ConnectionError:
                st.error("❌ Failed to connect to API server. Make sure the server is running on http://localhost:8000")
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout. Generation takes too long.")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Request error: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.exception(e)

st.caption("Backend: FastAPI + LangGraph, LLM: Gemini.")
