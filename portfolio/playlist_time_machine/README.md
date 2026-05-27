# Playlist Tijdmachine — Streamlit Versie

**Student:** Bart Brondeel  
**Opleiding:** Graduaat Programmeren - Odisee  
**Cursus:** 100 Days of Code — The Complete Python Pro Bootcamp

---

## Beschrijving

Een interactieve webapplicatie gebouwd met Streamlit.  
Kies een datum via een datumkiezer en ontdek welke nummers populair waren  
op de Billboard Hot 100 op die dag.

---

## Projectstructuur

```
playlist_tijdmachine_streamlit/
├── app.py            ← Streamlit webinterface (alles in één bestand)
└── requirements.txt  ← Benodigde bibliotheken
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

| Concept | Beschrijving |
|---|---|
| `requests` + BeautifulSoup | Billboard website ophalen en scrapen |
| `st.date_input()` | Datumkiezer widget |
| `st.slider()` | Aantal nummers instellen |
| `st.spinner()` | Laadanimatie tijdens ophalen |
| `st.metric()` | Statistieken tonen |
| `st.markdown()` met HTML | Opgemaakte nummerslijst met kleuren |
| Demo-modus | Fallback als Billboard niet bereikbaar is |

---

## Noot over Billboard

Billboard.com kan geautomatiseerde verzoeken soms blokkeren (statuscode 403).  
De app schakelt dan automatisch over naar **demo-modus** met echte historische data.

**Tip — probeer deze datums:**
- `21/06/1990` — zomer 1990
- `01/01/2000` — millenniumwisseling
- `10/07/2010` — zomer 2010
- `15/03/2020` — begin corona-lockdown
