"""Invio di email agli utenti dal pannello di amministratore (Gmail via SMTP).

Segreti di Streamlit necessari:
    EMAIL_SMTP_USER     = "tuoindirizzo@gmail.com"
    EMAIL_SMTP_PASSWORD = "password per le app di Google (16 lettere)"
Facoltativi:
    EMAIL_FROM_NAME     = "Scrittore Site"      (nome mostrato come mittente)
    EMAIL_SMTP_HOST     = "smtp.gmail.com"
    EMAIL_SMTP_PORT     = "465"

Ogni destinatario riceve un'email separata (nessuno vede gli indirizzi degli
altri) con un link personale per non ricevere più queste comunicazioni.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import smtplib
import ssl
import time
from email.message import EmailMessage
from email.utils import formataddr, make_msgid
from html import escape
from typing import Callable, Iterable

# Gmail consente circa 500 destinatari al giorno: oltre questa soglia avvisiamo.
LIMITE_GIORNALIERO_GMAIL = 500
PAUSA_TRA_INVII_SECONDI = 0.6


def configurazione_email(segreto: Callable[[str], str]) -> dict | None:
    """Legge la configurazione dai segreti; None se manca utente o password."""
    utente = (segreto("EMAIL_SMTP_USER") or "").strip()
    password = (segreto("EMAIL_SMTP_PASSWORD") or "").replace(" ", "").strip()
    if not utente or not password:
        return None
    try:
        porta = int((segreto("EMAIL_SMTP_PORT") or "465").strip())
    except ValueError:
        porta = 465
    return {
        "utente": utente,
        "password": password,
        "nome": (segreto("EMAIL_FROM_NAME") or "Scrittore Site").strip() or "Scrittore Site",
        "host": (segreto("EMAIL_SMTP_HOST") or "smtp.gmail.com").strip() or "smtp.gmail.com",
        "porta": porta,
    }


# ---------------------------------------------------------------- disiscrizione
def _b64(testo: str) -> str:
    return base64.urlsafe_b64encode(testo.encode("utf-8")).decode("ascii").rstrip("=")


def _da_b64(testo: str) -> str:
    riempimento = "=" * (-len(testo) % 4)
    return base64.urlsafe_b64decode((testo + riempimento).encode("ascii")).decode("utf-8")


def token_disiscrizione(email: str, chiave: str) -> str:
    """Firma dell'indirizzo: solo chi riceve l'email può usare il proprio link."""
    messaggio = email.strip().lower().encode("utf-8")
    return hmac.new(chiave.encode("utf-8"), messaggio, hashlib.sha256).hexdigest()[:32]


def link_disiscrizione(base_url: str, email: str, chiave: str) -> str:
    return f"{base_url.rstrip('/')}/?disiscrivi={_b64(email.strip().lower())}&t={token_disiscrizione(email, chiave)}"


def leggi_disiscrizione(valore: str, token: str, chiave: str) -> str:
    """Restituisce l'email se il link è autentico, altrimenti stringa vuota."""
    try:
        email = _da_b64(str(valore or "")).strip().lower()
    except Exception:
        return ""
    if not email or "@" not in email or not chiave:
        return ""
    if not hmac.compare_digest(token_disiscrizione(email, chiave), str(token or "")):
        return ""
    return email


# ---------------------------------------------------------------- composizione
def corpo_html(testo: str, link_stop: str, nome_mittente: str) -> str:
    """Versione grafica dell'email (colori della home), testo sempre leggibile."""
    paragrafi = "".join(
        f"<p style=\"margin:0 0 14px;font:16px/1.6 Arial,Helvetica,sans-serif;color:#1d1a14\">"
        f"{escape(blocco).replace(chr(10), '<br>')}</p>"
        for blocco in [b.strip() for b in testo.strip().split("\n\n")] if blocco
    )
    return (
        "<!doctype html><html><body style=\"margin:0;padding:0;background:#0a0e1a\">"
        "<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"background:#0a0e1a;padding:28px 12px\">"
        "<tr><td align=\"center\">"
        "<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" style=\"max-width:600px\">"
        f"<tr><td style=\"padding:0 4px 16px;font:600 20px Georgia,serif;color:#f4efe6\">{escape(nome_mittente)}"
        "<div style=\"width:40px;height:3px;background:#f2b84b;margin-top:10px;border-radius:3px\"></div></td></tr>"
        f"<tr><td style=\"background:#f4ecdc;border-radius:16px;padding:28px 26px\">{paragrafi}</td></tr>"
        "<tr><td style=\"padding:18px 6px;font:12px/1.5 Arial,Helvetica,sans-serif;color:#8e99b3\">"
        "Ricevi questa email perché hai un account su Scrittore Site. "
        f"<a href=\"{escape(link_stop, quote=True)}\" style=\"color:#f2b84b\">Non voglio più ricevere queste email</a>."
        "</td></tr></table></td></tr></table></body></html>"
    )


