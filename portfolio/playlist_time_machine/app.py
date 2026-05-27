"""
=============================================================
  app.py — Playlist Tijdmachine met Streamlit UI
  Opdracht:  Portfolio - 100 Days of Code
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee

  Beschrijving:
  ------------
  De Playlist Tijdmachine omgezet naar een Streamlit webinterface.
  De gebruiker kiest een datum via een datumkiezer,
  en het programma haalt de Billboard Hot 100 op via web scraping.

  Starten:
  --------
      streamlit run app.py

  Streamlit functies gebruikt in dit bestand:
  --------------------------------------------
  st.set_page_config(...)     Paginatitel en icoon instellen.
  st.title(tekst)             Grote hoofdtitel.
  st.subheader(tekst)         Kleinere ondertitel.
  st.markdown(tekst)          Opgemaakte tekst (HTML/Markdown).
  st.date_input(label, ...)   Datumkiezer widget.
  st.slider(label, ...)       Schuifregelaar voor een getal.
  st.button(label)            Klikknop.
  st.spinner(tekst)           Laadanimatie tijdens verwerking.
  st.success(tekst)           Groene boodschap.
  st.warning(tekst)           Oranje waarschuwing.
  st.error(tekst)             Rode foutboodschap.
  st.info(tekst)              Blauwe informatieboodschap.
  st.columns(aantal)          Pagina opdelen in kolommen.
  st.metric(label, waarde)    Groot getal met label tonen.
  st.divider()                Horizontale scheidingslijn.

  ============================================================
  SAMENVATTING GEBRUIKTE METHODES (eigen code)
  ============================================================

  fetch_billboard_chart(date_str) → list | None
      Haalt de Billboard Hot 100 pagina op via requests.
      Verwerkt de HTML met BeautifulSoup.
      Geeft een lijst van nummertitels terug, of None bij fout.

  get_demo_songs(year) → tuple[list, str]
      Geeft historische demo-data terug als Billboard niet
      bereikbaar is. Kiest de dichtstbijzijnde beschikbare datum.
      Geeft (lijst_van_nummers, gebruikte_datum) terug.

  display_chart(songs, date_str, source, max_songs)
      Toont de chart als een opgemaakte Streamlit pagina
      met metrics, nummers en medailles voor top 3.

  ============================================================
=============================================================
"""

# --- Standaard bibliotheken ---
from datetime import date, datetime   # Datumverwerking

# --- Externe bibliotheken ---
import streamlit as st       # Webinterface
import requests              # Website ophalen
from bs4 import BeautifulSoup  # HTML verwerken


