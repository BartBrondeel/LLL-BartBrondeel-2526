"""
=============================================================
  app.py — Quiz App met Streamlit UI
  Opdracht:  Portfolio - 100 Days of Code
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee

  Beschrijving:
  ------------
  De Quiz App omgezet naar een Streamlit webinterface.
  Streamlit laat ons toe om met pure Python een
  interactieve webpagina te maken, zonder HTML of JavaScript.

  Starten:
  --------
      streamlit run app.py

  Hoe werkt Streamlit state?
  --------------------------
  Normale Python variabelen worden opnieuw aangemaakt
  elke keer de pagina herlaadt (bij elke klik).
  st.session_state is een speciale dictionary die waarden
  BIJHOUDT tussen herladingen — essentieel voor een quiz!

  Streamlit functies gebruikt in dit bestand:
  --------------------------------------------
  st.set_page_config(...)
      Paginatitel en icoon instellen (moet als eerste staan).

  st.title(tekst)
      Grote hoofdtitel bovenaan de pagina.

  st.subheader(tekst)
      Kleinere ondertitel.

  st.markdown(tekst)
      Opgemaakte tekst tonen (ondersteunt Markdown en HTML).

  st.progress(waarde)
      Voortgangsbalk tussen 0.0 en 1.0.

  st.columns(aantal)
      Pagina opdelen in kolommen naast elkaar.

  st.button(label)
      Knop die True geeft wanneer erop geklikt wordt.

  st.success(tekst)
      Groene succesboodschap tonen.

  st.error(tekst)
      Rode foutboodschap tonen.

  st.info(tekst)
      Blauwe informatieboodschap tonen.

  st.balloons()
      Geanimeerde ballonnen bij een goed resultaat 🎈

  st.session_state
      Dictionary die data bijhoudt tussen pagina-herladingen.
      Gebruik: st.session_state["sleutel"] = waarde

  st.rerun()
      Herlaadt de volledige pagina (na een klik verwerken).

  ============================================================
  SAMENVATTING GEBRUIKTE METHODES (eigen code)
  ============================================================

  build_question_list(data) → list
      Zet een lijst van dicts om naar Question objecten.
      Gebruikt list comprehension.

  initialize_session_state()
      Controleert of de Streamlit state al bestaat.
      Zo niet: maak de begintoestand aan.
      Voorkomt dat de quiz herstart bij elke paginaherlaad.

  get_current_question() → Question | None
      Geeft het huidige Question object terug op basis van
      het vraagnummer in de state.
      Geeft None terug als alle vragen gesteld zijn.

  handle_answer(user_answer, correct_answer)
      Verwerkt het antwoord van de gebruiker:
      - Verhoogt de score indien correct
      - Slaat het resultaat op in de state
      - Verhoogt het vraagnummer

  show_question_card(question, question_number, total)
      Toont de huidige vraag met True/False knoppen.

  show_result_feedback()
      Toont groene of rode feedback na een antwoord.

  show_final_score()
      Toont het eindscherm met totale score en percentage.

  reset_quiz()
      Zet alle state terug naar de begintoestand.
  ============================================================
=============================================================
"""

# --- Externe bibliotheken ---
import streamlit as st   # Webinterface

# --- Eigen modules ---
from question_model import Question
from question_data import QUESTION_DATA


# =====================
#  Pagina configuratie
# =====================
# set_page_config() MOET als allereerste Streamlit-aanroep staan
st.set_page_config(
    page_title="Quiz App",
    page_icon="🧠",
    layout="centered",       # Inhoud gecentreerd op de pagina
    initial_sidebar_state="collapsed",
)


# =====================
#  Hulpfuncties
# =====================

def build_question_list(data: list) -> list:
    """
    Zet de ruwe data (lijst van dicts) om naar Question objecten.

    Parameters:
    -----------
    data : Lijst van dicts met "question" en "correct_answer"

    Geeft terug:
    ------------
    list : Lijst van Question objecten
    """
    # List comprehension: korte manier om een nieuwe lijst te maken
    return [
        Question(item["question"], item["correct_answer"])
        for item in data
    ]


