import streamlit as st
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import requests
import io
import hashlib
import html

st.set_page_config(
    page_title="PDF RAG Assistant",
    page_icon="💙",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown(
    """
    <style>

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 4.2rem;
        padding-bottom: 4rem;
    }

    /* MAIN PAGE - follows Streamlit Light/Dark mode */

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                color-mix(in srgb, var(--primary-color) 11%, transparent),
                transparent 30%
            ),
            linear-gradient(
                180deg,
                color-mix(in srgb, var(--background-color) 96%, #2563eb 4%),
                var(--background-color)
            );
        color: var(--text-color);
    }

    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                color-mix(in srgb, var(--secondary-background-color) 92%, #2563eb 8%),
                var(--secondary-background-color)
            );
        border-right: 1px solid
            color-mix(in srgb, var(--primary-color) 20%, transparent);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem;
    }

    [data-testid="stSidebar"] p {
        color: var(--text-color);
        opacity: 0.88;
        line-height: 1.65;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--text-color);
        text-shadow:
            0 0 10px color-mix(
                in srgb,
                var(--primary-color) 22%,
                transparent
            );
    }

    /* MAIN TITLE */

    .main-title {
        font-size: 44px;
        font-weight: 760;
        letter-spacing: -1px;
        color: var(--text-color);
        margin-bottom: 6px;

        text-shadow:
            0 0 10px color-mix(
                in srgb,
                var(--primary-color) 22%,
                transparent
            ),
            0 0 25px color-mix(
                in srgb,
                var(--primary-color) 10%,
                transparent
            );
    }

    .subtitle {
        font-size: 17px;
        color: var(--text-color);
        opacity: 0.68;
        margin-bottom: 28px;
    }

    /* HOW IT WORKS */

    .info-card {
        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 92%,
                var(--primary-color) 8%
            );

        color: var(--text-color);

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 22%,
                transparent
            );

        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 24px;

        box-shadow:
            0 10px 28px rgba(0, 0, 0, 0.08),
            0 0 18px color-mix(
                in srgb,
                var(--primary-color) 6%,
                transparent
            );
    }

    .info-card b {
        color: var(--text-color);
        text-shadow:
            0 0 8px color-mix(
                in srgb,
                var(--primary-color) 18%,
                transparent
            );
    }

    /* ASK AI BUTTON */

    .stButton > button {
        background: linear-gradient(
            135deg,
            #1d4ed8,
            #2563eb
        );

        color: white !important;

        border: 1px solid rgba(147, 197, 253, 0.40);
        border-radius: 10px;

        padding: 0.55rem 1.10rem;

        font-weight: 650;

        box-shadow:
            0 0 13px rgba(37, 99, 235, 0.30),
            0 0 30px rgba(37, 99, 235, 0.10);

        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);

        border-color: rgba(147, 197, 253, 0.80);

        box-shadow:
            0 0 18px rgba(59, 130, 246, 0.45),
            0 0 36px rgba(37, 99, 235, 0.17);
    }

    /* QUESTION INPUT */

    .stTextInput input {
        background: var(--secondary-background-color) !important;
        color: var(--text-color) !important;

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 22%,
                transparent
            ) !important;

        border-radius: 9px !important;
    }

    .stTextInput input:focus {
        border-color: #3b82f6 !important;

        box-shadow:
            0 0 0 1px #3b82f6,
            0 0 14px rgba(59, 130, 246, 0.18) !important;
    }

    /* PDF UPLOAD */

    [data-testid="stFileUploader"] {
        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 94%,
                var(--primary-color) 6%
            );

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 18%,
                transparent
            );

        border-radius: 13px;

        padding-left: 14px;
        padding-right: 10px;
    }

    [data-testid="stFileUploaderDropzone"] {
        background: transparent;
        border-radius: 12px;

        padding-left: 16px !important;
    }

    [data-testid="stFileUploaderDropzone"] > div {
        padding-left: 7px;
    }

    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] p {
        color: var(--text-color) !important;
    }

    /* ANSWER CARD */

    .result-card {
        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 94%,
                var(--primary-color) 6%
            );

        color: var(--text-color);

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 20%,
                transparent
            );

        border-left: 3px solid #3b82f6;

        border-radius: 12px;

        padding: 18px 20px;

        margin-top: 10px;
        margin-bottom: 12px;

        line-height: 1.65;

        box-shadow:
            0 10px 26px rgba(0, 0, 0, 0.08);
    }

    /* SOURCE PAGE BADGES */

    .source-badge {
        display: inline-block;

        background:
            color-mix(
                in srgb,
                var(--primary-color) 13%,
                var(--secondary-background-color)
            );

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 24%,
                transparent
            );

        color: var(--text-color);

        padding: 5px 9px;

        border-radius: 999px;

        margin-right: 6px;
        margin-top: 4px;

        font-size: 12px;
    }

    /* MADE BY BUSE */

    .made-by-buse {
        position: fixed;

        top: 66px;
        right: 26px;

        z-index: 999;

        font-size: 12px;

        color: var(--text-color);

        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 90%,
                var(--primary-color) 10%
            );

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 20%,
                transparent
            );

        padding: 6px 11px;

        border-radius: 999px;

        backdrop-filter: blur(8px);

        box-shadow:
            0 4px 16px rgba(0, 0, 0, 0.10),
            0 0 13px color-mix(
                in srgb,
                var(--primary-color) 9%,
                transparent
            );
    }

    /* HEADINGS */

    h1, h2, h3 {
        color: var(--text-color);
    }

    h2, h3 {
        text-shadow:
            0 0 8px color-mix(
                in srgb,
                var(--primary-color) 11%,
                transparent
            );
    }

    /* RETRIEVED TEXT */

    [data-testid="stExpander"] {
        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 96%,
                var(--primary-color) 4%
            );

        border: 1px solid
            color-mix(
                in srgb,
                var(--primary-color) 16%,
                transparent
            );

        border-radius: 11px;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    hr {
        border-color:
            color-mix(
                in srgb,
                var(--primary-color) 14%,
                transparent
            );
    }

    footer {
        visibility: hidden;
    }

    </style>

    <div class="made-by-buse">
        Made by Buse 💙
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- HEADER ----------
st.markdown(
    '<div class="main-title">💙 PDF Question Answering Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Ask questions about a PDF using Retrieval-Augmented Generation (RAG).</div>',
    unsafe_allow_html=True
)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("About")
    st.write(
        "This application retrieves relevant information from a PDF "
        "and uses a local language model to generate an answer."
    )

    st.subheader("Technologies")
    st.write("• Python")
    st.write("• Streamlit")
    st.write("• PyPDF")
    st.write("• Sentence Transformers")
    st.write("• FAISS")
    st.write("• Ollama")
    st.write("• Qwen 2.5")

    st.subheader("RAG Pipeline")
    st.write("PDF → Text → Chunks → Embeddings → Retrieval → LLM → Answer")


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


embedding_model = load_embedding_model()


# ---------- PDF PROCESSING ----------
def process_pdf(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))

    chunks = []
    chunk_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if not text:
            continue

        words = text.split()

        chunk_size = 200
        overlap = 40
        start = 0

        while start < len(words):
            chunk = " ".join(words[start:start + chunk_size])

            if chunk.strip():
                chunks.append(chunk)
                chunk_pages.append(page_number)

            start += chunk_size - overlap

    return chunks, chunk_pages


# ---------- VECTOR STORE ----------
def create_vector_store(chunks):
    embeddings = embedding_model.encode(
        chunks,
        batch_size=64,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    ).astype("float32")

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    return index


# ---------- RETRIEVAL ----------
def retrieve_chunks(question, chunks, chunk_pages, index, k=4):
    question_embedding = embedding_model.encode(
        [question],
        convert_to_numpy=True,
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(question_embedding, k)

    results = []

    for i in indices[0]:
        if 0 <= i < len(chunks):
            results.append({
                "text": chunks[i],
                "page": chunk_pages[i]
            })

    return results


# ---------- OLLAMA ----------
def ask_ollama(question, context):
    prompt = f"""
Answer the question using only the PDF context below.

Do not add information that is not supported by the context.

If the answer is not available in the context, say:
"I could not find this information in the document."

Context:
{context}

Question:
{question}

Answer:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:1.5b",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]


# ---------- HOW IT WORKS ----------
st.markdown(
    """
    <div class="info-card">
        <b>How it works</b><br><br>
        1. Upload a PDF.<br>
        2. The PDF is split into smaller text chunks.<br>
        3. The system retrieves the most relevant chunks for your question.<br>
        4. A local language model generates an answer using those chunks.
    </div>
    """,
    unsafe_allow_html=True
)


# ---------- UPLOAD ----------
uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type=["pdf"]
)

if uploaded_file:
    pdf_bytes = uploaded_file.getvalue()
    file_id = hashlib.md5(pdf_bytes).hexdigest()

    if st.session_state.get("file_id") != file_id:
        with st.spinner("Processing PDF..."):
            chunks, chunk_pages = process_pdf(pdf_bytes)

            if len(chunks) == 0:
                st.error("No readable text was found in this PDF.")
                st.stop()

            index = create_vector_store(chunks)

            st.session_state.file_id = file_id
            st.session_state.chunks = chunks
            st.session_state.chunk_pages = chunk_pages
            st.session_state.index = index

    chunks = st.session_state.chunks
    chunk_pages = st.session_state.chunk_pages
    index = st.session_state.index

    st.success(
        f"PDF processed successfully. {len(chunks)} text chunks created."
    )

    question = st.text_input(
        "Ask a question about the PDF:"
    )

    if st.button("Ask AI") and question:
        with st.spinner("Searching the PDF..."):
            results = retrieve_chunks(
                question,
                chunks,
                chunk_pages,
                index
            )

            context = "\n\n".join(
                f"[Page {item['page']}]\n{item['text']}"
                for item in results
            )

        with st.spinner("Generating answer..."):
            try:
                answer = ask_ollama(
                    question,
                    context
                )

                st.subheader("Answer")

                safe_answer = html.escape(answer).replace("\n", "<br>")

                st.markdown(
                    f'<div class="result-card">{safe_answer}</div>',
                    unsafe_allow_html=True
                )

                pages = sorted(
                    set(item["page"] for item in results)
                )

                st.markdown("**Retrieved source pages**")

                badge_html = "".join(
                    f'<span class="source-badge">Page {page}</span>'
                    for page in pages
                )

                st.markdown(
                    badge_html,
                    unsafe_allow_html=True
                )

                st.write("")

                with st.expander("View retrieved text"):
                    for item in results:
                        st.markdown(
                            f"### Page {item['page']}"
                        )

                        st.write(item["text"])
                        st.divider()

            except requests.exceptions.RequestException:
                st.error(
                    "Could not connect to Ollama. Make sure Ollama is running."
                )

else:
    st.info("Upload a PDF to begin.")