# =====================
#  Pagina configuratie
# =====================
st.set_page_config(
    page_title="Playlist Tijdmachine",
    page_icon="🕰️",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =====================
#  Constanten
# =====================

BILLBOARD_BASE_URL = "https://www.billboard.com/charts/hot-100/"

# Headers zodat Billboard ons niet blokkeert
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Historische demo-data (als Billboard niet bereikbaar is)
DEMO_CHARTS = {
    "1990-06-21": [
        "Hold On — Wilson Phillips",
        "It Must Have Been Love — Roxette",
        "Poison — Bell Biv DeVoe",
        "She Ain't Worth It — Glenn Medeiros ft. Bobby Brown",
        "Step by Step — New Kids on the Block",
        "Do You Remember? — Phil Collins",
        "Vision of Love — Mariah Carey",
        "Cradle of Love — Billy Idol",
        "All I Wanna Do Is Make Love to You — Heart",
        "Sending All My Love — Linear",
    ],
    "2000-01-01": [
        "What a Girl Wants — Christina Aguilera",
        "Say My Name — Destiny's Child",
        "Smooth — Santana ft. Rob Thomas",
        "Maria Maria — Santana ft. The Product G&B",
        "I Knew I Loved You — Savage Garden",
        "Amazed — Lonestar",
        "The Next Episode — Dr. Dre ft. Snoop Dogg",
        "Bent — matchbox twenty",
        "Thong Song — Sisqó",
        "He Wasn't Man Enough — Toni Braxton",
    ],
    "2010-07-10": [
        "California Gurls — Katy Perry ft. Snoop Dogg",
        "Airplanes — B.o.B ft. Hayley Williams",
        "OMG — Usher ft. will.i.am",
        "Cooler Than Me — Mike Posner",
        "Not Afraid — Eminem",
        "Magic — B.o.B ft. Rivers Cuomo",
        "Your Love Is My Drug — Ke$ha",
        "DJ Got Us Fallin' In Love — Usher ft. Pitbull",
        "Break Your Heart — Taio Cruz ft. Ludacris",
        "Teenage Dream — Katy Perry",
    ],
    "2020-03-15": [
        "Blinding Lights — The Weeknd",
        "Toosie Slide — Drake",
        "Rockstar — DaBaby ft. Roddy Ricch",
        "Say So — Doja Cat",
        "Intentions — Justin Bieber ft. Quavo",
        "Life Is Good — Future ft. Drake",
        "Savage — Megan Thee Stallion ft. Beyoncé",
        "The Box — Roddy Ricch",
        "Circles — Post Malone",
        "Lose You to Love Me — Selena Gomez",
    ],
}


# =====================
#  Functies
# =====================

def fetch_billboard_chart(date_str: str) -> list | None:
    """
    Haalt de Billboard Hot 100 op voor een gegeven datum
    en haalt de nummertitels eruit via web scraping.

    Parameters:
    -----------
    date_str : Datum als tekst "JJJJ-MM-DD"

    Geeft terug:
    ------------
    list : Lijst van nummertitels als het gelukt is
    None : Als de pagina niet opgehaald kon worden
    """
    url = f"{BILLBOARD_BASE_URL}{date_str}/"

    try:
        # Stuur GET-verzoek met browser-headers
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=10)

        if response.status_code != 200:
            # Pagina niet gevonden of toegang geweigerd
            return None

        # Verwerk de HTML met BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Zoek alle titelelementen via CSS selector
        title_elements = soup.select("h3#title-of-a-story")

        # Billboard toont naast nummertitels ook metadata in hetzelfde
        # h3-element: "Songwriter(s)", "Producer(s)", "Imprint/Label",
        # "Gains in Weekly Performance", "Additional Awards", enzovoort.
        # We filteren die eruit met een lijst van bekende metadatateksten.
        METADATA_WORDS = [
            "songwriter",
            "producer",
            "imprint",
            "label",
            "gains",
            "awards",
            "performance",
            "additional",
        ]

        songs = []
        for el in title_elements:
            title = el.get_text(strip=True)

            # Sla lege tekst over
            if not title:
                continue

            # Controleer of de tekst een bekende metadataterm bevat
            # We zetten de titel om naar kleine letters voor de vergelijking
            title_lower = title.lower()
            is_metadata = any(word in title_lower for word in METADATA_WORDS)

            # Voeg alleen toe als het GEEN metadata is
            if not is_metadata:
                songs.append(title)

        # Geef de lijst terug (kan leeg zijn als scraping mislukt)
        return songs if songs else None

    except requests.exceptions.RequestException:
        # Alle requests-fouten opvangen (geen verbinding, timeout, ...)
        return None


def get_demo_songs(year: int) -> tuple:
    """
    Geeft de meest passende demo-data terug op basis van het jaar.

    Parameters:
    -----------
    year : Het gevraagde jaar als integer

    Geeft terug:
    ------------
    tuple : (lijst_van_nummers, datum_als_tekst)
    """
    # Zoek de demo-datum waarvan het jaar het dichtste bij ligt
    closest_date = min(
        DEMO_CHARTS.keys(),
        key=lambda d: abs(int(d[:4]) - year)
    )

    return DEMO_CHARTS[closest_date], closest_date


