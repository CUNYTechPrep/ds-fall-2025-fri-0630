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
    return pipeline(
        "zero-shot-classification", 
        model="facebook/bart-large-mnli",
        device=0 if torch.cuda.is_available() else -1
    )

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
        height=300,
        placeholder="Enter the complete lyrics of the song you want to classify...",
        help="The more lyrics you provide, the better the classification will be!"
    )

with col2:
    # Classification section
    st.subheader("Genre Classification")
    
    # Define music genres for classification
    candidate_labels = ["rock", "pop", "hip hop", "country", "jazz", "classical", "R&B", "electronic", "folk", "blues"]
    
    # Button to classify
    classify_button = st.button(
        "🎯 Classify Genre",
        type="primary",
        use_container_width=True
    )
    
    # Classification logic
    if classify_button:
        if lyrics.strip():
            with st.spinner("🎵 Analyzing lyrics and predicting genre..."):
                # Perform zero-shot classification
                result = classifier(lyrics, candidate_labels, multi_label=False)
                
                # Display results
                st.success("✅ Classification Complete!")
                
                # Show top prediction
                st.write("### 🎸 Predicted Genre:")
                st.write(f"## **{result['labels'][0].upper()}**")
                st.write(f"Confidence: **{result['scores'][0]:.1%}**")
                
                # Show all predictions
                st.write("### 📊 All Genre Scores:")
                for label, score in zip(result['labels'][:5], result['scores'][:5]):
                    st.write(f"**{label.capitalize()}**: {score:.1%}")
                    st.progress(score)
        else:
            st.warning("Please enter some lyrics first!")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit 🚀 | Powered by facebook/bart-large-mnli")
