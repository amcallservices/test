import uuid
import streamlit as st

COMMERCIAL_TEST_VERSION = "commercial-test-01"
DEMO_INITIAL_CREDITS = 120
AI_REQUEST_CREDITS = 1


class CommercialCreditError(RuntimeError):
    pass


def _init_account():
    if "commercial_user_context" not in st.session_state:
        st.session_state["commercial_user_context"] = {
            "id": f"demo-{uuid.uuid4().hex}",
            "email": "demo@scrittore-site.local",
        }
        st.session_state["commercial_demo_credits"] = DEMO_INITIAL_CREDITS
        st.session_state["commercial_demo_ledger"] = []


def _balance():
    return int(st.session_state.get("commercial_demo_credits", DEMO_INITIAL_CREDITS))


def _movement(reason, delta):
    st.session_state["commercial_demo_ledger"].append(
        {
            "operazione": reason,
            "crediti": delta,
        }
    )


def charge_credits(reason="generazione_ia", amount=AI_REQUEST_CREDITS):
    _init_account()

    if _balance() < amount:
        raise CommercialCreditError(
            "Crediti insufficienti. Usa una ricarica demo nella sidebar."
        )

    st.session_state["commercial_demo_credits"] = _balance() - amount
    reference = uuid.uuid4().hex
    _movement(reason, -amount)
    return reference


def refund_credits(reference, reason="errore_generazione", amount=AI_REQUEST_CREDITS):
    _init_account()
    st.session_state["commercial_demo_credits"] = _balance() + amount
    _movement(reason, amount)


def bootstrap_commercial_test():
    _init_account()

    with st.sidebar:
        st.divider()
        st.markdown("### 💳 Crediti di test")
        st.caption("Modalità demo: nessun pagamento reale.")

        st.metric("Saldo disponibile", f"{_balance()} crediti")
        st.caption("Ogni richiesta IA costa 1 credito demo.")

        with st.expander("Ricarica crediti demo"):
            if st.button("Aggiungi 100 crediti demo", key="demo_100"):
                st.session_state["commercial_demo_credits"] = _balance() + 100
                _movement("ricarica_demo", 100)
                st.rerun()

            if st.button("Aggiungi 300 crediti demo", key="demo_300"):
                st.session_state["commercial_demo_credits"] = _balance() + 300
                _movement("ricarica_demo", 300)
                st.rerun()

        with st.expander("Movimenti demo"):
            movements = st.session_state.get("commercial_demo_ledger", [])[-10:]
            st.write(movements or "Nessun movimento ancora.")