def display_chart(songs: list, date_str: str, source: str, max_songs: int):
    """
    Toont de Billboard chart als een opgemaakte Streamlit pagina.

    Parameters:
    -----------
    songs    : Lijst van nummertitels
    date_str : De datum van de chart ("JJJJ-MM-DD")
    source   : "Billboard" (live) of "Demo" (historisch)
    max_songs: Aantal te tonen nummers
    """
    # Zet de datum om naar een mooi formaat
    parsed = datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = parsed.strftime("%d %B %Y")

    st.divider()

    # Toon bron-badge
    if source == "Demo":
        st.warning(
            "⚠️ **Demo data** — Billboard was niet bereikbaar. "
            "Dit zijn historische nummers voor de dichtstbijzijnde beschikbare datum."
        )
    else:
        st.success("✅ Live data opgehaald van Billboard.com")

    # Header met datum
    st.subheader(f"🎵 Billboard Hot 100 — {formatted_date}")

    # Statistieken in kolommen
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Gevonden nummers", len(songs))
    with col2:
        st.metric("Getoond in lijst", min(max_songs, len(songs)))

    st.divider()

    # Toon de nummers
    top_songs = songs[:max_songs]

    for position, song_title in enumerate(top_songs, start=1):
        # Medaille voor top 3, nummer voor de rest
        if position == 1:
            medal = "🥇"
            color = "#FFD700"   # Goud
        elif position == 2:
            medal = "🥈"
            color = "#C0C0C0"   # Zilver
        elif position == 3:
            medal = "🥉"
            color = "#CD7F32"   # Brons
        else:
            medal = f"{position}."
            color = "#cccccc"   # Grijs voor de rest

        # Elke rij als opgemaakte HTML
        st.markdown(
            f"""
            <div style="
                display: flex;
                align-items: center;
                padding: 10px 15px;
                margin: 4px 0;
                background-color: #1a1a2e;
                border-radius: 6px;
                border-left: 4px solid {color};
            ">
                <span style="
                    font-size: 1.2rem;
                    min-width: 45px;
                    color: {color};
                    font-weight: bold;
                ">{medal}</span>
                <span style="
                    color: #ffffff;
                    font-size: 1rem;
                ">{song_title}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =====================
#  Hoofdprogramma
# =====================

def main():
    """
    Hoofdfunctie: bouwt de volledige Streamlit pagina op.
    """
    # Paginatitel
    st.title("🕰️ Playlist Tijdmachine")
    st.markdown(
        "Ontdek welke nummers populair waren op een specifieke datum in het verleden. "
        "Data via **Billboard Hot 100**."
    )

    st.divider()

    # --- Invoersectie ---
    st.subheader("📅 Kies een datum")

    # Datumkiezer: min = eerste Billboard datum, max = vandaag
    chosen_date = st.date_input(
        label="Datum",
        value=date(1990, 6, 21),              # Standaardwaarde
        min_value=date(1958, 8, 4),           # Eerste Billboard datum
        max_value=date.today(),               # Niet in de toekomst
        format="DD/MM/YYYY",                  # Europees formaat in de widget
        help="Billboard bestaat vanaf augustus 1958.",
    )

    # Schuifregelaar voor aantal te tonen nummers
    max_songs = st.slider(
        label="Aantal nummers tonen",
        min_value=5,
        max_value=100,
        value=10,        # Standaard top 10
        step=5,
        help="Kies hoeveel nummers je wil zien (5 tot 100).",
    )

    st.divider()

    # Demo-datums tonen als klikbare tip
    st.caption(
        "💡 **Tip — probeer deze datums:** "
        "21/06/1990 · 01/01/2000 · 10/07/2010 · 15/03/2020"
    )

    # --- Zoekknop ---
    if st.button("🔍  Zoek Billboard Chart", use_container_width=True, type="primary"):

        # Zet de datum om naar het formaat dat Billboard verwacht
        date_str = chosen_date.strftime("%Y-%m-%d")

        # Toon laadanimatie tijdens het ophalen
        with st.spinner("Billboard ophalen..."):
            songs = fetch_billboard_chart(date_str)

        if songs:
            # Live data beschikbaar
            display_chart(songs, date_str, source="Billboard", max_songs=max_songs)
        else:
            # Billboard niet bereikbaar: gebruik demo-data
            demo_songs, demo_date = get_demo_songs(chosen_date.year)
            display_chart(demo_songs, demo_date, source="Demo", max_songs=max_songs)


# Start het programma
main()