# app.py
import streamlit as st
import time
from utils.llm_client import LLMClient
from utils.pdf_extractor import DocumentExtractor
from config import Config

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = ""
if 'document_stats' not in st.session_state:
    st.session_state.document_stats = {}
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


def main():
    """Main application function"""

    # Header
    st.title("📄 " + Config.APP_TITLE)
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")

        # Model selection
        selected_model = st.selectbox(
            "Select LLM Model:",
            Config.AVAILABLE_MODELS,
            index=0,
            help="Choose the language model for text processing"
        )

        # API status check
        st.header("🔗 API Status")
        if st.button("Test API Connection"):
            with st.spinner("Testing API connection..."):
                llm = LLMClient()
                success, response = llm.test_connection()
                if success:
                    st.success("✅ API Connected Successfully!")
                    st.write(f"Response: {response}")
                else:
                    st.error("❌ API Connection Failed")
                    st.write(f"Error: {response}")

        # File upload statistics
        if st.session_state.document_stats:
            st.header("📊 Document Statistics")
            stats = st.session_state.document_stats
            st.metric("Characters", stats.get('character_count', 0))
            st.metric("Words", stats.get('word_count', 0))
            st.metric("Lines", stats.get('line_count', 0))

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📁 Document Upload & Processing")

        # File uploader
        uploaded_file = st.file_uploader(
            "Upload your document:",
            type=Config.SUPPORTED_FILE_TYPES,
            help=f"Supported formats: {', '.join(Config.SUPPORTED_FILE_TYPES).upper()}"
        )

        if uploaded_file is not None:
            # Display file info
            st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

            # Extract text button
            if st.button("🔍 Extract Text", type="primary"):
                with st.spinner("Extracting text from document..."):
                    extractor = DocumentExtractor()

                    # Get file type
                    file_type = uploaded_file.name.split('.')[-1].lower()

                    # Extract text
                    success, text, error = extractor.extract_text_from_file(
                        file_content=uploaded_file.read(),
                        file_type=file_type
                    )

                    if success:
                        st.session_state.extracted_text = text
                        st.session_state.document_stats = extractor.get_text_stats(text)
                        st.success("✅ Text extracted successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Extraction failed: {error}")

        # Display extracted text
        if st.session_state.extracted_text:
            st.subheader("📄 Extracted Text")

            # Text preview with scroll
            with st.expander("View Full Text", expanded=False):
                st.text_area(
                    "Document Content:",
                    value=st.session_state.extracted_text,
                    height=300,
                    disabled=True
                )

            # Text summary section
            st.subheader("📝 Generate Summary")

            # Summary options
            summary_length = st.slider(
                "Summary Length (words):",
                min_value=50,
                max_value=500,
                value=200,
                step=50
            )

            if st.button("✨ Generate Summary", type="secondary"):
                with st.spinner("Generating summary..."):
                    llm = LLMClient()
                    summary = llm.summarize_text(
                        st.session_state.extracted_text,
                        max_length=summary_length
                    )

                    if "❌" not in summary:
                        st.success("📋 Summary Generated:")
                        st.write(summary)

                        # Add to chat history
                        st.session_state.chat_history.append({
                            "type": "summary",
                            "content": summary,
                            "timestamp": time.strftime("%H:%M:%S")
                        })
                    else:
                        st.error(f"Summary generation failed: {summary}")

    with col2:
        st.header("💬 Document Q&A")

        if st.session_state.extracted_text:
            # Question input
            user_question = st.text_input(
                "Ask a question about the document:",
                placeholder="e.g., What are the main points discussed in this document?"
            )

            if st.button("🤔 Ask Question") and user_question:
                with st.spinner("Processing your question..."):
                    llm = LLMClient()
                    answer = llm.answer_question(
                        st.session_state.extracted_text,
                        user_question
                    )

                    if "❌" not in answer:
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "type": "qa",
                            "question": user_question,
                            "answer": answer,
                            "timestamp": time.strftime("%H:%M:%S")
                        })
                        st.rerun()
                    else:
                        st.error(f"Failed to generate answer: {answer}")

            # Chat history
            if st.session_state.chat_history:
                st.subheader("💭 Chat History")

                # Clear chat history button
                if st.button("🗑️ Clear History"):
                    st.session_state.chat_history = []
                    st.rerun()

                # Display chat history
                for i, entry in enumerate(reversed(st.session_state.chat_history)):
                    with st.expander(f"💬 {entry['timestamp']} - {entry['type'].title()}", expanded=(i == 0)):
                        if entry['type'] == 'summary':
                            st.write("**📋 Summary:**")
                            st.write(entry['content'])
                        elif entry['type'] == 'qa':
                            st.write(f"**❓ Question:** {entry['question']}")
                            st.write(f"**💡 Answer:** {entry['answer']}")
        else:
            st.info("📤 Please upload and extract text from a document first to start asking questions.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray; padding: 20px;'>
            🎓 CS 590 Summer Project - LLM Document Summarization and Q&A System<br>
            Built with Streamlit & Together AI
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()