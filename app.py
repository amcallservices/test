import streamlit as st
import replicate
import requests
import os
import PyPDF2
from deep_translator import GoogleTranslator

# ==============================================================================
# 1. CONFIGURAZIONE E DESIGN (INVARIATO)
# ==============================================================================
st.set_page_config(page_title="Ebook Designer v90.2 - Targeted Neuromarketing", page_icon="📕", layout="wide")

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
# 2. LOGICA RESET E SESSIONE (INVARIATO)
# ==============================================================================
if 'v83_prompt' not in st.session_state: st.session_state['v83_prompt'] = ""
if 'v83_res' not in st.session_state: st.session_state['v83_res'] = None
if 'auto_desc' not in st.session_state: st.session_state['auto_desc'] = ""

def reset_all():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# ==============================================================================
# 3. KNOWLEDGE BASE: NEUROMARKETING E TRE CERVELLI (AGGIORNATO CON FOCUS)
# ==============================================================================
TRIUNE_BRAIN_THEORY = """
REGOLE DI CONVERSIONE E NEUROMARKETING (I 3 CERVELLI):
1. CERVELLO RETTILIANO (Istinto/Sopravvivenza): Cattura l'attenzione visiva immediata usando forti contrasti, elementi tangibili, minaccia/soluzione, o stimoli visivi primari (cibo, pericolo, sesso, fuga, vittoria).
2. CERVELLO LIMBICO (Emozione): Inserisci elementi che creano empatia o curiosità viscerale (es. sguardi intensi, atmosfere sognanti, colori caldi o drammatici, volti umani).
3. NEOCORTECCIA (Logica): Fornisci una struttura pulita, layout professionale e spazi vuoti per far capire istantaneamente che il libro è autorevole e risolve il problema.
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
            st.error(f"Errore nella lettura del PDF: {e}")
            return None

    @staticmethod
    def generate_psychological_concept(text, api_token, genere_scelto, argomento_focus=""):
        try:
            client = replicate.Client(api_token=api_token)
            
            # --- INTEGRAZIONE: LOGICA DEL FOCUS ARGOMENTO ---
            focus_istruzione = f"ARGOMENTO FOCUS RICHIESTO DALL'UTENTE: '{argomento_focus}'. L'intera metafora visiva DEVE ruotare attorno a questo tema specifico, integrandolo in modo fluido con il testo estratto dal PDF." if argomento_focus else "Estrai il tema principale unicamente dal testo del PDF."

            system_prompt = f"""
            Sei un Art Director editoriale senior esperto in {genere_scelto} e in Neuromarketing comportamentale.
            Il tuo scopo è progettare una scena visiva per una copertina che massimizzi le vendite (CTR) colpendo il subconscio del cliente al primo sguardo.
            
            {TRIUNE_BRAIN_THEORY}
            
            {focus_istruzione}
            
            ESTRATTO DEL LIBRO: {text[:6000]}
            
            ISTRUZIONI TASSATIVE:
            Progetta una singola immagine potente che unisca questi tre cervelli, TASSATIVAMENTE coerente con il genere '{genere_scelto}'.
            Scrivi SOLO ed esclusivamente la scena visiva in 3-4 frasi in italiano descrivendo: 
            - L'elemento visivo rettiliano (il contrasto/impatto).
            - L'atmosfera limbica (l'emozione/colori).
            - La composizione (logica/spazio per il testo).
            """
            output = client.run(
                "meta/meta-llama-3-8b-instruct",
                input={"prompt": system_prompt, "max_tokens": 300, "temperature": 0.5} 
            )
            return "".join(output)
        except Exception as e:
            st.error(f"Errore Motore LLM: {e}")
            return None

# ==============================================================================
# 4. MATRICE DEGLI STILI (DINAMICA AGGIORNATA CON CONTEMPORANEO)
# ==============================================================================
MODALITA_RENDERING = {
    "Fotorealistico": "photorealistic, 8k, highly detailed",
    "Illustrazione": "artistic digital illustration, vibrant",
    "3D Render": "octane render, unreal engine 5, 3d depth",
    "Minimalista": "flat design, vector art, minimalist",
    "Vintage": "retro oil painting style, aged paper"
}

ATMOSFERE = {
    "Saggio Scientifico": "authoritative academic layout, clean white space, mathematical or data precision",
    "Quiz Scientifico": "engaging educational layout, dynamic colorful diagrams, vibrant and fun",
    "Manuale Tecnico": "precise industrial schematic style, blueprint aesthetic, clean technical lines",
    "Religioso/Teologico": "sacred atmosphere, divine light rays, solemn and majestic classical composition",
    "Spirituale/Esoterico": "mystical vibes, occult symbols, ethereal fog, deep purple and gold palette",
    "Meditazione / Mindfulness": "peaceful serenity, zen harmony, soft focus, airy natural elements",
    "Business & Marketing": "modern corporate luxury, gold accents, sharp professional contrast, high-end branding",
    "Romanzo Rosa": "dreamy lighting, bokeh effect, soft pastel tones, emotional and romantic",
    "Thriller / Noir": "suspenseful noir, cinematic shadows, high contrast, dark and gritty mood",
    "Fantasy": "epic magical atmosphere, mystical glowing elements, ornate legendary landscape",
    "Fantascienza": "cyberpunk tech aesthetic, futuristic neon, space-age textures, sci-fi HUD",
    "Manuale Psicologico": "balanced zen minimalist layout, calming watercolor textures, psychological harmony",
    "Biografia": "classic biography portrait, elegant typography, timeless historical textures",
    "Ricettario": "gourmet food photography style, bright appetizing colors, fresh ingredients in focus",
    "Test Prep (Preparazione Esami)": "organized textbook style, academic focus icons, professional structured layout",
    "Romanzo Classico": "timeless literary aesthetic, elegant serif typography, historical or metaphorical atmosphere, oil painting or etched textures",
    "Narrativo": "balanced fiction layout, emotional narrative depth, contemporary commercial appeal, character-focused scenery",
    "Contemporaneo": "modern contemporary aesthetic, trendy and sleek layout, relatable everyday elements, vivid and crisp color grading, minimalist yet striking composition"
}

# ========================================================================
# INIZIO NUOVE RIGHE: AGGIUNTA SELF-HELP E MANUALE PRATICO
# ========================================================================
ATMOSFERE["Self-Help"] = "uplifting self-help aesthetic, bright and inspiring layout, modern typography, positive and empowering atmosphere, clear conceptual metaphor"
ATMOSFERE["Manuale Pratico"] = "hands-on practical guide, clear instructional layout, step-by-step visual clarity, functional and accessible design, bold actionable typography"
# ========================================================================
# FINE NUOVE RIGHE
# ========================================================================

# ==============================================================================
# 5. SIDEBAR: ZERO-WASTE TYPOGRAPHY ENFORCEMENT & TOPIC FOCUS
# ==============================================================================
with st.sidebar:
    st.title("📕 DESIGNER v90.2")
    if st.button("🔄 RESET COMPLETO"): reset_all()
    
    st.divider()
    genere = st.selectbox("1. Atmosfera Editoriale:", list(ATMOSFERE.keys()))
    tipo_render = st.selectbox("2. Stile di Rendering:", list(MODALITA_RENDERING.keys()))
    
    st.divider()
    
    use_t = st.checkbox("Abilita Inserimento Titolo", value=True)
    t_val = st.text_input("Testo Titolo:", "TITOLO ESEMPIO") if use_t else ""
    t_pos = st.selectbox("Posizione Titolo:", ["top", "center", "bottom"]) if use_t else ""

    use_a = st.checkbox("Abilita Inserimento Autore", value=True)
    a_val = st.text_input("Nome Autore:", "AUTORE ESEMPIO") if use_a else ""
    a_pos = st.selectbox("Posizione Autore:", ["top", "center", "bottom"], index=2) if use_a else ""

    st.divider()

    # Modulo PDF Neuromarketing con Suggerimento Argomento
    st.markdown('<div class="pdf-uploader-box">', unsafe_allow_html=True)
    st.markdown(f"📄 **Profilazione Neuromarketing ({genere})**")
    
    # --- INTEGRAZIONE: CAMPO DI TESTO PER L'ARGOMENTO FOCUS ---
    argomento_focus = st.text_input("🎯 Suggerisci Argomento (Opzionale):", placeholder="Es. Rivincita personale, Lotta di classe...")
    uploaded_pdf = st.file_uploader("Carica il PDF del libro:", type=["pdf"])
    
    if uploaded_pdf is not None:
        if st.button("🧠 Estrai Scena di Conversione"):
            if "REPLICATE_API_TOKEN" not in st.secrets:
                st.error("Token mancante!")
            else:
                with st.spinner(f"Analisi dei Tre Cervelli in corso..."):
                    txt = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if txt:
                        # Passiamo anche l'argomento_focus alla funzione
                        ai_scene = PDFSemanticPsychologyAnalyzer.generate_psychological_concept(txt, st.secrets["REPLICATE_API_TOKEN"], genere, argomento_focus)
                        if ai_scene:
                            st.session_state['auto_desc'] = ai_scene
                            st.success(f"Scena ottimizzata per le vendite generata!")
                            
        # ========================================================================
        # INIZIO NUOVE RIGHE: OPZIONE GPT-4o-MINI PER ANALISI TESTO
        # ========================================================================
        if st.button("🧠 Estrai Scena (Usa GPT-4o-mini)"):
            if "OPENAI_API_KEY" not in st.secrets:
                st.error("Chiave OPENAI_API_KEY mancante in st.secrets!")
            else:
                with st.spinner("Analisi con GPT-4o-mini in corso..."):
                    txt = PDFSemanticPsychologyAnalyzer.extract_text_from_pdf(uploaded_pdf)
                    if txt:
                        try:
                            from openai import OpenAI
                            client_oai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                            focus_istruzione = f"ARGOMENTO FOCUS RICHIESTO DALL'UTENTE: '{argomento_focus}'. L'intera metafora visiva DEVE ruotare attorno a questo tema specifico, integrandolo in modo fluido con il testo estratto dal PDF." if argomento_focus else "Estrai il tema principale unicamente dal testo del PDF."
                            sys_prompt = f"Sei un Art Director editoriale senior esperto in {genere} e in Neuromarketing comportamentale. Il tuo scopo è progettare una scena visiva per una copertina che massimizzi le vendite (CTR) colpendo il subconscio del cliente al primo sguardo.\n\n{TRIUNE_BRAIN_THEORY}\n\n{focus_istruzione}\n\nESTRATTO DEL LIBRO: {txt[:6000]}\n\nISTRUZIONI TASSATIVE: Progetta una singola immagine potente che unisca questi tre cervelli, TASSATIVAMENTE coerente con il genere '{genere}'. Scrivi SOLO ed esclusivamente la scena visiva in 3-4 frasi in italiano descrivendo: - L'elemento visivo rettiliano (il contrasto/impatto). - L'atmosfera limbica (l'emozione/colori). - La composizione (logica/spazio per il testo)."
                            
                            resp = client_oai.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": sys_prompt}],
                                temperature=0.5,
                                max_tokens=300
                            )
                            if resp.choices[0].message.content:
                                st.session_state['auto_desc'] = resp.choices[0].message.content
                                st.success("Scena generata con GPT-4o-mini!")
                        except Exception as e:
                            st.error(f"Errore OpenAI: {e}")
        # ========================================================================
        # FINE NUOVE RIGHE
        # ========================================================================

    st.markdown('</div>', unsafe_allow_html=True)

    desc_it = st.text_area("3. Scena Visiva (IT):", value=st.session_state['auto_desc'])
    
    # --- GABBIA DI FERRO PER LA TIPOGRAFIA (INVARIATO) ---
    if st.button("🪄 GENERA ARCHITETTURA"):
        if desc_it:
            with st.spinner("Compilazione prompt..."):
                try:
                    t = GoogleTranslator(source='it', target='en')
                    scene_en = t.translate(desc_it)
                    
                    text_enforcement = ""
                    if use_t and t_val:
                        text_enforcement += f"MANDATORY TITLE: The exact text \"{t_val.upper()}\" MUST be flawlessly printed in massive, highly legible font at the {t_pos}. "
                    if use_a and a_val:
                        text_enforcement += f"MANDATORY AUTHOR: The exact text \"{a_val.upper()}\" MUST be flawlessly printed at the {a_pos}. "

                    prompt = (
                        f"TYPOGRAPHY IS THE ABSOLUTE PRIORITY. {text_enforcement} "
                        f"VISUAL HOOK: A highly engaging, neuromarketing-optimized ebook cover representing: {scene_en}. "
                        f"STYLE DIRECTION: {ATMOSFERE[genere]} rendered in {MODALITA_RENDERING[tipo_render]}. "
                        f"CRITICAL ANTI-HALLUCINATION RULES: "
                        f"1. You MUST print the EXACT characters inside the quotes. "
                        f"2. ZERO EXTRA TEXT: Do not generate any random words, subtitles, watermarks, or gibberish. ONLY the requested strings. "
                        f"3. MAXIMUM LEGIBILITY: The background immediately behind the text MUST be darkened, blurred, or simplified to guarantee the text is 100% readable on the first try."
                    )
                    
                    # ========================================================================
                    # INIZIO NUOVE RIGHE: ENFORCEMENT CATEGORICO ASSOLUTO ZERO SPRECHI
                    # ========================================================================
                    blocco_categorico = ""
                    if use_t and t_val:
                        blocco_categorico += f"TITLE: '{t_val}' | "
                    if use_a and a_val:
                        blocco_categorico += f"AUTHOR: '{a_val}'"
                        
                    if blocco_categorico:
                        prompt = f"[SYSTEM OVERRIDE: CATEGORICAL REQUIREMENT] YOU ARE STRICTLY FORBIDDEN FROM GENERATING THIS IMAGE WITHOUT THE EXACT TEXT: {blocco_categorico}. " + prompt + f" FINAL DIRECTIVE: IF THE WORDS {blocco_categorico} ARE OMITTED, IT IS A CATASTROPHIC FAILURE. RENDER THEM BOLDLY."
                    # ========================================================================
                    # FINE NUOVE RIGHE
                    # ========================================================================

                    st.session_state['v83_prompt'] = prompt
                    st.success(f"Architettura Zero-Sprechi pronta.")
                except Exception as e:
                    st.error(f"Errore: {e}")

# ==============================================================================
# 6. WORKSTATION GENERAZIONE (INVARIATO)
# ==============================================================================
st.title("🎨 Custom Creative Workstation")
col_l, col_r = st.columns([1.2, 1])

with col_l:
    p_edit = st.text_area("Prompt Finale (EN):", value=st.session_state['v83_prompt'], height=300)
    
    if st.button("🔥 GENERA COPERTINA HD"):
        if not p_edit:
            st.error("Configura prima la sidebar!")
        else:
            client = replicate.Client(api_token=st.secrets["REPLICATE_API_TOKEN"])
            try:
                with st.spinner("Generazione Master in corso..."):
                    out = client.run(
                        "black-forest-labs/flux-1.1-pro",
                        input={"prompt": p_edit, "aspect_ratio": "2:3", "output_format": "jpg", "output_quality": 100}
                    )
                    st.session_state['v83_res'] = str(out)
                    st.balloons()
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                
    # ========================================================================
    # INIZIO NUOVE RIGHE: OPZIONE DALL-E 3 (ECOSISTEMA GPT) PER IMMAGINI
    # ========================================================================
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("✨ GENERA COPERTINA CON OPENAI (GPT / DALL-E 3)"):
        if not p_edit:
            st.error("Configura prima la sidebar e compila il prompt!")
        elif "OPENAI_API_KEY" not in st.secrets:
            st.error("Manca la OPENAI_API_KEY nei secrets!")
        else:
            try:
                from openai import OpenAI
                client_oai = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
                with st.spinner("Generazione Master OpenAI (DALL-E 3) in corso..."):
                    response_oai = client_oai.images.generate(
                        model="dall-e-3",
                        prompt=p_edit[:4000],  # DALL-E 3 ha un limite di 4000 caratteri per il prompt
                        size="1024x1792",      # Aspect ratio perfetto per KDP
                        quality="hd",
                        n=1
                    )
                    st.session_state['v83_res'] = response_oai.data[0].url
                    st.balloons()
                    st.rerun() # Forza l'aggiornamento per mostrare l'immagine
            except Exception as e:
                st.error(f"Errore tecnico OpenAI: {e}")
    # ========================================================================
    # FINE NUOVE RIGHE
    # ========================================================================

with col_r:
    if st.session_state['v83_res']:
        st.image(st.session_state['v83_res'], use_container_width=True)
        st.divider()
        response = requests.get(st.session_state['v83_res'])
        st.download_button(label="📥 Scarica Copertina", data=response.content, file_name="cover.jpg", mime="image/jpeg")
    else:
        st.info("Configura e genera per visualizzare l'anteprima.")
