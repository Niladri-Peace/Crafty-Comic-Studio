import streamlit as st
import os
import random
import base64
from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer
from BACKEND import generate_panels, generate_image, process_comic

def image_to_base64(img):
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

PANEL_FOLDER = "PANEL_IMAGES"
OUTPUT_FOLDER = "OUTPUT"

os.makedirs(PANEL_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

STYLE_DESCRIPTIONS = {
    "Manga": "High-contrast black and white sketch with sharp, clean lines, exaggerated facial expressions, and dramatic shading. No bright colors, only grayscale tones",
    "American": "Bold outlines with heavy inking, bright and saturated colors, and exaggerated muscular features. Classic superhero comic book style",
    "Anime": "Vibrant colors with smooth cel shading, large expressive eyes, and detailed hair. Dynamic action poses with fluid motion lines",
    "Belgian": "Clean, clear lines with soft, flat shading. Rich and detailed backgrounds in a semi-realistic style, inspired by Tintin comics",
}

SURPRISE_PROMPTS = [
    "A robot chef competing in a cooking competition against humans",
    "A time-traveling cat accidentally brings a dinosaur to modern-day Tokyo",
    "A superhero who loses their powers every time they sneeze",
    "Two rival wizards accidentally swap their magic wands at a coffee shop",
    "A detective solving mysteries in a city where everyone can read minds except them",
    "An alien trying to understand human emotions by watching romantic comedies",
    "A dragon who's afraid of fire and wants to become a librarian",
    "A group of pirates searching for treasure but they're all terrible at reading maps",
]

st.set_page_config(page_title="CraftyComic Ink", page_icon="🎨", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #2d3748;
        padding: 2rem 1rem;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        color: white;
    }
    
    .main {
        background-color: #f7fafc;
    }
    
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    .style-card {
        border: 3px solid transparent;
        border-radius: 12px;
        padding: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .style-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .style-card.selected {
        border-color: #3182ce;
        box-shadow: 0 4px 16px rgba(49,130,206,0.3);
    }
    
    .style-card-img {
        width: 100%;
        height: 100px;
        border-radius: 8px;
        object-fit: cover;
        margin-bottom: 8px;
    }
    
    .style-card-label {
        font-weight: 600;
        font-size: 14px;
        color: #2d3748;
    }
    
    .description-box {
        background: #ebf8ff;
        border-left: 4px solid #3182ce;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .description-title {
        font-weight: 600;
        color: #2c5282;
        margin-bottom: 0.5rem;
    }
    
    .description-text {
        color: #2d3748;
        line-height: 1.6;
    }
    
    .stTextArea textarea {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        font-size: 15px;
        padding: 12px;
    }
    
    .stTextArea textarea:focus {
        border-color: #3182ce;
        box-shadow: 0 0 0 3px rgba(49,130,206,0.1);
    }
    
    .stSlider {
        padding: 0.5rem 0;
    }
    
    .stSlider > div > div > div {
        background-color: #e2e8f0;
    }
    
    .surprise-btn {
        position: absolute;
        right: 10px;
        top: 10px;
        background: white;
        border: 2px solid #e2e8f0;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 13px;
        font-weight: 500;
        color: #4a5568;
        transition: all 0.3s ease;
    }
    
    .surprise-btn:hover {
        border-color: #3182ce;
        color: #3182ce;
    }
    
    .stButton button {
        background: #3182ce;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: #2c5282;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(49,130,206,0.3);
    }
    
    .stSlider {
        padding: 1rem 0;
    }
    
    h1 {
        color: #1a202c;
        font-weight: 700;
    }
    
    .section-label {
        color: #e53e3e;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('''
        <div style="display: flex; align-items: center; gap: 10px; padding: 1rem 0; border-bottom: 1px solid #4a5568;">
            <span style="font-size: 28px; flex-shrink: 0;">🎨</span>
            <h2 style="color: white; margin: 0; font-size: 17px; font-weight: 600; white-space: nowrap;">CraftyComic Ink</h2>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<p style="color: #cbd5e0; font-size: 13px; margin-top: 1.5rem; margin-bottom: 1rem;">Generate your story prompt</p>', unsafe_allow_html=True)
    
    st.markdown('''
        <div style="background: #4a5568; padding: 10px 12px; border-radius: 6px; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">📚</span>
            <span style="color: white; font-weight: 600; font-size: 14px;">Craft Your Story</span>
        </div>
    ''', unsafe_allow_html=True)
    
    search_input = st.text_input(
        "Search",
        placeholder="",
        label_visibility="collapsed",
        key="sidebar_search"
    )
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    
    st.markdown('''
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.75rem;">
            <span style="font-size: 16px;">✨</span>
            <span style="color: white; font-weight: 600; font-size: 14px;">Finert Your Riasios</span>
        </div>
    ''', unsafe_allow_html=True)
    
    character_desc = st.text_input(
        "Character Description",
        placeholder="Main Character Description (Optional)",
        label_visibility="collapsed",
        key="character_input"
    )

# Default layout to 3x2 Grid
layout_choice = "3x2 Grid (Classic Comic)"

col_logo, col_title = st.columns([1, 20])
with col_logo:
    st.markdown('<div style="font-size: 40px; line-height: 1; margin: 0; padding: 0;">🎨</div>', unsafe_allow_html=True)
with col_title:
    st.markdown('<h1 style="margin: 0; padding: 0; line-height: 1; display: flex; align-items: center; height: 40px;">CraftyComic Ink</h1>', unsafe_allow_html=True)

st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-label" style="margin-bottom: 1rem;">🎨 Craft Your Story</div>', unsafe_allow_html=True)

if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = ""
user_prompt = st.text_area("Story Prompt", value=st.session_state.user_prompt, height=100, placeholder="Enter your story prompt here...", label_visibility="collapsed", key="prompt_area")

st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-label" style="margin-bottom: 1rem;">🎨 Choose an art style</div>', unsafe_allow_html=True)

if 'selected_style' not in st.session_state:
    st.session_state.selected_style = "Manga"

cols = st.columns(4)
style_images = {
    "Manga": "SAMPLE_OUTPUT/MANGA.jpeg",
    "American": "SAMPLE_OUTPUT/AMERICAN.jpeg",
    "Anime": "SAMPLE_OUTPUT/ANIME.jpeg",
    "Belgian": "SAMPLE_OUTPUT/BELGIAN.jpeg",
}

for idx, (style_name, col) in enumerate(zip(STYLE_DESCRIPTIONS.keys(), cols)):
    with col:
        selected_class = "selected" if st.session_state.selected_style == style_name else ""
        try:
            full_img = Image.open(style_images[style_name])
            width, height = full_img.size
            panel_width = width // 2
            panel_height = height // 3
            single_panel = full_img.crop((panel_width, 0, width, panel_height))
            img_base64 = image_to_base64(single_panel)
            img_html = f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; max-height:130px; margin:auto; display:block; object-fit:contain; vertical-align:middle; border-radius:8px 8px 0 0; background:#fff;"/>'
        except Exception as e:
            img_html = '<div style="height: 110px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 8px;"></div>'
        if st.button(f"{style_name}", key=f"style_btn_{idx}_{style_name}", use_container_width=True):
            st.session_state.selected_style = style_name
            st.rerun()
        st.markdown(f'''
            <div class="style-card {selected_class}" style="margin-top: -45px; padding: 8px; box-sizing: border-box;">
                {img_html}
                <div class="style-card-label">{style_name}</div>
            </div>
        ''', unsafe_allow_html=True)

st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)

# Center the sliders in a 3-column layout
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    grit_level = st.slider("Grit vs. Clean", 0, 100, 50, help="Adjust the grittiness of the art style")
    tone_level = st.slider("Serious vs. Whimsical", 0, 100, 50, help="Adjust the tone of the story")

st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)

include_speech_bubbles = st.checkbox("✅ Include Speech Bubbles", value=True)

st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)