def componi_email(conf: dict, destinatario: str, oggetto: str, testo: str, link_stop: str) -> EmailMessage:
    messaggio = EmailMessage()
    messaggio["From"] = formataddr((conf["nome"], conf["utente"]))
    messaggio["To"] = destinatario
    messaggio["Subject"] = oggetto.strip()
    messaggio["Reply-To"] = conf["utente"]
    messaggio["Message-ID"] = make_msgid(domain=conf["utente"].split("@")[-1])
    # Intestazione standard: Gmail e gli altri mostrano il pulsante "Annulla iscrizione".
    messaggio["List-Unsubscribe"] = f"<{link_stop}>"
    messaggio.set_content(
        f"{testo.strip()}\n\n—\nRicevi questa email perché hai un account su Scrittore Site.\n"
        f"Per non ricevere più queste email: {link_stop}\n"
    )
    messaggio.add_alternative(corpo_html(testo, link_stop, conf["nome"]), subtype="html")
    return messaggio


# ---------------------------------------------------------------- invio
def apri_connessione(conf: dict) -> smtplib.SMTP:
    contesto = ssl.create_default_context()
    if int(conf["porta"]) == 465:
        server: smtplib.SMTP = smtplib.SMTP_SSL(conf["host"], int(conf["porta"]), context=contesto, timeout=30)
    else:
        server = smtplib.SMTP(conf["host"], int(conf["porta"]), timeout=30)
        server.starttls(context=contesto)
    server.login(conf["utente"], conf["password"])
    return server


def invia_a_tutti(
    conf: dict,
    destinatari: Iterable[str],
    oggetto: str,
    testo: str,
    base_url: str,
    chiave_firma: str,
    avanzamento: Callable[[int, int, str], None] | None = None,
    pausa: float = PAUSA_TRA_INVII_SECONDI,
) -> dict:
    """Invia un'email separata a ciascun destinatario. Non si ferma al primo errore."""
    elenco = [d.strip() for d in destinatari if d and "@" in d]
    inviati: list[str] = []
    falliti: list[tuple[str, str]] = []
    server = apri_connessione(conf)
    try:
        for indice, destinatario in enumerate(elenco, start=1):
            link_stop = link_disiscrizione(base_url, destinatario, chiave_firma)
            messaggio = componi_email(conf, destinatario, oggetto, testo, link_stop)
            try:
                server.send_message(messaggio)
                inviati.append(destinatario)
            except smtplib.SMTPServerDisconnected:
                # Gmail chiude a volte le connessioni lunghe: riapriamo e riproviamo una volta.
                try:
                    server = apri_connessione(conf)
                    server.send_message(messaggio)
                    inviati.append(destinatario)
                except Exception as errore:  # noqa: BLE001
                    falliti.append((destinatario, str(errore)[:200]))
            except Exception as errore:  # noqa: BLE001
                falliti.append((destinatario, str(errore)[:200]))
            if avanzamento:
                avanzamento(indice, len(elenco), destinatario)
            if pausa and indice < len(elenco):
                time.sleep(pausa)
    finally:
        try:
            server.quit()
        except Exception:  # noqa: BLE001
            pass
    return {"inviati": inviati, "falliti": falliti}


# ------------------------------------------------- avviso all'amministratore
def componi_avviso_nuovo_utente(conf: dict, destinatari: list[str], email_utente: str,
                                quando: str, invito: str = "", base_url: str = "") -> EmailMessage:
    """Email breve per l'amministratore: si è registrato un nuovo utente."""
    messaggio = EmailMessage()
    messaggio["From"] = formataddr((conf["nome"], conf["utente"]))
    messaggio["To"] = ", ".join(destinatari)
    messaggio["Subject"] = f"Nuovo utente su Scrittore Site: {email_utente}"
    messaggio["Message-ID"] = make_msgid(domain=conf["utente"].split("@")[-1])
    righe = [
        "Si è appena registrato un nuovo utente su Scrittore Site.",
        "",
        f"Email: {email_utente}",
        f"Data e ora: {quando}",
        f"Invitato con il codice: {invito}" if invito else "Invitato da un altro utente: no",
        "",
        "L'account diventa attivo quando l'utente conferma l'email.",
    ]
    if base_url:
        righe.append(f"Pannello amministratore: {base_url.rstrip('/')}/?azione=accedi")
    testo = "\n".join(righe)
    messaggio.set_content(testo + "\n")
    righe_html = "".join(
        f"<p style=\"margin:0 0 8px\">{escape(riga)}</p>" if riga else "<p style=\"margin:0 0 8px\">&nbsp;</p>"
        for riga in righe
    )
    messaggio.add_alternative(
        "<!doctype html><html><body style=\"margin:0;background:#0d1426;padding:24px\">"
        "<div style=\"max-width:560px;margin:auto;background:#f4ecdc;border-radius:16px;padding:24px;"
        "font:15px/1.55 Georgia,serif;color:#1c2540\">"
        "<p style=\"margin:0 0 14px;font:600 13px Arial,sans-serif;letter-spacing:.08em;color:#b07d1c\">"
        "SCRITTORE SITE · NUOVO UTENTE</p>" + righe_html + "</div></body></html>",
        subtype="html",
    )
    return messaggio


def invia_avviso_nuovo_utente(conf: dict, destinatari: list[str], email_utente: str,
                              quando: str, invito: str = "", base_url: str = "") -> None:
    """Invia l'avviso; gli errori vengono sollevati al chiamante."""
    if not conf or not destinatari:
        return
    messaggio = componi_avviso_nuovo_utente(conf, destinatari, email_utente, quando, invito, base_url)
    server = apri_connessione(conf)
    try:
        server.send_message(messaggio)
    finally:
        try:
            server.quit()
        except Exception:
            pass

