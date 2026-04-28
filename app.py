import streamlit as st
from openai import OpenAI
from fpdf import FPDF

# ==========================================
# CONFIGURAZIONE PAGINA E MEMORIA
# ==========================================
st.set_page_config(page_title="Chef IA - Ricette Innovative & Food Cost", page_icon="🍳", layout="centered")

# Inizializza la memoria di sessione per non perdere i dati durante il download
if "risultato_ricette" not in st.session_state:
    st.session_state["risultato_ricette"] = ""

# ==========================================
# INIZIALIZZAZIONE OPENAI
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("⚠️ Chiave API OpenAI non trovata. Aggiungi OPENAI_API_KEY nei Secrets di Streamlit.")
    st.stop()

# ==========================================
# FUNZIONE GENERAZIONE PDF
# ==========================================
def crea_pdf(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    # Sanitizzazione per FPDF (gestisce caratteri non supportati dal font base)
    testo_pulito = testo.replace("€", "EUR").replace("’", "'").replace("“", '"').replace("”", '"')
    testo_pulito = testo_pulito.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Menù Innovativo e Analisi Food Cost", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, testo_pulito)
    
    return bytes(pdf.output())

# ==========================================
# INTERFACCIA UTENTE
# ==========================================
st.title("🍳 Chef IA: Innovazione & Food Cost")
st.markdown("Inserisci gli ingredienti. L'IA genererà 10 ricette **innovative**, con dettagli completi su grammatura, preparazione, tempi e un'analisi analitica del Food Cost.")

ingredienti = st.text_area(
    "Ingredienti a disposizione:", 
    placeholder="Es: Guanciale, Gamberi rossi, Pistacchio, Lime, Menta...",
    height=100
)

# Layout per i pulsanti di azione
col_gen, col_reset = st.columns([4, 1])

# ==========================================
# LOGICA DI RESET (Aggiunta)
# ==========================================
with col_reset:
    if st.button("Reset 🔄", use_container_width=True):
        st.session_state["risultato_ricette"] = ""
        st.rerun()

# ==========================================
# LOGICA DI GENERAZIONE
# ==========================================
with col_gen:
    if st.button("Genera Ricette Innovative 🚀", use_container_width=True):
        if not ingredienti.strip():
            st.warning("Per favore, inserisci almeno un ingrediente.")
        else:
            with st.spinner("Lo Chef IA sta studiando abbinamenti innovativi e calcolando i costi..."):
                
                # Prompt ingegnerizzato potenziato per procedimenti molto dettagliati
                prompt_sistema = """
                Sei un Executive Chef stellato esperto in cucina molecolare, fusion e innovativa, nonché un maestro nel controllo del Food Cost.
                Genera esattamente 10 ricette altamente innovative utilizzando gli ingredienti forniti. 
                
                Per OGNI ricetta, formatta la risposta rigorosamente in questo modo:
                
                ### [Nome Creativo del Piatto]
                *Descrizione: [Breve intro sul concept del piatto e la filosofia degli abbinamenti]*
                
                **Tempi:** Preparazione: [X] min | Cottura: [Y] min | Riposo: [Z] min
                
                **Ingredienti e Food Cost (per 1 porzione):**
                - [Grammatura esatta] [Nome Ingrediente] - [Costo Stimato EUR]
                - [Grammatura esatta] [Nome Ingrediente] - [Costo Stimato EUR]
                - [Continua per tutti gli ingredienti]
                
                **Food Cost Totale Piatto:** [Totale EUR]
                **Prezzo di Vendita Suggerito (Markup 300% / Target 25-30% FC):** [Prezzo EUR]
                
                **Procedimento Tecnico Dettagliato:**
                *Sii estremamente analitico e minuzioso. Descrivi le tecniche professionali utilizzate (es. criocottura, sferificazione, osmosi, reazione di Maillard, sottovuoto). Specifica temperature esatte (es. dell'olio o al cuore), consistenze attese, strumenti specifici da cucina professionale e consigli per un impiattamento gourmet.*
                1. [Step 1 dettagliato]
                2. [Step 2 dettagliato]
                [Continua con passaggi tecnici completi]
                ---
                """
                
                try:
                    risposta = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": prompt_sistema},
                            {"role": "user", "content": f"Crea il menù usando questi ingredienti base: {ingredienti}"}
                        ],
                        temperature=0.8
                    )
                    
                    st.session_state["risultato_ricette"] = risposta.choices[0].message.content
                    
                except Exception as e:
                    st.error(f"Errore durante la generazione: {str(e)}")

# ==========================================
# VISUALIZZAZIONE E DOWNLOAD
# ==========================================
if st.session_state["risultato_ricette"]:
    st.markdown("---")
    st.subheader("📋 Le Tue Ricette Innovative")
    
    st.write(st.session_state["risultato_ricette"])
    
    st.markdown("---")
    
    pdf_bytes = crea_pdf(st.session_state["risultato_ricette"])
    
    st.download_button(
        label="📥 Scarica PDF con Ricette e Food Cost",
        data=pdf_bytes,
        file_name="menu_innovativo_foodcost.pdf",
        mime="application/pdf",
        use_container_width=True
    )
