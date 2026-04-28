import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import io

# ==========================================
# CONFIGURAZIONE PAGINA
# ==========================================
st.set_page_config(page_title="Chef AI - Generatore Ricette & Costi", page_icon="🍳", layout="centered")

# ==========================================
# INIZIALIZZAZIONE OPENAI
# ==========================================
# Cerca la chiave API nei secrets di Streamlit
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("⚠️ Chiave API OpenAI non trovata. Aggiungi OPENAI_API_KEY nei Secrets di Streamlit.")
    st.stop()

# ==========================================
# MEMORIA DI SESSIONE
# ==========================================
# Serve a non perdere i dati generati quando la pagina si aggiorna (es. cliccando un pulsante)
if "risultato_ricette" not in st.session_state:
    st.session_state["risultato_ricette"] = ""

# ==========================================
# FUNZIONE GENERAZIONE PDF
# ==========================================
def crea_pdf(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    # Pulizia del testo per evitare errori di codifica con il font base (Latin-1)
    testo_pulito = testo.replace("€", "EUR").replace("’", "'").replace("“", '"').replace("”", '"')
    testo_pulito = testo_pulito.encode('latin-1', 'replace').decode('latin-1')
    
    # Aggiunge il titolo
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "Report Ricette e Food Cost", ln=True, align="C")
    pdf.ln(10)
    
    # Aggiunge il corpo del testo
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, testo_pulito)
    
    # Restituisce i byte del PDF
    return bytes(pdf.output())

# ==========================================
# INTERFACCIA UTENTE
# ==========================================
st.title("🍳 Generatore di Ricette & Food Cost")
st.markdown("Inserisci gli ingredienti a tua disposizione. L'IA creerà 10 ricette, calcolerà una stima del food cost e suggerirà un prezzo di vendita per il menù.")

ingredienti = st.text_area("Cosa hai in dispensa/frigo?", placeholder="Es: Guanciale, Pecorino, Uova, Pepe nero, Pasta...")

if st.button("Genera Ricette e Costi 🚀", use_container_width=True):
    if ingredienti.strip() == "":
        st.warning("Per favore, inserisci almeno un ingrediente.")
    else:
        with st.spinner("Lo Chef IA sta studiando il menù e i costi..."):
            
            # Prompt di sistema per istruire l'IA
            prompt_sistema = (
                "Sei un Executive Chef e un consulente della ristorazione esperto in Food Cost. "
                "Il tuo compito è generare esattamente 10 ricette professionali basate sugli ingredienti forniti dall'utente. "
                "Per ogni ricetta devi fornire: "
                "1. Nome del piatto. "
                "2. Breve descrizione e procedimento. "
                "3. Stima del Food Cost (in EUR) per una singola porzione. "
                "4. Prezzo di vendita suggerito al cliente (mantenendo un Food Cost attorno al 25-30%). "
                "Formatta il testo in modo chiaro e leggibile."
            )
            
            try:
                risposta = client.chat.completions.create(
                    model="gpt-4o-mini", # Modello veloce ed economico. Puoi usare "gpt-4o" per maggiore precisione
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {"role": "user", "content": f"Ecco gli ingredienti: {ingredienti}"}
                    ],
                    temperature=0.7
                )
                
                # Salva il risultato nella memoria di sessione
                st.session_state["risultato_ricette"] = risposta.choices[0].message.content
                
            except Exception as e:
                st.error(f"Si è verificato un errore durante la generazione: {e}")

# ==========================================
# RISULTATO E DOWNLOAD PDF
# ==========================================
if st.session_state["risultato_ricette"]:
    st.markdown("---")
    st.markdown("### 📋 Il tuo Menù")
    
    # Mostra il testo generato
    st.write(st.session_state["risultato_ricette"])
    
    st.markdown("---")
    
    # Genera il PDF dietro le quinte
    pdf_bytes = crea_pdf(st.session_state["risultato_ricette"])
    
    # Pulsante di Download
    st.download_button(
        label="📥 Scarica Report in PDF",
        data=pdf_bytes,
        file_name="ricette_food_cost.pdf",
        mime="application/pdf",
        use_container_width=True
    )
