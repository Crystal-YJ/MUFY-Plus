import streamlit as st
import string
import re

st.set_page_config(page_title="Text Summarizer & Notes Extractor", layout="centered")

def split_sentences(text):
    # Split text into sentences using punctuation marks.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def word_freq(text):
    # Count word frequency excluding punctuation
    translator = str.maketrans('', '', string.punctuation)
    words = text.lower().translate(translator).split()
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq

def score_sentences(sentences, freq):
    # Score sentences based on frequency of words
    scores = {}
    for s in sentences:
        score = 0
        for w in s.lower().split():
            score += freq.get(w, 0)
        scores[s] = score
    return scores

# Sidebar Instructions
with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. Paste or type your text into the main input box.
    2. Click **Summarize and Extract Notes**.
    3. View the concise summary and key important points.
    4. Use the **Clear** button to reset the input.
    """)

st.title("📝 Text Summarizer & Important Notes Extractor")

text = st.text_area("Enter your text below:", height=300, placeholder="Paste your text here...")

col1, col2 = st.columns([1,1])

with col1:
    summarize_btn = st.button("✅ Summarize and Extract Notes")

with col2:
    clear_btn = st.button("🗑️ Clear Text")

if clear_btn:
    text = ""
    st.experimental_rerun()

if summarize_btn:
    if not text.strip():
        st.warning("⚠️ Please enter some text to summarize.")
    else:
        sentences = split_sentences(text)
        freq = word_freq(text)
        scores = score_sentences(sentences, freq)

        # Get top 3 sentences for summary
        summary_sentences = sorted(scores, key=scores.get, reverse=True)[:3]
        summary = " ".join(summary_sentences)

        # Get top 5 sentences for notes
        notes_sentences = sorted(scores, key=scores.get, reverse=True)[:5]

        st.markdown("---")
        st.subheader("📝 Summary")
        st.write(summary)

        st.subheader("📌 Important Points / Notes")
        for idx, note in enumerate(notes_sentences, 1):
            st.markdown(f"{idx}. {note}")

# Footer spacing
st.markdown("<br><br>", unsafe_allow_html=True)
