import streamlit as st
import io
from PIL import Image
import numpy as np
import os
import subprocess
import base64
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="SuperRez - Amélioration d'image HD",
    page_icon="🖼️",
    layout="wide"
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
        transition: all 0.3s;
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
        margin-bottom: 1rem;
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
</style>
""", unsafe_allow_html=True)

# Fonction pour créer un effet de glissement entre deux images
def create_image_comparison_html(before_img, after_img):
    # Convertir les images en base64
    before_base64 = image_to_base64(before_img)
    after_base64 = image_to_base64(after_img)
    
    # HTML/JS pour la comparaison d'images avec effet de glissement
    comparison_html = f 
    """
    <div class="img-comp-container" style="height: 600px; position: relative; overflow: hidden;">
      <div class="img-comp-img" style="position: absolute; width: 100%; height: 100%; overflow: hidden;">
        <img src="data:image/jpeg;base64,{before_base64}" style="width: 100%; object-fit: contain; display: block; height: 100%;">
      </div>
      <div class="img-comp-img img-comp-overlay" style="position: absolute; width: 50%; height: 100%; overflow: hidden;">
        <img src="data:image/jpeg;base64,{after_base64}" style="width: 200%; object-fit: contain; display: block; height: 100%;">
      </div>
      <div class="img-comp-slider" style="position: absolute; z-index: 9; cursor: ew-resize; width: 40px; height: 40px; background-color: #3494E6; border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); display: flex; align-items: center; justify-content: center;">
        <div style="color: white; font-size: 20px;">↔</div>
      </div>
    </div>
    <script>
    function initComparisons() { 
      var x, i;
      x = document.getElementsByClassName("img-comp-overlay");
      for (i = 0; i < x.length; i++) {
        compareImages(x[i]);
      }
      function compareImages(img) {
        var slider, clicked = 0, w, h;
        w = img.offsetWidth;
        h = img.offsetHeight;
        img.style.width = (w / 2) + "px";
        slider = img.nextElementSibling;
        slider.addEventListener("mousedown", slideReady);
        window.addEventListener("mouseup", slideFinish);
        slider.addEventListener("touchstart", slideReady);
        window.addEventListener("touchend", slideFinish);
        
        function slideReady(e) {
          e.preventDefault();
          clicked = 1;
          window.addEventListener("mousemove", slideMove);
          window.addEventListener("touchmove", slideMove);
        }
        
        function slideFinish() {
          clicked = 0;
        }
        
        function slideMove(e) {
          var pos;
          if (clicked == 0) return false;
          pos = getCursorPos(e);
          if (pos < 0) pos = 0;
          if (pos > w) pos = w;
          img.style.width = pos + "px";
          slider.style.left = img.offsetWidth + "px";
        }
        
        function getCursorPos(e) {
          var a, x = 0;
          e = (e.changedTouches) ? e.changedTouches[0] : e;
          a = img.getBoundingClientRect();
          x = e.pageX - a.left;
          x = x - window.pageXOffset;
          return x;
        }
      }
    }
    
    // Exécuter le script après le chargement de la page
    document.addEventListener("DOMContentLoaded", initComparisons);
    // Pour Streamlit qui charge dynamiquement le contenu
    setTimeout(initComparisons, 300);
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

# Interface divisée en colonnes
col1, col2 = st.columns([1.5, 3])

