"""Email agli utenti: configurazione, link di disiscrizione e invio (Gmail finto)."""
import smtplib

import email_admin as ea

SEGRETI = {"EMAIL_SMTP_USER": "scrittore@gmail.com", "EMAIL_SMTP_PASSWORD": "abcd efgh ijkl mnop"}


def test_configurazione_letta_dai_segreti():
    conf = ea.configurazione_email(lambda nome: SEGRETI.get(nome, ""))
    assert conf["utente"] == "scrittore@gmail.com"
    assert conf["password"] == "abcdefghijklmnop"  # spazi della password per le app tolti
    assert conf["host"] == "smtp.gmail.com" and conf["porta"] == 465 and conf["nome"] == "Scrittore Site"
    assert ea.configurazione_email(lambda nome: "") is None


def test_link_di_disiscrizione_firmato():
    link = ea.link_disiscrizione("https://sito.app/", "Mario@Email.it", "chiave")
    assert link.startswith("https://sito.app/?disiscrivi=")
    valore = link.split("disiscrivi=")[1].split("&")[0]
    token = link.split("&t=")[1]
    assert ea.leggi_disiscrizione(valore, token, "chiave") == "mario@email.it"
    # Token manomesso, chiave diversa o indirizzo cambiato: rifiutati.
    assert ea.leggi_disiscrizione(valore, "0" * 32, "chiave") == ""
    assert ea.leggi_disiscrizione(valore, token, "altra") == ""
    altro = ea._b64("altro@email.it")
    assert ea.leggi_disiscrizione(altro, token, "chiave") == ""
    assert ea.leggi_disiscrizione("%%%", token, "chiave") == ""


def test_email_composta_con_testo_html_e_annulla_iscrizione():
    conf = ea.configurazione_email(lambda nome: SEGRETI.get(nome, ""))
    msg = ea.componi_email(conf, "a@b.it", "Novità", "Ciao <b>autore</b>\n\nSecondo paragrafo", "https://x/?disiscrivi=1&t=2")
    assert msg["To"] == "a@b.it" and msg["Subject"] == "Novità"
    assert "scrittore@gmail.com" in msg["From"] and msg["List-Unsubscribe"] == "<https://x/?disiscrivi=1&t=2>"
    testo = msg.get_body(("plain",)).get_content()
    html = msg.get_body(("html",)).get_content()
    assert "Secondo paragrafo" in testo and "https://x/?disiscrivi=1&t=2" in testo
    assert "&lt;b&gt;autore&lt;/b&gt;" in html  # il messaggio non può iniettare HTML
    assert "Non voglio più ricevere queste email" in html


class _GmailFinto:
    def __init__(self, rifiuta=()):
        self.inviati, self.rifiuta, self.chiuso = [], set(rifiuta), False

    def send_message(self, msg):
        if msg["To"] in self.rifiuta:
            raise smtplib.SMTPRecipientsRefused({msg["To"]: (550, b"no")})
        self.inviati.append(msg)

    def quit(self):
        self.chiuso = True


def test_invio_separato_a_ciascuno_senza_fermarsi_agli_errori(monkeypatch):
    finto = _GmailFinto(rifiuta={"b@x.it"})
    monkeypatch.setattr(ea, "apri_connessione", lambda conf: finto)
    passi = []
    esito = ea.invia_a_tutti(
        {"utente": "s@gmail.com", "nome": "Scrittore Site", "password": "p", "host": "h", "porta": 465},
        ["a@x.it", "b@x.it", "c@x.it", "non-email"], "Ogg", "Testo", "https://sito.app", "k",
        avanzamento=lambda fatti, totale, ultimo: passi.append((fatti, totale)), pausa=0,
    )
    assert esito["inviati"] == ["a@x.it", "c@x.it"]
    assert [e for e, _ in esito["falliti"]] == ["b@x.it"]
    assert [m["To"] for m in finto.inviati] == ["a@x.it", "c@x.it"]  # un'email per persona
    assert all("?disiscrivi=" in m["List-Unsubscribe"] for m in finto.inviati)
    assert passi[-1] == (3, 3) and finto.chiuso
