import streamlit as st
import os
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer
from BACKEND import generate_panels, generate_image, process_comic

PANEL_FOLDER = "PANEL_IMAGES"
OUTPUT_FOLDER = "OUTPUT"

os.makedirs(PANEL_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

STYLE_DESCRIPTIONS = {
    "Manga": "High-contrast black and white sketch with sharp, clean lines, exaggerated facial expressions, and dramatic shading. No bright colors, only grayscale tones",
    "Anime": "Vibrant colors with smooth cel shading, large expressive eyes, and detailed hair. Dynamic action poses with fluid motion lines",
    "American": "Bold outlines with heavy inking, bright and saturated colors, and exaggerated muscular features. Classic comic book style",
    "Belgian": "Clean, clear lines with soft, flat shading. Rich and detailed backgrounds in a semi-realistic style, inspired by Tintin comics",
}

st.markdown("""
    <style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .main .block-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    h1 {
        animation: slideIn 0.6s ease-out;
    }
    
    .stButton button {
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .stButton button:active {
        transform: translateY(0);
    }
    
    .stTextArea textarea, .stSelectbox > div > div {
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .stImage {
        animation: fadeIn 0.8s ease-out;
    }
    
    .stAlert {
        animation: slideIn 0.4s ease-out;
    }
    
    .stSpinner > div {
        animation: pulse 1.5s ease-in-out infinite;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 CraftyComic Ink")
st.write("Generate a 3x2 comic strip from your story prompt")

user_prompt = st.text_area("📝 Enter your story prompt", "")
art_style = st.selectbox("🎨 Choose an art style", list(STYLE_DESCRIPTIONS.keys()))
st.info(f"**Style Description:** {STYLE_DESCRIPTIONS[art_style]}")

if st.button("✨ Generate Comic"):
    if user_prompt:
        with st.spinner("✨ Generating panel descriptions & dialogues..."):
            panel_data = generate_panels.generate_panels(user_prompt, art_style)
        with st.spinner("🎨 Generating images for comic panels..."):
            image_paths = list(generate_image.generate_images(panel_data, art_style))
        panel_texts = [panel["Text"] for panel in panel_data]
        if len(image_paths) == 6 and all(isinstance(img, str) and os.path.exists(img) for img in image_paths):
            output_image_path = os.path.join(OUTPUT_FOLDER, "comic_strip_with_text.png")
            process_comic.create_comic_strip_with_text(image_paths, panel_texts, output_image_path)
            st.image(output_image_path, caption="Your Comic Strip", use_container_width=True)
            st.success("✅ Comic generated successfully!")
            pdf_output_path = os.path.join(OUTPUT_FOLDER, "comic_strip.pdf")
            def create_pdf(image_path, pdf_output_path):
                """Generate a PDF from the final comic strip"""
                doc = SimpleDocTemplate(pdf_output_path, pagesize=A4)
                img = RLImage(image_path, width=400, height=600)
                spacer = Spacer(1, 20)
                doc.build([img, spacer])
            create_pdf(output_image_path, pdf_output_path)
            with open(pdf_output_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Comic as PDF",
                    data=pdf_file,
                    file_name="comic_strip.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("❌ Something went wrong! Please try again later.")
    else:
        st.error("⚠️ Please enter a story prompt.")