def initialize_session_state(question_bank: list):
    """
    Maakt de Streamlit session state aan als die nog niet bestaat.

    session_state is een dictionary die waarden bijhoudt
    tussen pagina-herladingen. Zonder session_state zou de
    quiz elke keer opnieuw beginnen bij een klik.

    We controleren met "not in" zodat bestaande state
    niet overschreven wordt bij elke herlaad.

    Parameters:
    -----------
    question_bank : Lijst van Question objecten
    """
    # Huidige vraagnummer (start bij 0)
    if "question_number" not in st.session_state:
        st.session_state["question_number"] = 0

    # Huidige score (aantal correcte antwoorden)
    if "score" not in st.session_state:
        st.session_state["score"] = 0

    # De volledige vragenlijst opslaan in state
    if "question_bank" not in st.session_state:
        st.session_state["question_bank"] = question_bank

    # Feedback na een antwoord: None, "correct" of "wrong"
    if "last_result" not in st.session_state:
        st.session_state["last_result"] = None

    # Het correcte antwoord van de vorige vraag (voor feedback)
    if "last_correct_answer" not in st.session_state:
        st.session_state["last_correct_answer"] = None


def get_current_question() -> Question | None:
    """
    Geeft het huidige Question object terug.

    Geeft terug:
    ------------
    Question als er nog vragen zijn, anders None
    """
    current_number = st.session_state["question_number"]
    bank = st.session_state["question_bank"]

    # Controleer of we nog binnen de lijst zitten
    if current_number < len(bank):
        return bank[current_number]

    return None  # Alle vragen zijn gesteld


def handle_answer(user_answer: str, correct_answer: str):
    """
    Verwerkt het antwoord van de gebruiker.

    Vergelijkt het antwoord, past de score aan,
    slaat het resultaat op in state en verhoogt
    het vraagnummer.

    Parameters:
    -----------
    user_answer    : "True" of "False" (van de knop)
    correct_answer : Het correcte antwoord van de vraag
    """
    # Sla het correcte antwoord op voor de feedback
    st.session_state["last_correct_answer"] = correct_answer

    # Vergelijk antwoorden (case-insensitive)
    if user_answer.lower() == correct_answer.lower():
        # Correct antwoord
        st.session_state["score"] += 1
        st.session_state["last_result"] = "correct"
    else:
        # Fout antwoord
        st.session_state["last_result"] = "wrong"

    # Ga naar de volgende vraag
    st.session_state["question_number"] += 1


def reset_quiz():
    """
    Zet de volledige quiz terug naar de begintoestand.
    Wordt aangeroepen als de gebruiker opnieuw wil spelen.
    """
    st.session_state["question_number"] = 0
    st.session_state["score"] = 0
    st.session_state["last_result"] = None
    st.session_state["last_correct_answer"] = None


def show_result_feedback():
    """
    Toont groene of rode feedback op basis van het laatste antwoord.
    Wordt alleen getoond als er een antwoord is (last_result != None).
    """
    result = st.session_state["last_result"]
    correct = st.session_state["last_correct_answer"]

    if result == "correct":
        st.success(f"✅ Correct! Het juiste antwoord was: **{correct}**")
    elif result == "wrong":
        st.error(f"❌ Fout! Het juiste antwoord was: **{correct}**")