with col1:
    st.subheader("⚙️ Paramètres")
    
    # Upload d'image
    st.markdown("<p style='margin-top: 2rem; font-weight: bold;'>Sélectionner une image:</p>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
    
    # Options de modèle
    model_option = st.selectbox(
        "Modèle d'amélioration",
        ["realesrgan-x4plus", "realesrgan-x4plus-anime", "realesrgan-x2plus"],
        help="Sélectionnez le modèle selon votre type d'image"
    )
    
    # Facteur d'échelle
    scale_factor = st.slider(
        "Facteur d'échelle",
        min_value=2,
        max_value=4,
        value=4,
        help="Plus le facteur est élevé, plus la résolution finale sera importante"
    )
    
    # Option de préservation des couleurs
    preserve_colors = st.checkbox(
        "Préserver les couleurs originales",
        value=True,
        help="Active la préservation des couleurs d'origine"
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
    
    # Informations
    st.markdown("### ℹ️ À propos")
    st.markdown("""
    **SuperRez** utilise Real-ESRGAN, un modèle d'IA avancé pour:
    - Augmenter la résolution des images
    - Éliminer le bruit et les artefacts
    - Améliorer les détails et la netteté
    - Restaurer les photos anciennes
    """)

with col2:
    if uploaded_file is not None:
        # Afficher l'interface principale
        
        # Charger et afficher l'image originale
        image = Image.open(uploaded_file).convert("RGB")
        
        # Informations sur l'image
        width, height = image.size
        st.markdown(f"**Dimensions originales:** {width} x {height} pixels")
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.markdown('<p class="comparison-title">Image originale</p>', unsafe_allow_html=True)
            st.image(image, use_column_width=True)
        
        # Sauvegarder l'image temporairement avec horodatage pour éviter les conflits
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = f"input_{timestamp}.jpg"
        output_path = f"output_{timestamp}.jpg"
        image.save(input_path)
        
        # Bouton pour lancer le traitement
        if st.button("✨ Améliorer en HD"):
            with st.spinner("Traitement en cours... Veuillez patienter."):
                # Construction de la commande avec les options sélectionnées
                cmd = [
                    "./realesrgan-ncnn-vulkan.exe",
                    "-i", input_path,
                    "-o", output_path,
                    "-n", model_option,
                    "-s", str(scale_factor)
                ]
                
                if preserve_colors:
                    cmd.append("-fp")
                
                if denoise_level > 0:
                    cmd.extend(["-dn", str(denoise_level)])
                
                # Exécuter la commande
                result = subprocess.run(cmd, capture_output=True)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    # Charger et afficher l'image améliorée
                    hd_image = Image.open(output_path)
                    hd_width, hd_height = hd_image.size
                    
                    with col_img2:
                        st.markdown('<p class="comparison-title">Image améliorée HD</p>', unsafe_allow_html=True)
                        st.image(hd_image, use_column_width=True)
                    
                    # Afficher les statistiques
                    col_stats1, col_stats2 = st.columns(2)
                    with col_stats1:
                        st.metric("Résolution originale", f"{width} x {height}")
                    with col_stats2:
                        st.metric("Résolution HD", f"{hd_width} x {hd_height}", f"+{int((hd_width*hd_height)/(width*height)*100 - 100)}%")
                    
                    # Comparaison interactive des images
                    st.markdown("### Comparaison interactive (glissez pour voir la différence)")
                    comparison_html = create_image_comparison_html(image, hd_image)
                    st.components.v1.html(comparison_html, height=620)
                    
                    # Option de téléchargement
                    st.markdown('<div class="download-btn">', unsafe_allow_html=True)
                    with open(output_path, "rb") as f:
                        st.download_button(
                            "📥 Télécharger l'image HD",
                            f,
                            file_name=f"SuperRez_HD_{timestamp}.jpg",
                            mime="image/jpeg"
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Nettoyer les fichiers
                    try:
                        os.remove(input_path)
                    except:
                        pass
                else:
                    st.error("Erreur lors du traitement de l'image. Vérifiez que l'exécutable Real-ESRGAN est présent et fonctionnel.")
                    st.code(result.stderr.decode())
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Afficher un message d'accueil avec des exemples
        st.markdown('<div class="card" style="text-align: center; padding: 3rem 1rem;">', unsafe_allow_html=True)
        st.markdown("## 👋 Bienvenue sur SuperRez!")
        st.markdown("### Transformez vos images en qualité HD professionnelle")
        st.markdown("Chargez une image à gauche pour commencer")
        
        # Exemples visuels explicatifs
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        with col_ex1:
            st.markdown("#### 🔍 Améliorer la résolution")
            st.image("https://via.placeholder.com/200x150/3494E6/FFFFFF?text=Avant")
            st.image("https://via.placeholder.com/200x150/EC6EAD/FFFFFF?text=Après")
        with col_ex2:
            st.markdown("#### 🧹 Réduire le bruit")
            st.image("https://via.placeholder.com/200x150/3494E6/FFFFFF?text=Avant")
            st.image("https://via.placeholder.com/200x150/EC6EAD/FFFFFF?text=Après")
        with col_ex3:
            st.markdown("#### ✨ Restaurer les détails")
            st.image("https://via.placeholder.com/200x150/3494E6/FFFFFF?text=Avant")
            st.image("https://via.placeholder.com/200x150/EC6EAD/FFFFFF?text=Après")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Pied de page
st.markdown('<div class="footer">SuperRez - Propulsé par Real-ESRGAN et Streamlit</div>', unsafe_allow_html=True)