import streamlit as st
from transformers import pipeline
import torch

# Set page config
st.set_page_config(
    page_title="Music Genre Guesser",
    page_icon="🎵",
    layout="wide"
)

# Load the BART model for zero-shot classification
@st.cache_resource
def load_model():
    """Load the facebook/bart-large-mnli model for zero-shot classification"""
    return pipeline("zero-shot-classification", 
                   model="facebook/bart-large-mnli", 
                   device=0 if torch.cuda.is_available() else -1)

# Load the model
with st.spinner("Loading AI model... This may take a moment on first run."):
    classifier = load_model()

# Title
st.title("🎵 Music Genre Guesser")
st.markdown("Enter song lyrics below and let our AI guess the music genre!")

# Create two columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    # Text input for lyrics
    st.subheader("Enter Song Lyrics")
    lyrics = st.text_area(
        "Paste the song lyrics here:",
        height=200,
        placeholder="Enter the complete lyrics of the song you want to classify...",
        help="The more lyrics you provide, the better the classification will be!"
    )

with col2:
    # Classification section
    st.subheader("Genre Classification")
    
    # Button to classify
    classify_button = st.button(
        "🎯 Classify Genre",
        type="primary",
        use_container_width=True
    )
    
    # Genre classification logic
    if classify_button:
        if lyrics.strip():
            with st.spinner("🎵 Analyzing lyrics with AI..."):
                # Define music genres for classification
                music_genres = [
                    "Rock", "Pop", "Hip-Hop", "Electronic", "Country", 
                    "Jazz", "Classical", "R&B", "Reggae", "Blues", 
                    "Folk", "Metal", "Punk", "Alternative", "Indie"
                ]
                
                # Perform zero-shot classification
                result = classifier(lyrics, music_genres)
                
                st.success("🎉 Classification complete!")
                
                # Display results
                st.subheader("🎵 Genre Predictions:")
                
                # Show top 3 predictions
                for i, (genre, score) in enumerate(zip(result['labels'][:3], result['scores'][:3])):
                    confidence = score * 100
                    emoji_map = {
                        "Rock": "🎸", "Pop": "🎵", "Hip-Hop": "🎤", "Electronic": "🎹",
                        "Country": "🎻", "Jazz": "🎺", "Classical": "🎼", "R&B": "🎤",
                        "Reggae": "🌴", "Blues": "🎸", "Folk": "🪕", "Metal": "🤘",
                        "Punk": "⚡", "Alternative": "🎸", "Indie": "🎵"
                    }
                    emoji = emoji_map.get(genre, "🎵")
                    st.write(f"{emoji} **{genre}** ({confidence:.1f}% confidence)")
                
                # Show a progress bar for the top prediction
                top_score = result['scores'][0] * 100
                st.progress(top_score / 100)
                st.caption(f"Confidence in top prediction: {top_score:.1f}%")
        else:
            st.warning("⚠️ Please enter some lyrics first!")

# Footer
st.markdown("---")
st.markdown("### How it works:")
st.markdown("1. 📝 Enter song lyrics in the text box")
st.markdown("2. 🎯 Click the 'Classify Genre' button")
st.markdown("3. 🎵 Get instant genre predictions with confidence scores")

# Sidebar for additional info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This Music Genre Guesser uses Facebook's BART-large-MNLI model 
    for zero-shot classification to analyze song lyrics and predict 
    the most likely music genre.
    
    **Supported Genres:**
    - 🎸 Rock
    - 🎵 Pop  
    - 🎤 Hip-Hop
    - 🎹 Electronic
    - 🎻 Country
    - 🎺 Jazz
    - 🎼 Classical
    - 🎤 R&B
    - 🌴 Reggae
    - 🎸 Blues
    - 🪕 Folk
    - 🤘 Metal
    - ⚡ Punk
    - 🎸 Alternative
    - 🎵 Indie
    """)
    
    st.markdown("---")
    st.markdown("**Powered by:** Facebook BART-large-MNLI")
    st.markdown("**Model Type:** Zero-shot Classification")
    st.markdown("**AI Capability:** Advanced natural language understanding")
