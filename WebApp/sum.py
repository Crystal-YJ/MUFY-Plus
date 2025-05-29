import streamlit as st
import urllib.request
import re
import random
from PIL import Image, ImageDraw, ImageFont
import io
from collections import Counter

st.set_page_config(page_title="Structured Notes", layout="centered")

# --- Helper Functions ---
def fetch_url_text(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        paragraphs = re.findall(r'<p.*?>(.*?)</p>', html, re.DOTALL | re.IGNORECASE)
        clean_paragraphs = [re.sub(r'<.*?>', '', p).strip() for p in paragraphs]
        text = ' '.join(clean_paragraphs)
        return text
    except Exception:
        return None

def clean_text(text):
    text = re.sub(r'\[[^\]]*\]', '', text)  # Remove bracketed references
    text = re.sub(r'http\S+\.(jpg|jpeg|png|gif|svg)', '', text, flags=re.IGNORECASE)  # Remove image URLs
    text = re.sub(r'http\S+', '', text)  # Remove other URLs
    text = re.sub(r'www\S+', '', text)
    text = re.sub(r'\b(image|photo|picture|fig|figure|chart|diagram)\b[^.]*\.', '', text, flags=re.IGNORECASE)  # Remove image sentences
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s.,!?\'-]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\xa0', ' ')
    return text.strip()

def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip().split()) > 5]

def get_top_keywords(sentences, num_keywords=10):
    all_words = ' '.join(sentences).lower().split()
    stop_words = set(["the", "and", "for", "are", "was", "were", "that", "with", "this", "from", "which", "their"])
    keywords = [word for word in all_words if word.isalpha() and word not in stop_words]
    return [w for w, _ in Counter(keywords).most_common(num_keywords)]

def extract_by_keywords(sentences, keywords, used, max_per_section=5):
    results = []
    for s in sentences:
        if s in used:
            continue
        if any(k in s.lower() for k in keywords):
            results.append(s)
            used.add(s)
        if len(results) >= max_per_section:
            break
    return results

def text_to_image(text, font_size=20, padding=20):
    font = ImageFont.load_default()
    lines = text.split('\n')
    dummy_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    widths = [draw.textbbox((0, 0), line, font=font)[2] for line in lines]
    width = max(widths) + 2 * padding
    height = (font_size + 6) * len(lines) + 2 * padding
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    y = padding
    for line in lines:
        draw.text((padding, y), line, fill="black", font=font)
        y += font_size + 6
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

# --- UI ---
st.title("\U0001F9E0 Structured Note Extractor")

tab1, tab2 = st.tabs(["\U0001F4C4 Paste Text", "\U0001F310 From Website"])

with tab1:
    text = st.text_area("Paste your text here:", height=300, value=st.session_state.get('text', ''))

with tab2:
    url = st.text_input("Enter a webpage URL to summarize:", value=st.session_state.get('url', ''))

col1, col2 = st.columns([1, 1])
with col1:
    summarize_btn = st.button("✅ Summarize")
with col2:
    clear_btn = st.button("🗑️ Clear")

if clear_btn:
    for k in ["text", "url", "quiz_items", "recall_sentences"]:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state.clear()
    st.experimental_set_query_params()
    st.stop()

if summarize_btn:
    if url:
        st.info("\U0001F50D Fetching webpage...")
        raw_text = fetch_url_text(url)
        if not raw_text:
            st.error("❌ Failed to fetch or parse the URL.")
        else:
            raw_text = clean_text(raw_text)
            st.session_state.text = raw_text
            st.session_state.url = url
            st.success("✅ Website content loaded and cleaned.")
    elif text.strip():
        st.session_state.text = clean_text(text)
        st.session_state.url = url
    else:
        st.warning("⚠️ Please enter some text or URL.")

if 'text' in st.session_state:
    raw_text = st.session_state.text
    sentences = split_sentences(raw_text)

    used_sentences = set()
    top_keywords = get_top_keywords(sentences, num_keywords=12)
    sections = [top_keywords[i:i + 3] for i in range(0, len(top_keywords), 3)]

    st.subheader("\U0001F4DA Notes Overview")

    col1, col2 = st.columns(2)
    for i, keywords in enumerate(sections):
        section_label = f"📓 Section {i + 1}"
        column = col1 if i % 2 == 0 else col2
        with column:
            with st.expander(section_label):
                items = extract_by_keywords(sentences, keywords, used_sentences)
                for item in items:
                    st.markdown(f"- {item}")

    with st.expander("\U0001F9FE Full Cleaned Text"):
        st.write(raw_text)

    # --- Typing Recall Test ---
    st.subheader("⌨️ Typing Recall Test")

    all_notes = list(used_sentences)
    random.shuffle(all_notes)

    if 'recall_sentences' not in st.session_state:
        st.session_state.recall_sentences = all_notes[:5]

    for idx, sentence in enumerate(st.session_state.recall_sentences):
        with st.expander(f"📝 Test {idx + 1}", expanded=False):
            key_prefix = f"recall_{idx}"

            show_key = f"show_image_{idx}"
            allow_key = f"allow_typing_{idx}"

            if show_key not in st.session_state:
                st.session_state[show_key] = False
            if allow_key not in st.session_state:
                st.session_state[allow_key] = False

            show = st.session_state[show_key]
            allow_typing = st.session_state[allow_key]

            show_clicked = st.button("Show Sentence", key=f"show_btn_{idx}")
            hide_clicked = st.button("Hide", key=f"hide_btn_{idx}")

            if show_clicked:
                st.session_state[show_key] = True
                st.session_state[allow_key] = False
                show = True
                allow_typing = False

            if hide_clicked:
                st.session_state[show_key] = False
                st.session_state[allow_key] = True
                show = False
                allow_typing = True

            if show:
                image_bytes = text_to_image(sentence, font_size=24)
                st.image(image_bytes, use_container_width=False, caption="Memorize and click Hide to proceed.")

            if allow_typing:
                user_input = st.text_area("Type from memory:", key=f"typed_{idx}")
                if st.button("Check Answer", key=f"check_{idx}"):
                    original = sentence.strip().lower()
                    typed = user_input.strip().lower()
                    if typed == original:
                        st.success("✅ Perfect recall!")
                    elif original in typed or typed in original:
                        st.warning("🟡 Almost correct!")
                    else:
                        st.error("❌ Keep practicing!")
