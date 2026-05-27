# Quiz App — Streamlit Versie

**Student:** Bart Brondeel  
**Opleiding:** Graduaat Programmeren - Odisee  
**Cursus:** 100 Days of Code — The Complete Python Pro Bootcamp

---

## Beschrijving

Een interactieve True/False quizapplicatie als webpagina, gebouwd met Streamlit.  
De speler klikt op True of False knoppen en ziet meteen feedback.  
Aan het einde verschijnt de eindscore met percentage.

---

## Projectstructuur

```
quiz_app_streamlit/
├── app.py              ← Streamlit webinterface (startpunt)
├── question_model.py   ← Question klasse (1 vraag als object)
├── question_data.py    ← Lijst van vragen (ruwe data)
└── requirements.txt    ← Benodigde bibliotheken
```

---

## Installatie en starten

```bash
pip install -r requirements.txt
streamlit run app.py
```

De app opent automatisch in je browser op `http://localhost:8501`

---

## Gebruikte concepten

| Concept | Waar gebruikt |
|---|---|
| OOP — klassen en objecten | `Question` klasse |
| DRY — data gescheiden van logica | `question_data.py` apart |
| List comprehension | `build_question_list()` |
| `st.session_state` | Score en voortgang bijhouden tussen klikken |
| `st.columns()` | True/False knoppen naast elkaar |
| `st.progress()` | Voortgangsbalk |
| `st.balloons()` | Animatie bij perfecte score |
| `st.rerun()` | Pagina herladen na een antwoord |

---

## Streamlit vs terminal

| | Terminal versie | Streamlit versie |
|---|---|---|
| Interface | Tekst in terminal | Webpagina in browser |
| Interactie | `input()` typen | Knoppen klikken |
| Feedback | `print()` | Gekleurde berichten |
| Voortgang | Tekst | Voortgangsbalk |
