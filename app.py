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

# Aggiunta: Inizializza la memoria per la chat dello Step 2
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

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
# LOGICA DI RESET
# ==========================================
with col_reset:
    if st.button("Reset 🔄", use_container_width=True):
        st.session_state["risultato_ricette"] = ""
        st.session_state["chat_history"] = [] # Aggiunta: Pulisce anche la memoria della chat
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
                
                # Prompt ingegnerizzato potenziato per procedimenti molto dettagliati (Modificato per tagli e parti specifiche)
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
                *Sii estremamente analitico e minuzioso. Specifica con rigore chirurgico la selezione della materia prima: indica esattamente quale taglio o parte dell'animale utilizzare (es. sella di coniglio, fegato, guancia, pancia, filetto), la varietà o il calibro dei vegetali. Descrivi le tecniche professionali utilizzate (es. criocottura, sferificazione, osmosi, reazione di Maillard, sottovuoto). Specifica temperature esatte (es. dell'olio o al cuore), consistenze attese, gestione degli scarti in ottica zero-waste, strumenti specifici da cucina professionale e consigli per un impiattamento gourmet.*
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
                    st.session_state["chat_history"] = [] # Reset della chat per ogni nuova generazione
                    
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

    # ==========================================
    # STEP 2: CHAT INTERATTIVA PER CHIARIMENTI (NUOVA SEZIONE)
    # ==========================================
    st.markdown("---")
    st.header("💬 Step 2: Chiedi allo Chef (Domande & Chiarimenti)")
    st.markdown("Hai dubbi su una tecnica? Vuoi sostituire un ingrediente, chiedere come sfilettare o capire meglio l'impiattamento? Fai una domanda allo Chef! Il numero di domande è illimitato.")

    # Mostra lo storico della chat
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input della chat
    if prompt_chat := st.chat_input("Chiedi allo Chef (es. 'Con cosa posso sostituire la menta?', 'Come cuocio esattamente a bassa temperatura?'):"):
        
        # Aggiunge il messaggio dell'utente allo storico e lo mostra
        st.chat_message("user").markdown(prompt_chat)
        st.session_state["chat_history"].append({"role": "user", "content": prompt_chat})

        # Prepara i messaggi per l'API, includendo il contesto delle ricette generate
        messaggi_chat = [
            {
                "role": "system", 
                "content": f"Sei l'Executive Chef stellato che ha appena creato questo menù per l'utente:\n\n{st.session_state['risultato_ricette']}\n\nRispondi alle domande dell'utente in modo professionale, tecnico ma comprensibile, fornendo consigli culinari di alto livello. Il contesto delle tue risposte deve sempre essere basato sul menù appena generato."
            }
        ]
        # Aggiunge tutto lo storico della chat
        messaggi_chat.extend(st.session_state["chat_history"])

        # Chiama l'API per generare la risposta
        with st.spinner("Lo Chef sta elaborando la risposta..."):
            try:
                risposta_chat = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messaggi_chat,
                    temperature=0.7
                )
                
                risposta_testo = risposta_chat.choices[0].message.content
                
                # Mostra la risposta dell'assistente e la salva
                with st.chat_message("assistant"):
                    st.markdown(risposta_testo)
                st.session_state["chat_history"].append({"role": "assistant", "content": risposta_testo})
                
            except Exception as e:
                st.error(f"Errore durante la comunicazione: {str(e)}")
