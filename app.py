from pathlib import Path
import streamlit as st
from rag.vectorstore import clear_collection
from rag.pipeline import add_pdf, ask

st.set_page_config(
    page_title="Research RAG Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Research RAG Assistant")
st.checkbox("🔍 Compare Selected Papers")
# -------------------------
# Configuration
# -------------------------
UPLOAD_FOLDER = Path("uploaded_papers")
UPLOAD_FOLDER.mkdir(exist_ok=True)

# Adjust this after testing


if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# SIDEBAR
# =========================
with st.sidebar:

    st.header("📂 Upload Papers")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:

            save_path = UPLOAD_FOLDER / uploaded_file.name

            if not save_path.exists():
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

            if uploaded_file.name not in st.session_state.processed_files:

                with st.spinner(f"Processing {uploaded_file.name}..."):
                    add_pdf(save_path)

                st.session_state.processed_files.add(uploaded_file.name)
                st.success(f"✓ {uploaded_file.name}")

            else:
                st.info(f"✓ {uploaded_file.name}")

    st.divider()

    papers = sorted(UPLOAD_FOLDER.glob("*.pdf"))

    selected_papers = []

    if papers:
      st.write("### 📄 Search In")

      for paper in papers:
        checked = st.checkbox(
            paper.name,
            value=True,
            key=f"paper_{paper.name}"
        )

        if checked:
            selected_papers.append(paper.name)
    

    else:
      st.info("No papers uploaded.")

    compare_mode = st.checkbox(
    "🔍 Compare Selected Papers",
    value=False,
)

    if compare_mode and len(selected_papers) != 2:
     st.warning("Select exactly two papers to compare.")

    st.divider()

    if st.button("🗑️ Delete All", use_container_width=True):

        clear_collection()          # Delete vectors from Qdrant

        for pdf in UPLOAD_FOLDER.glob("*.pdf"):
            pdf.unlink()

        st.session_state.clear()
        st.success("All papers deleted.")
        st.rerun()

# =========================
# CHAT
# =========================

st.subheader("💬 Ask Questions")

# Display previous chat
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            with st.expander("📚 Sources"):

                for i, source in enumerate(message["sources"], 1):

                    st.write(f"**Source {i}:** {source['paper']}")

                    if "rerank_score" in source:
                        st.write(
                            f"Score: {source['rerank_score']:.3f}"
                        )

                    st.write(source["text"])
                    st.divider()
# Chat input
question = st.chat_input("Ask a question about your papers...")

GENERAL_RESPONSES = {
    "who are you":
        "I'm your Research RAG Assistant. I answer questions based on the research papers you upload.",
    "what are you":
        "I'm a Research RAG Assistant designed to answer questions using the uploaded research papers.",
    "introduce yourself":
        "I'm your Research RAG Assistant. Upload one or more research papers, select which ones to search, and I'll answer questions based only on their contents.",
    "tell me about yourself":
        "I'm your Research RAG Assistant. My purpose is to help you explore and understand the research papers you upload.",
}

if question:

    q = question.lower().strip()

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        # Built-in assistant questions
        if q in GENERAL_RESPONSES:

            answer = GENERAL_RESPONSES[q]
            valid_sources = []

        else:

            papers = sorted(UPLOAD_FOLDER.glob("*.pdf"))

            if not papers:
                st.warning("Please upload at least one paper first.")
                st.stop()

            if not selected_papers:
                st.warning("Please select at least one paper.")
                st.stop()

            spinner_text = (
    "Comparing papers..."
    if compare_mode
    else "Searching papers..."
)

            with st.spinner(spinner_text):

   
                answer, sources = ask(
    question,
    filenames=selected_papers,
    compare=compare_mode
)
            valid_sources = sources

        st.markdown(answer)

        if valid_sources:
            with st.expander("📚 Sources"):
                for i, source in enumerate(valid_sources, 1):
                    st.write(f"**Source {i}:** {source['paper']}")

                    if "rerank_score" in source:
                        st.write(
                            f"Score: {source['rerank_score']:.3f}"
                        )

                    st.write(source["text"])
                    st.divider()

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": valid_sources,
    })