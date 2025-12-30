#!/bin/bash

# Script to run Streamlit application

cd "$(dirname "$0")" || exit

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit is not installed. Installing..."
    pip install streamlit
fi

# Run Streamlit app
streamlit run ui/streamlit_app.py




