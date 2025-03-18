import streamlit as st
import pandas as pd
import gpt4all
import sqlite3
import tempfile
import os

# Load Local AI Model
model_path = "models/mistral-7b.gguf"  # Update with your model path
model = gpt4all.GPT4All(model_path)

# Connect to SQLite database
conn = sqlite3.connect("ai_memory.db")
cursor = conn.cursor()

# Create table for memory (queries & responses)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT UNIQUE,
        response TEXT,
        feedback TEXT DEFAULT NULL
    )
""")
conn.commit()

# Streamlit UI
st.title("🤖 Athena - Your AI Excel Assistant")
st.write("Upload an Excel file, ask questions, and let Athena help!")

# File Upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xls", "xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("📂 **Preview of Uploaded File:**", df.head())

    user_query = st.text_area("🔍 What do you want to do with this data?")

    if st.button("Process with Athena"):
        if user_query:
            # Check if query is in memory
            cursor.execute("SELECT response, feedback FROM memory WHERE query = ?", (user_query,))
            stored_data = cursor.fetchone()

            if stored_data:
                response, feedback = stored_data
                st.success("✅ Retrieved from memory!")
            else:
                df_text = df.to_string()
                prompt = f"Here is an Excel dataset:\n\n{df_text}\n\n{user_query}"
                response = model.generate(prompt)

                # Store new response in memory
                cursor.execute("INSERT INTO memory (query, response) VALUES (?, ?)", (user_query, response))
                conn.commit()
            
            st.write("🤖 **Athena's Response:**", response)

            # Feedback buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Good Response"):
                    cursor.execute("UPDATE memory SET feedback = ? WHERE query = ?", ("good", user_query))
                    conn.commit()
                    st.success("Thanks for your feedback!")

            with col2:
                if st.button("👎 Bad Response"):
                    st.warning("Please provide a better response:")
                    corrected_response = st.text_area("Enter a better response")

                    if st.button("Save Correction"):
                        cursor.execute("UPDATE memory SET response = ?, feedback = ? WHERE query = ?",
                                       (corrected_response, "corrected", user_query))
                        conn.commit()
                        st.success("Correction saved! Athena will remember this.")

    if st.button("Download Modified File"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmpfile:
            df.to_excel(tmpfile.name, index=False)
            tmpfile.close()
            with open(tmpfile.name, "rb") as f:
                st.download_button("📥 Download Excel", f, file_name="modified_data.xlsx")

# Close database connection when app stops
conn.close()
