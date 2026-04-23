import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN (INVARIATO)
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v90.4 - FLUX Edition", page_icon="📕", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; min-width: 420px !important; }
    header, footer, .stAppDeployButton { display: none !important; }
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #0d1117 !important; color: #58a6ff !important; border: 1px solid #30363d !important;
    }
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white; font-size: 1.1rem; font-weight: 800; height: 3.5rem; border-radius: 10px; border: none;
    }
    .pdf-uploader-box { border: 2px dashed #007bff; padding: 15px; border-radius: 8px; margin-bottom: 15px; background-color: #10141b; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. LOGICA SESSIONE
# ==============================================================================
if 'v83_prompt' not in st.session_state: st.session_state['v83_prompt'] = ""
if 'v83_res' not in st.session_state: st.session_state['v83_res'] = None
if 'auto_desc' not in st.session_state: st.session_state['auto_desc'] = ""

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 3. ANALISI NEUROMARKETING (GPT-4o-mini)
# ==============================================================================
TRIUNE_BRAIN_THEORY = """
REGOLE DI CONVERSIONE E NEUROMARKETING (I 3 CERVELLI):
1. CERVELLO RETTILIANO: Contrasto forte, impatto visivo immediato.
2. CERVELLO LIMBICO: Emozione, colori, sguardi.
3. NEOCORTECCIA: Spazio pulito, autorevolezza, tipografia chiara.
"""

class PDFSemanticPsychologyAnalyzer:
    @staticmethod
    def extract_text_from_pdf(pdf_file, max_pages=10):
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            text_content = ""
            limit = min(max_pages, len(reader.pages))
            for i in range(limit):
                page = reader.pages[i]
                text_content += page.extract_text() + " "
            return text_content
        except Exception as e:
            st.error(f"Errore lettura PDF: {e}")
            return None

    @staticmethod
    def generate_psychological_concept(text, api_token, genere_scelto, argomento_focus=""):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_token)
            focus = f"ARGOMENTO FOCUS: '{argomento_focus}'." if argomento_focus else ""
            
            sys_p = f"Sei un Art Director editoriale. Progetta una scena per una copertina in stile {genere_scelto}. {TRIUNE_BRAIN_THEORY} {focus} ESTRATTO: {text[:6000]}. Descrivi la scena visiva in 3 frasi italiane."
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": sys_p}],
                temperature=0.5
            )
            return resp.choices[0].message.content
        except Exception as e:
            st.error(f"Errore OpenAI: {e}")
            return None

# ==============================================================================
# 4. MATRICE STILI
# ==============================================================================
MODALITA_RENDERING = {
    "Fotorealistico": "photorealistic, 8k, highly detailed",
    "Illustrazione": "artistic digital illustration, vibrant",
    "Minimalista": "flat design, vector art, minimalist",
    "Vintage": "retro oil painting style"
}

ATMOSFERE = {
    "Business & Marketing": "modern corporate luxury, gold accents, sharp contrast",
    "Thriller / Noir": "suspenseful noir, cinematic shadows, gritty",
    "Self-Help": "uplifting, bright, inspiring, modern layout",
    "Manuale Pratico": "clear instructional layout, bold actionable design",
    "Contemporaneo": "sleek contemporary aesthetic, vivid colors"
}

# ==============================================================================
# 5. SIDEBAR
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v90.4")
    if st.button("🔄 RESET"): reset_all()
    
    genere = st.selectbox("1. Atmosfera:", list(ATMOSFERE.keys()))
    tipo_render = st.selectbox("2. Stile:", list(MODALITA_RENDERING.keys()))
    
    use_t = st.checkbox("Inserisci Titolo", value=True)
    t_val = st.text_input("Titolo:", "TITOLO ESEMPIO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    use_a = st.checkbox("Inserisci Autore", value=True)
    a_val = st.text_input("Autore:", "AUTORE ESEMPIO") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()
    argomento_focus = st.text_input("🎯 Argomento Focus:", placeholder="Es. Successo Finanziario")
    uploaded_pdf = st.file_uploader("Carica PDF:", type=["pdf"])
    
    if uploaded_pdf and st.button("🧠 Estrai Scena"):
        with st.spinner("Analisi GPT-4o-mini..."):
            txt = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
            if txt:
                scena = PDFSemanticPsychologyAnalyzer.generate_psychological_concept(txt, st.secrets["OPENAI_API_KEY"], genere, argomento_focus)
                st.session_state['auto_desc'] = scena

    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'])
    
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            t = GoogleTranslator(source='it', target='en')
            scene_en = t.translate(desc_it)
            
            # PROMPT OTTIMIZZATO PER FLUX: Testo esatto tra virgolette
            txt_p = ""
            if use_t and t_val: txt_p += f'The words "{t_val.upper()}" written in a massive bold font at the {t_pos}. '
            if use_a and a_val: txt_p += f'The name "{a_val.upper()}" written at the {a_pos}. '
            
            st.session_state['v83_prompt'] = (
                f"A high-quality 2D professional book cover illustration. {txt_p} "
                f"The artwork features: {scene_en}. "
                f"Style: {ATMOSFERE[genere]}, {MODALITA_RENDERING[tipo_render]}. "
                f"Ensure the text is perfectly spelled and clearly visible. Foreground focus, 8k resolution."
            )
            st.success("Architettura Flux pronta.")

# ==============================================================================
# 6. GENERAZIONE (FLUX SCHNELL - COSTO ZERO SPRECHI)
# ==============================================================================
st.title("🎨 Creative Workstation (Flux Schnell)")
col_l, col_r = st.columns([1.2, 1])

with col_l:
    p_edit = st.text_area("Prompt Finale:", value=st.session_state['v83_prompt'], height=250)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if p_edit:
            try:
                client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
                with st.spinner("Generazione con Flux Schnell (Precisione Testo)..."):
                    # FLUX SCHNELL: Il più veloce ed economico
                    output = client.run(
                        "black-forest-labs/flux-schnell",
                        input={
                            "prompt": p_edit,
                            "aspect_ratio": "2:3", # Perfetto per copertine KDP
                            "output_format": "webp",
                            "output_quality": 95
                        }
                    )
                    st.session_state['v83_res'] = output[0]
                    st.balloons()
            except Exception as e:
                st.error(f"Errore tecnico: {e}")

with col_r:
    if st.session_state['v83_res']:
        st.image(st.session_state['v83_res'], use_container_width=True)
        response = requests.get(st.session_state['v83_res'])
        st.download_button("📥 Scarica Copertina", data=response.content, file_name="cover.webp")
    else:
        st.info("Configura la sidebar e genera.")
