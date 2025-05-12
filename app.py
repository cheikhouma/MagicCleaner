import streamlit as st
import io
from PIL import Image
import numpy as np
import os
import subprocess
import base64
from datetime import datetime
import os

# Créer les dossiers s'ils n'existent pas (utile pour Streamlit Cloud)
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

# Configuration de la page
st.set_page_config(
    page_title="MagicCleaner  - Amélioration d'image HD",
    page_icon="🖼️"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        background: linear-gradient(90deg, #3494E6, #EC6EAD);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background-color: #3494E6;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        width: 100%;
        transition: all 0.3s;
        margin: 1rem 0;
    }
    .stButton>button:hover {
        background-color: #EC6EAD;
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .card {
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    .download-btn {
        text-align: center;
        margin-top: 1rem;
    }
    .comparison-title {
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .stSpinner > div {
        border-top-color: #3494E6 !important;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        color: #6c757d;
        font-size: 0.8rem;
    }
    .image-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap;
        margin: 1rem 0;
    }
    .image-card {
        text-align: center;
        margin: 0.5rem;
        max-width: 48%;
    }
    .hide-label label {
        display: none;
    }
    .options-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .option-item {
        flex: 1;
        min-width: 200px;
    }
    .centered {
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour créer un effet de glissement entre deux images
def create_image_comparison_html(before_img, after_img):
    # Convertir les images en base64
    before_base64 = image_to_base64(before_img)
    after_base64 = image_to_base64(after_img)
    
    # HTML/JS pour la comparaison d'images avec effet de glissement
    comparison_html = f"""
    <style>
    .comparison-container {{
        position: relative;
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        background: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        overflow: hidden;
    }}
    .comparison-wrapper {{
        position: relative;
        width: 100%;
        height: 600px;
        overflow: hidden;
    }}
    .comparison-before {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }}
    .comparison-after {{
        position: absolute;
        top: 0;
        left: 0;
        width: 50%;
        height: 100%;
        overflow: hidden;
        border-right: 3px solid #3494E6;
    }}
    .comparison-before img, .comparison-after img {{
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }}
    .comparison-slider {{
        position: absolute;
        top: 0;
        left: 50%;
        width: 4px;
        height: 100%;
        background: #3494E6;
        cursor: ew-resize;
        transform: translateX(-50%);
        z-index: 10;
    }}
    .comparison-slider::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 40px;
        height: 40px;
        background: #3494E6;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}
    .comparison-slider::after {{
        content: '↔';
        position: absolute;
        top: 50%;
        left: 50%;
        color: white;
        font-size: 20px;
        transform: translate(-50%, -50%);
        pointer-events: none;
    }}
    .comparison-labels {{
        position: absolute;
        bottom: 20px;
        width: 100%;
        display: flex;
        justify-content: space-between;
        padding: 0 20px;
        color: white;
        font-weight: bold;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        pointer-events: none;
    }}
    </style>
    <div class="comparison-container">
        <div class="comparison-wrapper">
            <div class="comparison-before">
                <img src="data:image/jpeg;base64,{before_base64}">
            </div>
            <div class="comparison-after">
                <img src="data:image/jpeg;base64,{after_base64}">
            </div>
            <div class="comparison-slider"></div>
            <div class="comparison-labels">
                <span>Après</span>
                <span>Avant</span>
            </div>
        </div>
    </div>
    <script>
    function initComparison() {{
        const container = document.querySelector('.comparison-wrapper');
        const after = document.querySelector('.comparison-after');
        const slider = document.querySelector('.comparison-slider');
        let isDown = false;
        let startX;
        let scrollLeft;

        function handleMouseDown(e) {{
            isDown = true;
            startX = e.pageX - container.offsetLeft;
            scrollLeft = after.offsetWidth;
        }}

        function handleMouseUp() {{
            isDown = false;
        }}

        function handleMouseMove(e) {{
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX);
            const newWidth = Math.max(0, Math.min(container.offsetWidth, scrollLeft + walk));
            after.style.width = newWidth + 'px';
            slider.style.left = newWidth + 'px';
        }}

        function handleTouchStart(e) {{
            isDown = true;
            startX = e.touches[0].pageX - container.offsetLeft;
            scrollLeft = after.offsetWidth;
        }}

        function handleTouchMove(e) {{
            if (!isDown) return;
            const x = e.touches[0].pageX - container.offsetLeft;
            const walk = (x - startX);
            const newWidth = Math.max(0, Math.min(container.offsetWidth, scrollLeft + walk));
            after.style.width = newWidth + 'px';
            slider.style.left = newWidth + 'px';
        }}

        slider.addEventListener('mousedown', handleMouseDown);
        window.addEventListener('mouseup', handleMouseUp);
        window.addEventListener('mousemove', handleMouseMove);
        slider.addEventListener('touchstart', handleTouchStart);
        window.addEventListener('touchend', handleMouseUp);
        window.addEventListener('touchmove', handleTouchMove);
    }}

    // Pour Streamlit qui charge dynamiquement le contenu
    setTimeout(initComparison, 300);
    </script>
    """
    return comparison_html

# Fonction pour convertir une image en base64
def image_to_base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Titre principal
st.markdown('<h1 class="main-title">MagicCleaner - Transformation HD d\'Images</h1>', unsafe_allow_html=True)

# Carte principale
st.markdown('<div class="card">', unsafe_allow_html=True)

# Section upload d'image
st.subheader("📤 Sélectionner une image")
uploaded_file = st.file_uploader("Choisissez une image JPG, JPEG ou PNG", type=["jpg", "jpeg", "png"])

# Si une image est uploadée
if uploaded_file is not None:
    # Charger et afficher l'image originale
    image = Image.open(uploaded_file).convert("RGB")
    width, height = image.size
    
    # Afficher l'image originale
    st.markdown("### Votre image")
    st.image(image, use_container_width =True, caption=f"Dimensions: {width} x {height} pixels")
    
    # Afficher les options dans un expander
    with st.expander("⚙️ Options avancées (optionnel)"):
        col1, col2 = st.columns(2)
        with col1:
            # Options de modèle
            model_option = st.selectbox(
                "Modèle d'amélioration",
                ["realesrgan-x4plus", "realesrgan-x4plus-anime", "realesrgan-x2plus"],
                help="Sélectionnez le modèle selon votre type d'image"
            )
            
            # Option de préservation des couleurs
            preserve_colors = st.checkbox(
                "Préserver les couleurs originales",
                value=True,
                help="Active la préservation des couleurs d'origine"
            )
        
        with col2:
            # Facteur d'échelle
            scale_factor = st.slider(
                "Facteur d'échelle",
                min_value=2,
                max_value=4,
                value=4,
                help="Plus le facteur est élevé, plus la résolution finale sera importante"
            )
            
            # Option de débruitage
            denoise_level = st.slider(
                "Niveau de débruitage",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                help="0 = Pas de débruitage, 1 = Débruitage maximum"
            )
    
    # Sauvegarder l'image temporairement avec horodatage pour éviter les conflits
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_path = f"input/input_{timestamp}.jpg"
    output_path = f"output/output_{timestamp}.jpg"
    image.save(input_path)
    
    # Bouton pour lancer le traitement
    st.markdown('<div class="centered">', unsafe_allow_html=True)
    process_button = st.button("✨ Améliorer en HD")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if process_button:
        with st.spinner("Traitement en cours... Veuillez patienter."):
            try:
                import cv2
                from realesrgan import RealESRGANer

                # Charger l'image
                img = cv2.imread(input_path, cv2.IMREAD_COLOR)

                # Initialiser l'upscaler
                model_name = model_option
                model_paths = {
                    "realesrgan-x4plus": "realesrgan-x4plus.pth",
                    "realesrgan-x4plus-anime": "realesrgan-x4plus-anime.pth",
                    "realesrgan-x2plus": "realesrgan-x2plus.pth"
                }

                # Télécharger automatiquement le bon modèle
                upsampler = RealESRGANer(
                    scale=scale_factor,
                    model_path=None,
                    model_name=model_name,
                    half=False,  # True si GPU compatible FP16 (pas sur Streamlit Cloud)
                    tile=0,      # Tu peux activer le tiling si besoin
                    pre_pad=0
                )

                # Traitement
                output, _ = upsampler.enhance(img, outscale=scale_factor)

                # Sauvegarder le résultat
                cv2.imwrite(output_path, output)

                # Charger l'image HD pour l'affichage
                hd_image = Image.open(output_path)
                hd_width, hd_height = hd_image.size

                st.success("✅ Image traitée avec succès!")

                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    st.metric("Résolution originale", f"{width} x {height}")
                with col_stats2:
                    st.metric("Résolution HD", f"{hd_width} x {hd_height}", f"+{int((hd_width*hd_height)/(width*height)*100 - 100)}%")

                st.markdown("### Résultat: Original vs HD")
                st.markdown('<div class="image-container">', unsafe_allow_html=True)
                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                st.image(image, use_container_width=True, caption="Original")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="image-card">', unsafe_allow_html=True)
                st.image(hd_image, use_container_width=True, caption="HD")
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown("### Comparaison interactive")
                st.markdown("Glissez le curseur pour voir la différence:")
                comparison_html = create_image_comparison_html(image, hd_image)
                st.components.v1.html(comparison_html, height=650, width=None)

                st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                with open(output_path, "rb") as f:
                    st.download_button(
                        "📥 Télécharger l'image HD",
                        f,
                        file_name=f"MagicCleaner_HD_{timestamp}.jpg",
                        mime="image/jpeg"
                    )
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Erreur lors du traitement : {e}")

else:
    # Afficher un message d'accueil
    st.markdown('<div style="text-align: center; padding: 2rem 0;">', unsafe_allow_html=True)
    st.markdown("## 👋 Bienvenue sur MagicCleaner!")
    st.markdown("### Transformez vos images en qualité HD professionnelle")
    st.markdown("Commencez par charger une image ci-dessus")
    
    # Bloc explicatif
    st.markdown("#### Comment ça fonctionne:")
    st.markdown("""
    1. **Chargez** votre image
    2. **Lancez** l'amélioration HD
    3. **Téléchargez** votre nouvelle image en haute définition
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Informations sur l'outil
    st.markdown("### ℹ️ À propos de cet outil")
    st.markdown("""
    **MagicCleaner** utilise Real-ESRGAN, un modèle d'IA avancé pour:
    - Augmenter la résolution des images
    - Éliminer le bruit et les artefacts
    - Améliorer les détails et la netteté
    - Restaurer les photos anciennes
    """)

st.markdown("</div>", unsafe_allow_html=True)

# Pied de page
st.markdown('<div class="footer">MagicCleaner - Propulsé par Real-ESRGAN et Streamlit</div>', unsafe_allow_html=True)