import streamlit as st
import pandas as pd
import gpt4all  # For running a local AI model
import tempfile
import os

# Load Local AI Model
model_path = "models/mistral-7b.gguf"  # Update with your model file path
model = gpt4all.GPT4All(model_path)

# Streamlit UI
st.title("📊 Athena")
st.write("Upload an Excel file, ask questions, and let AI help!")

# File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)  # Read Excel file
    st.write("📂 **Preview of Uploaded File:**", df.head())  # Show preview

    # User Input for AI Processing
    user_query = st.text_area("🔍 What do you want to do with this data?")

    if st.button("Process with AI"):
        if user_query:
            # Convert DataFrame to text for AI
            df_text = df.to_string()

            # Generate AI response
            prompt = f"Here is an Excel dataset:\n\n{df_text}\n\n{user_query}"
            response = model.generate(prompt)

            # Show AI response
            st.write("🤖 **AI Response:**", response)

        else:
            st.warning("Please enter a query.")

    # Download modified data
    if st.button("Download Modified File"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmpfile:
            df.to_excel(tmpfile.name, index=False)
            tmpfile.close()
            with open(tmpfile.name, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="modified_data.xlsx")
