import streamlit as st
import os
import requests
import re
import json
import time
import datetime
from fpdf import FPDF
from openai import OpenAI
from docx import Document
from io import BytesIO
from collections import Counter
import PyPDF2  # Necessaria per l'analisi dei PDF caricate

# ======================================================================================================================
# 0. GESTIONE MEMORIA DI STATO E PREVENZIONE AUTO-RESET
# ======================================================================================================================
if "memoria_blindata" not in st.session_state:
    st.session_state["memoria_blindata"] = True
    st.session_state["indice_raw"] = ""
    st.session_state["lista_capitoli"] = []
    # Nuova chiave per contenere il testo estratto dai file caricati
    st.session_state["conoscenza_extra"] = ""

# ======================================================================================================================
# FUNZIONE ESTRAZIONE TESTO DA DOCUMENTI (NUOVO MODULO OPZIONALE)
# ======================================================================================================================
def estrai_testo_da_files(files_caricati):
    testo_estratto = ""
    for file in files_caricati:
        try:
            if file.name.lower().endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(file)
                for pagina in pdf_reader.pages:
                    testo_estratto += (pagina.extract_text() or "") + "\n"
            elif file.name.lower().endswith('.docx'):
                doc = Document(file)
                for para in doc.paragraphs:
                    testo_estratto += para.text + "\n"
        except Exception as e:
            st.error(f"Errore durante la lettura del file {file.name}: {e}")
    return testo_estratto

# ======================================================================================================================
# 1. ARCHITETTURA DI SISTEMA E SICUREZZA API
# ======================================================================================================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception as e:
    st.error("ERRORE CRITICO: Chiave API OpenAI non trovata nei Secrets di Streamlit.")

st.set_page_config(
    page_title="AI di Antonino: Ebook Mondiale Creator PRO",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="✒️"
)

