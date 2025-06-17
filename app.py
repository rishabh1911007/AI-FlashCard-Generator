# app.py

import streamlit as st
from file_handler import extract_text_from_pdf
from flashcard_generator import generate_flashcards
from utils import export_to_csv

st.set_page_config(page_title="AI Flashcard Generator", layout="centered")
st.title("🧠 AI Flashcard Generator")
st.markdown(
    "Generate flashcards instantly using AI - upload a PDF or paste your text directly.")

# Input method selection
input_method = st.radio(
    "Choose your input method:",
    ["📄 Upload PDF", "📝 Paste Text"],
    horizontal=True
)

# Difficulty selection
difficulty = st.selectbox("Select difficulty level",
                          ["Easy", "Medium", "Hard"])

# Initialize text variable
text = ""

# PDF Upload Section
if input_method == "📄 Upload PDF":
    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

    if uploaded_file:
        if st.button("Generate Flashcards from PDF", type="primary"):
            with st.spinner("Extracting content and generating flashcards..."):
                try:
                    text = extract_text_from_pdf(uploaded_file)

                    if not text or len(text.strip()) < 50:
                        st.error(
                            "⚠️ Insufficient text extracted from PDF. Please check if the PDF contains readable text.")
                        st.stop()

                    # Generate flashcards
                    flashcards = generate_flashcards(
                        text, difficulty=difficulty)

                    if flashcards and isinstance(flashcards, list) and len(flashcards) > 0:
                        st.success(
                            f"✅ {len(flashcards)} flashcards generated successfully!")

                        # Display flashcards in expandable format
                        st.subheader("📚 Your Flashcards")
                        for i, card in enumerate(flashcards, 1):
                            with st.expander(f"Flashcard {i} - {card.get('difficulty', 'Unknown')} Level"):
                                st.write(
                                    f"**❓ Question:** {card.get('question', 'No question')}")
                                st.write(
                                    f"**💡 Answer:** {card.get('answer', 'No answer')}")

                        # Download button
                        csv_data = export_to_csv(flashcards)
                        st.download_button(
                            "📥 Download as CSV",
                            csv_data,
                            file_name="flashcards.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(
                            "⚠️ No valid flashcards generated. Please try again.")

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# Text Input Section
else:  # Paste Text option
    st.subheader("📝 Paste Your Text")
    text_input = st.text_area(
        "Enter or paste your text here:",
        height=200,
        placeholder="Paste your study material, notes, or any text you want to convert into flashcards..."
    )

    if text_input:
        if st.button("Generate Flashcards from Text", type="primary"):
            with st.spinner("Generating flashcards..."):
                try:
                    if len(text_input.strip()) < 50:
                        st.error(
                            "⚠️ Please enter more text (at least 50 characters) to generate meaningful flashcards.")
                        st.stop()

                    # Generate flashcards
                    flashcards = generate_flashcards(
                        text_input, difficulty=difficulty)

                    if flashcards and isinstance(flashcards, list) and len(flashcards) > 0:
                        st.success(
                            f"✅ {len(flashcards)} flashcards generated successfully!")

                        # Display flashcards in expandable format
                        st.subheader("📚 Your Flashcards")
                        for i, card in enumerate(flashcards, 1):
                            with st.expander(f"Flashcard {i} - {card.get('difficulty', 'Unknown')} Level"):
                                st.write(
                                    f"**❓ Question:** {card.get('question', 'No question')}")
                                st.write(
                                    f"**💡 Answer:** {card.get('answer', 'No answer')}")

                        # Download button
                        csv_data = export_to_csv(flashcards)
                        st.download_button(
                            "📥 Download as CSV",
                            csv_data,
                            file_name="flashcards.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error(
                            "⚠️ No valid flashcards generated. Please try again.")

                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")

# Instructions
st.markdown("---")
st.markdown("""
### 📋 How to Use:
1. **Choose your input method** - Upload a PDF or paste text directly
2. **Select difficulty level** - Easy, Medium, or Hard
3. **Generate flashcards** - Click the button to create your study cards
4. **Review and download** - Expand each flashcard to review, then download as CSV

### 💡 Tips:
- For PDFs: Make sure your PDF contains selectable text (not just images)
- For text input: Include at least 50 characters for meaningful flashcards
- The AI will generate 3-5 flashcards based on your content
- Higher difficulty levels create more analytical questions
""")

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ using Streamlit and AI*")