def show_question_card(question: Question, question_number: int, total: int):
    """
    Toont de huidige vraag met voortgangsbalk en True/False knoppen.

    Parameters:
    -----------
    question        : Het huidige Question object
    question_number : Het vraagnummer (1-gebaseerd voor weergave)
    total           : Totaal aantal vragen
    """
    # Voortgangsbalk: hoe ver zijn we? (0.0 tot 1.0)
    progress_value = question_number / total
    st.progress(progress_value)
    st.caption(f"Vraag {question_number} van {total}")

    # Toon de vraagtekst in een opvallend kader
    st.markdown(
        f"""
        <div style="
            background-color: #1e3a5f;
            border-left: 5px solid #4fc3f7;
            border-radius: 8px;
            padding: 20px 25px;
            margin: 15px 0;
        ">
            <p style="
                color: #ffffff;
                font-size: 1.2rem;
                font-weight: 500;
                margin: 0;
                line-height: 1.6;
            ">{question.text}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Twee knoppen naast elkaar: True en False
    # st.columns(2) maakt twee gelijke kolommen
    col_true, col_false = st.columns(2)

    with col_true:
        # Als op True geklikt: verwerk het antwoord
        if st.button("✅  TRUE", use_container_width=True, type="primary"):
            handle_answer("True", question.answer)
            st.rerun()  # Herlaad de pagina om de volgende vraag te tonen

    with col_false:
        # Als op False geklikt: verwerk het antwoord
        if st.button("❌  FALSE", use_container_width=True):
            handle_answer("False", question.answer)
            st.rerun()


def show_final_score():
    """
    Toont het eindscherm met de totale score, percentage
    en een boodschap op basis van het resultaat.
    """
    score = st.session_state["score"]
    total = len(st.session_state["question_bank"])
    percentage = round((score / total) * 100, 1) if total > 0 else 0

    st.markdown("---")
    st.title("🏁 Quiz Afgerond!")

    # Score tonen in grote tekst
    st.markdown(
        f"""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 4rem; color: #4fc3f7;">{score}/{total}</h1>
            <p style="font-size: 1.5rem; color: #aaaaaa;">{percentage}% correct</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Boodschap op basis van de score
    if percentage == 100:
        st.balloons()  # Geanimeerde ballonnen bij perfecte score!
        st.success("🏆 Perfect! Alle vragen correct!")
    elif percentage >= 80:
        st.success("🌟 Uitstekend gedaan!")
    elif percentage >= 60:
        st.info("👍 Goed bezig!")
    elif percentage >= 40:
        st.warning("💪 Kan beter, probeer opnieuw!")
    else:
        st.error("📚 Blijf oefenen, het komt goed!")

    st.markdown("---")

    # Knop om opnieuw te spelen
    if st.button("🔄  Opnieuw Spelen", use_container_width=True, type="primary"):
        reset_quiz()
        st.rerun()


# =====================
#  Hoofdprogramma
# =====================

def main():
    """
    Hoofdfunctie: bouwt de volledige Streamlit pagina op.

    Streamlit voert dit bestand van boven naar beneden uit
    bij elke interactie. session_state zorgt ervoor dat
    de quizvoortgang bewaard blijft tussen die uitvoeringen.
    """
    # Stap 1: Bouw de vragenlijst
    question_bank = build_question_list(QUESTION_DATA)

    # Stap 2: Initialiseer de state (alleen de eerste keer)
    initialize_session_state(question_bank)

    # Stap 3: Paginaopbouw — titel en score bovenaan
    st.title("🧠 Quiz App")

    # Score altijd zichtbaar bovenaan
    score = st.session_state["score"]
    question_number = st.session_state["question_number"]
    total = len(question_bank)

    st.markdown(
        f"**Score:** {score} / {min(question_number, total)} &nbsp;|&nbsp; "
        f"**Vragen beantwoord:** {min(question_number, total)} / {total}"
    )
    st.markdown("---")

    # Stap 4: Toon feedback van het vorige antwoord (indien aanwezig)
    show_result_feedback()

    # Stap 5: Toon de huidige vraag OF het eindscherm
    current_question = get_current_question()

    if current_question is not None:
        # Er zijn nog vragen — toon de huidige vraag
        # question_number is 0-gebaseerd, +1 voor weergave
        show_question_card(current_question, question_number + 1, total)
    else:
        # Alle vragen zijn beantwoord — toon het eindscherm
        show_final_score()


# Start het programma
main()