# ======================================================================================================================
# 2. DIZIONARIO MULTILINGUA INTEGRALE (9 LINGUE)
# ======================================================================================================================
TRADUZIONI = {
    "Italiano": {
        "side_tit": "⚙️ Configurazione Editor",
        "lbl_tit": "Titolo del Libro", "lbl_auth": "Nome Autore", "lbl_lang": "Lingua", 
        "lbl_gen": "Genere Letterario", "lbl_style": "Tipologia Scrittura", "lbl_plot": "Trama o Argomento",
        "lbl_narrative": "Stile di Racconto", "lbl_goal": "Obiettivo del Libro", "lbl_pov": "Punto di Vista (Pronome)",
        "btn_res": "🔄 RESET PROGETTO", "tabs": ["📊 1. Indice", "✍️ 2. Scrittura & Quiz", "📖 3. Anteprima", "📑 4. Esporta"],
        "btn_idx": "🚀 Genera Indice Professionale", "btn_sync": "✅ Salva e Sincronizza Capitoli",
        "lbl_sec": "Seleziona sezione:", "btn_write": "✨ SCRIVI CONTENUTO (Dettagliato)",
        "btn_quiz": "🧠 AGGIUNGI QUIZ AL LIBRO", "btn_edit": "🚀 RIELABORA CON IA",
        "msg_run": "Il neuro-linguista sta analizzando gerarchia, stile e target emotivo...", "preface": "Prefazione", "ack": "Ringraziamenti",
        "preview_tit": "📖 Vista Lettura Professionale", "btn_word": "📥 Scarica Word (.docx)", "btn_pdf": "📥 Scarica PDF (.pdf)",
        "msg_err_idx": "Genera l'indice nella Tab 1 prima di procedere.", "msg_success_sync": "Capitoli sincronizzati!",
        "label_editor": "Editor di Testo Professionale", "welcome": "👋 Benvenuto nell'Ebook Creator di Antonino.",
        "guide": "Usa la sidebar a sinistra per impostare i parametri del tuo libro.",
        "lbl_upload": "📂 Carica Fonti (PDF/DOCX) - Max 10"
    },
    "English": {
        "side_tit": "⚙️ Editor Setup", "lbl_tit": "Book Title", "lbl_auth": "Author Name", "lbl_lang": "Language", 
        "lbl_gen": "Genre", "lbl_style": "Writing Style", "lbl_plot": "Plot", "lbl_narrative": "Narrative Style", "lbl_goal": "Book Goal", "lbl_pov": "Point of View (Pronoun)",
        "btn_res": "🔄 RESET PROJECT", "tabs": ["📊 1. Index", "✍️ 2. Write & Quiz", "📖 3. Preview", "📑 4. Export"],
        "btn_idx": "🚀 Generate Index", "btn_sync": "✅ Sync Chapters", "lbl_sec": "Select section:",
        "btn_write": "✨ WRITE CONTENT", "btn_quiz": "🧠 ADD QUIZ", "btn_edit": "🚀 REWRITE",
        "msg_run": "Native expert analyzing hierarchy, style and goal...", "preface": "Preface", "ack": "Acknowledgements",
        "preview_tit": "📖 Reading View", "btn_word": "📥 Word", "btn_pdf": "📥 PDF",
        "msg_err_idx": "Generate index first.", "msg_success_sync": "Synced!",
        "label_editor": "Editor", "welcome": "👋 Welcome.", "guide": "Use sidebar.",
        "lbl_upload": "📂 Upload Sources (PDF/DOCX) - Max 10"
    },
    "Español": {
        "side_tit": "⚙️ Configuración del Editor", "lbl_tit": "Título del Libro", "lbl_auth": "Nombre del Autor", "lbl_lang": "Idioma", 
        "lbl_gen": "Género Literario", "lbl_style": "Estilo de Escritura", "lbl_plot": "Trama o Argumento", "lbl_narrative": "Estilo Narrativo", "lbl_goal": "Objetivo del Libro", "lbl_pov": "Punto de Vista (Pronombre)",
        "btn_res": "🔄 RESETEAR PROYECTO", "tabs": ["📊 1. Índice", "✍️ 2. Escritura y Quiz", "📖 3. Vista Previa", "📑 4. Exportar"],
        "btn_idx": "🚀 Generar Índice Profesional", "btn_sync": "✅ Guardar y Sincronizar", "lbl_sec": "Seleccionar sección:",
        "btn_write": "✨ ESCRIBIR CONTENIDO", "btn_quiz": "🧠 AÑADIR QUIZ", "btn_edit": "🚀 REESCRIBIR",
        "msg_run": "Analizando jerarquía y estilo...", "preface": "Prefacio", "ack": "Agradecimientos",
        "preview_tit": "📖 Vista de Lectura", "btn_word": "📥 Descargar Word", "btn_pdf": "📥 Descargar PDF",
        "msg_err_idx": "Genera el índice primero.", "msg_success_sync": "¡Sincronizado!", "label_editor": "Editor Profesional", "welcome": "👋 Bienvenido.", "guide": "Usa la barra lateral.",
        "lbl_upload": "📂 Cargar fuentes (PDF/DOCX)"
    },
    "Français": {
        "side_tit": "⚙️ Configuration de l'Éditeur", "lbl_tit": "Titre du Livre", "lbl_auth": "Nom de l'Auteur", "lbl_lang": "Langue", 
        "lbl_gen": "Genre Littéraire", "lbl_style": "Style d'Écriture", "lbl_plot": "Intrigue ou Sujet", "lbl_narrative": "Style Narratif", "lbl_goal": "Objectif du Livre", "lbl_pov": "Point de Vue (Pronom)",
        "btn_res": "🔄 RÉINITIALISER", "tabs": ["📊 1. Index", "✍️ 2. Écriture & Quiz", "📖 3. Aperçu", "📑 4. Exporter"],
        "btn_idx": "🚀 Générer l'Index", "btn_sync": "✅ Synchroniser", "lbl_sec": "Sélectionner la section:",
        "btn_write": "✨ ÉCRIRE LE CONTENU", "btn_quiz": "🧠 AJOUTER UN QUIZ", "btn_edit": "🚀 RÉÉCRIRE",
        "msg_run": "Analyse de la hiérarchie et du style...", "preface": "Préface", "ack": "Remerciements",
        "preview_tit": "📖 Aperçu de Lecture", "btn_word": "📥 Télécharger Word", "btn_pdf": "📥 Télécharger PDF",
        "msg_err_idx": "Générez l'index d'abord.", "msg_success_sync": "Synchronisé!", "label_editor": "Éditeur Professionnel", "welcome": "👋 Bienvenue.", "guide": "Utilisez la barre latérale.",
        "lbl_upload": "📂 Charger les sources"
    },
    "Deutsch": {
        "side_tit": "⚙️ Editor-Setup", "lbl_tit": "Buchtitel", "lbl_auth": "Autorenname", "lbl_lang": "Sprache", 
        "lbl_gen": "Genre", "lbl_style": "Schreibstil", "lbl_plot": "Handlung", "lbl_narrative": "Erzählstil", "lbl_goal": "Buchziel", "lbl_pov": "Erzählperspektive (Pronomen)",
        "btn_res": "🔄 PROJEKT ZURÜCKSETZEN", "tabs": ["📊 1. Index", "✍️ 2. Schreiben & Quiz", "📖 3. Vorschau", "📑 4. Exportieren"],
        "btn_idx": "🚀 Index Generieren", "btn_sync": "✅ Synchronisieren", "lbl_sec": "Abschnitt wählen:",
        "btn_write": "✨ INHALT SCHREIBEN", "btn_quiz": "🧠 QUIZ HINZUFÜGEN", "btn_edit": "🚀 UMSCHREIBEN",
        "msg_run": "Analysiere Hierarchie und Stil...", "preface": "Vorwort", "ack": "Danksagungen",
        "preview_tit": "📖 Leseansicht", "btn_word": "📥 Word Herunterladen", "btn_pdf": "📥 PDF Herunterladen",
        "msg_err_idx": "Generiere zuerst den Index.", "msg_success_sync": "Synchronisiert!", "label_editor": "Professioneller Editor", "welcome": "👋 Willkommen.", "guide": "Nutze die Seitenleiste.",
        "lbl_upload": "📂 Quellen hochladen"
    },
    "Română": {
        "side_tit": "⚙️ Configurare Editor", "lbl_tit": "Titlul Cărții", "lbl_auth": "Nume Autor", "lbl_lang": "Limbă", 
        "lbl_gen": "Gen Literar", "lbl_style": "Stil de Scriere", "lbl_plot": "Subiect", "lbl_narrative": "Stil Narativ", "lbl_goal": "Obiectivul Cărții", "lbl_pov": "Punct de Vedere (Pronume)",
        "btn_res": "🔄 RESETARE PROIECT", "tabs": ["📊 1. Cuprins", "✍️ 2. Scriere & Quiz", "📖 3. Previzualizare", "📑 4. Export"],
        "btn_idx": "🚀 Generare Cuprins", "btn_sync": "✅ Sincronizare", "lbl_sec": "Selectează secțiunea:",
        "btn_write": "✨ SCRIE CONȚINUT", "btn_quiz": "🧠 ADAUGĂ QUIZ", "btn_edit": "🚀 RESCRIE",
        "msg_run": "Se analizează ierarhia și stilul...", "preface": "Prefață", "ack": "Mulțumiri",
        "preview_tit": "📖 Mod Citire", "btn_word": "📥 Descarcă Word", "btn_pdf": "📥 Descarcă PDF",
        "msg_err_idx": "Generează cuprinsul mai întâi.", "msg_success_sync": "Sincronizat!", "label_editor": "Editor Profesional", "welcome": "👋 Bun venit.", "guide": "Folosește bara laterală.",
        "lbl_upload": "📂 Încărcați sursele"
    },
    "Русский": {
        "side_tit": "⚙️ Настройки Редактора", "lbl_tit": "Название Книги", "lbl_auth": "Имя Автора", "lbl_lang": "Язык", 
        "lbl_gen": "Жанр", "lbl_style": "Стиль Написания", "lbl_plot": "Сюжет", "lbl_narrative": "Стиль Повествования", "lbl_goal": "Цель Книги", "lbl_pov": "Точка зрения (Местоимение)",
        "btn_res": "🔄 СБРОСИТЬ ПРОЕКТ", "tabs": ["📊 1. Оглавление", "✍️ 2. Текст и Тест", "📖 3. Просмотр", "📑 4. Export"],
        "btn_idx": "🚀 Создать Оглавление", "btn_sync": "✅ Синхронизировать", "lbl_sec": "Выберите раздел:",
        "btn_write": "✨ НАПИСАТЬ ТЕКСТ", "btn_quiz": "🧠 ДОБАВИТЬ ТЕСТ", "btn_edit": "🚀 ПЕРЕПИСАТЬ",
        "msg_run": "Анализ иерархии и стиля...", "preface": "Предисловие", "ack": "Благодарности",
        "preview_tit": "📖 Режим Чтения", "btn_word": "📥 Скачать Word", "btn_pdf": "📥 Скачать PDF",
        "msg_err_idx": "Сначала создайте оглавление.", "msg_success_sync": "Синхронизировано!", "label_editor": "Профессиональный Редактор", "welcome": "👋 Добро пожаловать.", "guide": "Используйте боковую панель.",
        "lbl_upload": "📂 Загрузить источники"
    },
    "العربية": {
        "side_tit": "⚙️ إعدادات المحرر", "lbl_tit": "عنوان الكتاب", "lbl_auth": "اسم المؤلف", "lbl_lang": "اللغة", 
        "lbl_gen": "النوع الأدبي", "lbl_style": "أسلوب الكتابة", "lbl_plot": "الحبكة أو الموضوع", "lbl_narrative": "الأسلوب السردي", "lbl_goal": "هدف الكتاب", "lbl_pov": "وجهة النظر (الضمير)",
        "btn_res": "🔄 إعادة ضبط المشروع", "tabs": ["📊 1. الفهرس", "✍️ 2. الكتابة والاختبار", "📖 3. معاينة", "📑 4. تصدير"],
        "btn_idx": "🚀 إنشاء فهرس احترافي", "btn_sync": "✅ حفظ ومزامنة الفصول", "lbl_sec": "اختر القسم:",
        "btn_write": "✨ كتابة المحتوى", "btn_quiz": "🧠 إضافة اختبار", "btn_edit": "🚀 إعادة صياغة",
        "msg_run": "جاري تحليل التسلسل الهرمي والأسلوب...", "preface": "مقدمة", "ack": "شكر وتقدير",
        "preview_tit": "📖 عرض القراءة الاحترافي", "btn_word": "📥 تحميل Word", "btn_pdf": "📥 تحميل PDF",
        "msg_err_idx": "قم بإنشاء الفهرس أولاً.", "msg_success_sync": "تمت المزامنة!", "label_editor": "محرر نصوص احترافي", "welcome": "👋 مرحباً بك.", "guide": "استخدم الشريط الجانبي.",
        "lbl_upload": "📂 تحميل المصادر"
    },
    "中文": {
        "side_tit": "⚙️ 编辑器设置", "lbl_tit": "书名", "lbl_auth": "作者姓名", "lbl_lang": "语言", 
        "lbl_gen": "文学体裁", "lbl_style": "写作类型", "lbl_plot": "情节或主题", "lbl_narrative": "叙事风格", "lbl_goal": "书籍目标", "lbl_pov": "叙事视角 (代词)",
        "btn_res": "🔄 重置项目", "tabs": ["📊 1. 目录", "✍️ 2. 写作与测试", "📖 3. 预览", "📑 4. 导出"],
        "btn_idx": "🚀 生成专业目录", "btn_sync": "✅ 保存并同步章节", "lbl_sec": "选择章节:",
        "btn_write": "✨ 编写内容", "btn_quiz": "🧠 添加测试", "btn_edit": "🚀 用AI重写",
        "msg_run": "正在分析层级、风格和情感目标...", "preface": "前言", "ack": "致谢",
        "preview_tit": "📖 专业阅读视图", "btn_word": "📥 下载 Word", "btn_pdf": "📥 下载 PDF",
        "msg_err_idx": "请先生成目录。", "msg_success_sync": "已同步！", "label_editor": "专业文本编辑器", "welcome": "👋 欢迎。", "guide": "请使用左侧边栏设置书籍参数。",
        "lbl_upload": "📂 上传资料"
    }
}