if st.button("🎨 Generate Comic", use_container_width=True, type="primary"):
    if user_prompt:
        # Build enhanced context with character description and mood
        grit_desc = "Clean and polished" if grit_level < 35 else ("Balanced style" if grit_level < 65 else "Gritty and rough")
        tone_desc = "Serious and dramatic" if tone_level < 35 else ("Balanced tone" if tone_level < 65 else "Whimsical and playful")
        
        enhanced_prompt = user_prompt
        if character_desc:
            enhanced_prompt = f"Main Character: {character_desc}. Story: {user_prompt}"
        enhanced_prompt += f" Style: {grit_desc}, {tone_desc}."
        
        with st.status("Creating your masterpiece...", expanded=True) as status:
            st.write("📝 Step 1: Brainstorming panel descriptions...")
            panel_data = generate_panels.generate_panels(enhanced_prompt, st.session_state.selected_style)
            
            st.write("🎨 Step 2: Drawing the artwork (this may take a moment)...")
            image_paths = list(generate_image.generate_images(panel_data, art_style=st.session_state.selected_style))
            
            st.write("📐 Step 3: Assembling the final comic layout...")
            panel_texts = [panel["Text"] for panel in panel_data] if include_speech_bubbles else [""] * 6
            
            if len(image_paths) == 6 and all(isinstance(img, str) and os.path.exists(img) for img in image_paths):
                output_image_path = os.path.join(OUTPUT_FOLDER, "comic_strip_with_text.png")
                
                # Force 3x2 grid layout (horizontal)
                is_vertical = False
                process_comic.create_comic_strip_with_text(image_paths, panel_texts, output_image_path, is_vertical)
                
                status.update(label="✅ Comic Complete!", state="complete", expanded=False)
                
                # Center the comic strip with some spacing
                st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
                
                # Create three columns with the middle one wider to center the image
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(output_image_path, width=400, caption="Your Generated Comic Strip")
                    
                st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
                st.success("🎉 Comic generated successfully!")
                
                # PDF Generation
                pdf_output_path = os.path.join(OUTPUT_FOLDER, "comic_strip.pdf")
                def create_pdf(image_path, pdf_output_path):
                    """Generate a PDF from the final comic strip"""
                    doc = SimpleDocTemplate(pdf_output_path, pagesize=A4)
                    img = RLImage(image_path, width=400, height=600)
                    spacer = Spacer(1, 20)
                    doc.build([img, spacer])
                create_pdf(output_image_path, pdf_output_path)
                
                col1, col2 = st.columns(2)
                with col1:
                    with open(output_image_path, "rb") as img_file:
                        st.download_button(
                            label="📥 Download as PNG",
                            data=img_file,
                            file_name="comic_strip.png",
                            mime="image/png",
                            use_container_width=True
                        )
                with col2:
                    with open(pdf_output_path, "rb") as pdf_file:
                        st.download_button(
                            label="� Download as PDF",
                            data=pdf_file,
                            file_name="comic_strip.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
            else:
                status.update(label="❌ Generation Failed", state="error", expanded=False)
                st.error("❌ Something went wrong! Please try again later.")
    else:
        st.error("⚠️ Please enter a story prompt.")