# ======================================================================================================================
# 3. BLOCCO CSS: SIDEBAR SCURA E PULSANTI (INVARIATO)
# ======================================================================================================================
st.markdown("""
<style>
#MainMenu, footer, header, [data-testid="stHeader"] {visibility: hidden;}
[data-testid="collapsedControl"] { display: none !important; }

section[data-testid="stSidebar"] { 
    min-width: 420px !important; max-width: 420px !important; 
    background-color: #1e1e1e !important; border-right: 1px solid #333;
}
section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, 
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
.stButton>button {
    width: 100% !important; border-radius: 10px !important; height: 4.2em !important; 
    font-weight: bold !important; background-color: #1e1e1e !important; color: #ffffff !important;
    font-size: 18px !important; border: 2px solid #333 !important; 
    box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.4) !important; transition: all 0.3s ease !important;
}
.stButton>button:hover { 
    background-color: #333333 !important; border-color: #007BFF !important; 
    color: #007BFF !important; transform: translateY(-2px) !important;
}
.preview-box {
    background-color: #ffffff !important; padding: 80px; border: 1px solid #ccc; 
    border-radius: 4px; height: 900px; overflow-y: scroll;
    font-family: 'Times New Roman', serif; line-height: 2.0; 
    color: #111 !important; box-shadow: 0px 25px 60px rgba(0,0,0,0.2); margin: 0 auto;
}
.custom-title {
    font-size: 38px; font-weight: 900; color: #111; text-align: center;
    padding: 30px; background-color: #ffffff; border-radius: 12px;
    margin-bottom: 30px; border-bottom: 6px solid #1e1e1e;
}
div[data-baseweb="select"] > div { background-color: #2b2b2b !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# ======================================================================================================================
# 4. GESTIONE EXPORT PDF (INVARIATO)
# ======================================================================================================================
class EbookPDF(FPDF):
    def __init__(self, titolo, autore):
        super().__init__()
        self.titolo = self._clean(titolo)
        self.autore = self._clean(autore)
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        
    def _clean(self, txt):
        if not txt: return ""
        replacements = {'“': '"', '”': '"', '‘': "'", '’': "'", '—': '-', '–': '-', '…': '...'}
        for k, v in replacements.items(): 
            txt = txt.replace(k, v)
        return txt.encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 9); self.set_text_color(150)
            self.cell(0, 10, f"{self.titolo} - {self.autore}", 0, 0, 'R'); self.ln(15)
            
    def footer(self):
        self.set_y(-20); self.set_font('Arial', 'I', 9)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def cover_page(self):
        self.add_page(); self.set_font('Arial', 'B', 32); self.ln(100)
        self.multi_cell(0, 15, self.titolo.upper(), 0, 'C'); self.ln(20)
        self.set_font('Arial', 'I', 20); self.cell(0, 10, f"di {self.autore}", 0, 1, 'C')
        
    def add_content(self, title, content):
        self.add_page(); self.ln(15); self.set_font('Arial', 'B', 22)
        self.multi_cell(0, 15, self._clean(title).upper(), 0, 'L'); self.ln(10); self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, self._clean(content))

# ======================================================================================================================
# 5. CORE LOGIC GPT-4o & ANALISI QUALITÀ
# ======================================================================================================================
def chiedi_gpt(prompt, system_prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            temperature=0.75 
        )
        testo = response.choices[0].message.content.strip()
        prefissi = ["ecco", "certamente", "sicuramente", "ok", "here is", "sure"]
        righe = [l for l in testo.split("\n") if not any(l.lower().startswith(p) for p in prefissi)]
        return "\n".join(righe).strip()
    except Exception as e: return f"ERRORE: {str(e)}"

def analizza_qualita_prosa(testo):
    if not testo or len(testo) < 50: 
        return "⚠️ Testo troppo breve per un'analisi sintattica significativa."
    risultati = ["📊 **REPORT LINTER AVANZATO E ANALISI SINTATTICA**\n"]
    parole = re.findall(r'\b\w+\b', testo.lower())
    frasi = [f.strip() for f in re.split(r'[.!?]+', testo) if len(f.strip()) > 5]
    tot_parole = len(parole)
    tot_frasi = len(frasi) if len(frasi) > 0 else 1
    vocabolo_unico = len(set(parole))
    indice_diversita = (vocabolo_unico / tot_parole) * 100 if tot_parole > 0 else 0
    if indice_diversita < 35:
        risultati.append(f"⚠️ **Vocabolario Ripetitivo**: Indice ({indice_diversita:.1f}%).")
    else:
        risultati.append(f"✅ **Ricchezza Lessicale**: ({indice_diversita:.1f}%).")
    parole_per_frase = tot_parole / tot_frasi
    if parole_per_frase > 30:
        risultati.append(f"⚠️ **Sintassi Pesante**: ({parole_per_frase:.1f} parole/frase).")
    else:
        risultati.append(f"✅ **Ritmo e Leggibilità**: ({parole_per_frase:.1f} parole/frase).")
    return "\n\n".join(risultati)

def sync_capitoli():
    testo_indice = st.session_state.get("indice_raw", "")
    if not testo_indice: st.session_state['lista_capitoli'] = []; return
    lista = []
    regex = r'(?i)(Capitolo|Chapter|Kapitel|Capítulo|Раздел|章节|Secţiune|Parte|\d+\.)'
    for riga in testo_indice.split('\n'):
        if re.search(regex, riga.strip()): lista.append(riga.strip())
    st.session_state['lista_capitoli'] = lista

def valuta_approccio_neurologico(genere, stile, narrativa):
    trigger_neuro_stile = ["Persuasivo (Neuromarketing Applicato)", "Conversazionale ed Empatico", "Storytelling Immersivo", "Epico ed Evocativo"]
    trigger_neuro_narrativa = ["Coinvolgente e Narrativo", "Ispirazionale e Motivante", "Storytelling Emozionale", "Diretto e Pratico (Action-oriented)"]
    trigger_neuro_genere = ["Business & Marketing", "Manuale Psicologico", "Romanzo Rosa", "Thriller / Noir", "Spirituale / Esoterico"]
    if stile in trigger_neuro_stile or narrativa in trigger_neuro_narrativa or genere in trigger_neuro_genere:
        return True
    return False

# ======================================================================================================================
# 6. SIDEBAR: SETUP EDITORIALE AVANZATO + CARICAMENTO DOCUMENTI
# ======================================================================================================================
with st.sidebar:
    lingua_sel = st.selectbox("🌐 Lingua / Language", list(TRADUZIONI.keys()))
    L = TRADUZIONI.get(lingua_sel, TRADUZIONI["Italiano"])
    st.title(L["side_tit"])
    val_titolo = st.text_input(L["lbl_tit"])
    val_autore = st.text_input(L["lbl_auth"])
    
    # --- NUOVA SEZIONE CARICAMENTO DOCUMENTI ---
    st.markdown("---")
    st.subheader(L.get("lbl_upload", "📂 Carica Fonti"))
    file_caricati = st.file_uploader("", type=['pdf', 'docx'], accept_multiple_files=True)
    
    if file_caricati:
        # Limitiamo l'analisi ai primi 10 file
        files_to_process = file_caricati[:10]
        if len(file_caricati) > 10:
            st.warning("Massimo 10 file consentiti. Verranno analizzati solo i primi 10.")
        
        with st.spinner("Analisi documenti in corso..."):
            testo_estratto = estrai_testo_da_files(files_to_process)
            # Salviamo il testo in session_state per passarlo all'IA
            st.session_state["conoscenza_extra"] = testo_estratto
            if testo_estratto:
                st.success(f"Analisi completata: {len(files_to_process)} file processati.")
    else:
        st.session_state["conoscenza_extra"] = ""

    st.markdown("---")
    lista_gen = ["Saggio Scientifico", "Quiz Scientifico", "Manuale Tecnico", "Religioso / Teologico", "Spirituale / Esoterico", "Meditazione / Mindfulness", "Business & Marketing", "Romanzo Rosa", "Thriller / Noir", "Fantasy", "Fantascienza", "Manuale Psicologico", "Biografia", "Ricettario", "Test Prep (Preparazione Esami)", "Narrativo", "Romanzo Classico", "Contemporaneo"]
    val_genere = st.selectbox(L["lbl_gen"], lista_gen)
    
    stili_estesi = ["Standard", "Professionale Accademico", "Persuasivo (Neuromarketing Applicato)", "Conversazionale ed Empatico", "Scientifico Divulgativo", "Storytelling Immersivo", "Giornalistico d'Inchiesta", "Socratico (Dialogico / Riflessivo)", "Epico ed Evocativo", "Minimalista ed Essenziale"]
    val_stile = st.selectbox(L["lbl_style"], stili_estesi)
    
    st.markdown("---")
    val_narrativa = st.selectbox(L["lbl_narrative"], ["Coinvolgente e Narrativo", "Tecnico e Analitico", "Ispirazionale e Motivante", "Socratico (Domanda/Risposta)", "Storytelling Emozionale", "Diretto e Pratico (Action-oriented)"])
    
    lista_pov = ["Tu (Diretto, confidenziale e personale)", "Voi (Plurale, autorevole e rispettoso)", "Noi (Inclusivo, partecipativo e didattico)", "Impersonale / Terza Persona (Distaccato, analitico, oggettivo)"]
    val_pov = st.selectbox(L.get("lbl_pov", "Punto di Vista (Pronome)"), lista_pov)
    
    val_goal = st.text_input(L["lbl_goal"], placeholder="Es: Mantenere l'attenzione alta...")
    val_trama = st.text_area(L["lbl_plot"], height=150)
    
    if st.button(L["btn_res"]):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# ======================================================================================================================
# 7. LOGICA DI MEMORIA E CONTESTO (INTEGRAZIONE FONTI)
# ======================================================================================================================
def genera_contesto_avanzato(sezione_corrente):
    contesto = ""
    # Se l'utente ha caricato dei documenti, vengono passati come base di conoscenza prioritaria
    if st.session_state.get("conoscenza_extra"):
        # Passiamo una porzione significativa ma compatibile con i limiti di context window
        contesto += f"=== CONOSCENZA ESTRATTA DAI DOCUMENTI CARICATI (FONTI) ===\n{st.session_state['conoscenza_extra'][:7000]}\n\n"
        contesto += "Nota: Utilizza i dati e le informazioni delle fonti qui sopra per dare autorevolezza e precisione al testo.\n\n"

    for s in st.session_state.get("lista_capitoli", []):
        if s == sezione_corrente: break
        k = f"txt_{s.replace(' ', '_').replace('.', '')}"
        if k in st.session_state and st.session_state[k].strip():
            contesto += f"- Trattato in {s}: [Sintesi: {st.session_state[k][:150]}...]\n"
    return contesto

# ======================================================================================================================
# 8. UI PRINCIPALE & GENERAZIONE PROMPT DINAMICO
# ======================================================================================================================
st.markdown(f'<div class="custom-title">AI di Antonino: {val_titolo if val_titolo else "Ebook Creator PRO"}</div>', unsafe_allow_html=True)

sync_capitoli()
lista_cap_base = st.session_state.get("lista_capitoli", [])
opzioni_editor = [L["preface"]] + lista_cap_base + [L["ack"]]

if val_titolo and val_trama:
    usa_tre_cervelli = valuta_approccio_neurologico(val_genere, val_stile, val_narrativa)
    
    # Blocco Neuromarketing Originale
    if usa_tre_cervelli:
        modulo_stilistico = """=== METODOLOGIA DEI 3 CERVELLI ===
1. CERVELLO RETTILE: Linguaggio netto, contrasti forti.
2. CERVELLO LIMBICO: Storytelling, empatia, dopamina/ossitocina.
3. NEOCORTECCIA: Struttura, dati logici."""
    else:
        modulo_stilistico = "=== APPROCCIO ANALITICO === Mantieni un tono rigoroso, accademico e fattuale."

    # Prompt di Sistema Potenziato
    S_PROMPT = f"""
Sei un esperto Madrelingua in {lingua_sel}, Editor e Luminare mondiale nel campo '{val_genere}'. 
Stai redigendo l'ebook '{val_titolo}'. 

PARAMETRI EDITORIALI:
- Genere: {val_genere} | Stile: {val_stile} | POV: {val_pov}
- Lingua: {lingua_sel}

{modulo_stilistico}

=== REGOLE HARD ===
1. CONFORMITÀ FONTI: Se sono presenti informazioni nelle 'FONTI' caricate, usale come riferimento principale per dati e fatti.
2. POV COERENTE: Usa sempre il punto di vista richiesto ({val_pov}).
3. SINTASSI PULITA: No emoji, no asterischi eccessivi. Solo testo da libro stampato.
4. SILENZIO STAMPA: Se scrivi un Capitolo, non anticipare i Sottocapitoli.
"""

    tabs = st.tabs(L["tabs"])

    # TAB 1: INDICE
    with tabs[0]:
        if st.button(L["btn_idx"]):
            with st.spinner("Creazione indice..."):
                # Se ci sono fonti, l'IA deve analizzarle per creare l'indice
                prompt_idx = f"Crea l'indice per '{val_titolo}' basandoti sulla trama: {val_trama}."
                if st.session_state.get("conoscenza_extra"):
                    prompt_idx += f"\n\nUsa queste fonti per strutturare i capitoli in modo tecnico: {st.session_state['conoscenza_extra'][:4000]}"
                
                prompt_idx += f"\n\nFormato: Parte I, Capitolo 1, 1.1, 1.2. Lingua: {lingua_sel}."
                st.session_state["indice_raw"] = chiedi_gpt(prompt_idx, S_PROMPT)
                sync_capitoli(); st.rerun()
        
        testo_input = st.text_area("Indice:", value=st.session_state.get("indice_raw", ""), height=400)
        if testo_input != st.session_state.get("indice_raw", ""):
            st.session_state["indice_raw"] = testo_input
        if st.button(L["btn_sync"]): sync_capitoli(); st.rerun()

    # TAB 2: SCRITTURA & QUIZ
    with tabs[1]:
        if not lista_cap_base: st.warning(L["msg_err_idx"])
        else:
            sez_scelta = st.selectbox(L["lbl_sec"], opzioni_editor)
            k_sessione = f"txt_{sez_scelta.replace(' ', '_').replace('.', '')}"
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                if st.button(L["btn_write"]):
                    with st.spinner(L["msg_run"]):
                        memoria = genera_contesto_avanzato(sez_scelta)
                        full_prompt = f"Scrivi la sezione: '{sez_scelta}'.\n\nCONTENUTO E FONTI:\n{memoria}\n\nObiettivo: {val_goal}."
                        st.session_state[k_sessione] = chiedi_gpt(full_prompt, S_PROMPT)
                        st.rerun()
            with c2:
                istr = st.text_input(L["btn_edit"], key=f"mod_{k_sessione}")
                if st.button(L["btn_edit"] + " 🪄"):
                    st.session_state[k_sessione] = chiedi_gpt(f"Rielabora: {istr}\nTesto:\n{st.session_state.get(k_sessione, '')}", S_PROMPT)
                    st.rerun()
            with c3:
                if st.button("🧠 QUIZ"):
                    res_q = chiedi_gpt(f"Crea quiz su:\n{st.session_state.get(k_sessione, '')}", "Learning Expert.")
                    st.session_state[k_sessione] += "\n\n### TEST\n" + res_q; st.rerun()

            st.session_state[k_sessione] = st.text_area(L["label_editor"], value=st.session_state.get(k_sessione, ""), height=500)

    # TAB 3: ANTEPRIMA (CODICE ORIGINALE)
    with tabs[2]:
        st.subheader(L["preview_tit"])
        html_p = f"<div class='preview-box'><h1 style='text-align:center;'>{val_titolo.upper()}</h1><hr>"
        for s in opzioni_editor:
            sk = f"txt_{s.replace(' ', '_').replace('.', '')}"
            if sk in st.session_state and st.session_state[sk].strip():
                html_p += f"<h2>{s.upper()}</h2><p>{st.session_state[sk].replace(chr(10), '<br>')}</p>"
        st.markdown(html_p + "</div>", unsafe_allow_html=True)

    # TAB 4: ESPORTAZIONE (CODICE ORIGINALE)
    with tabs[3]:
        cw, cp = st.columns(2)
        with cw:
            if st.button(L["btn_word"]):
                doc = Document(); doc.add_heading(val_titolo, 0)
                for s in opzioni_editor:
                    ke = f"txt_{s.replace(' ', '_').replace('.', '')}"
                    if ke in st.session_state: doc.add_heading(s.upper(), level=1); doc.add_paragraph(st.session_state[ke])
                bw = BytesIO(); doc.save(bw); bw.seek(0); st.download_button(L["btn_word"], data=bw, file_name=f"{val_titolo}.docx")
        with cp:
            if st.button(L["btn_pdf"]):
                pdf = EbookPDF(val_titolo, val_autore); pdf.cover_page()
                for s in opzioni_editor:
                    kd = f"txt_{s.replace(' ', '_').replace('.', '')}"
                    if kd in st.session_state: pdf.add_content(s.upper(), st.session_state[kd])
                out_p = pdf.output(dest='S').encode('latin-1', 'replace'); st.download_button(L["btn_pdf"], data=out_p, file_name=f"{val_titolo}.pdf")
else:
    st.info(L["welcome"] + " " + L["guide"])
