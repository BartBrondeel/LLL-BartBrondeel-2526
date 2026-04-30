"""
=============================================================
  ENERGIE DASHBOARD - Eindwerk Python Webapplicatie
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren — Odisee
  Versie:    0.1 — Project setup
=============================================================
"""

# --- Externe bibliotheken ---
from flask import Flask

# =====================
#  Flask app aanmaken
# =====================
app = Flask(__name__)


# =====================
#  Routes
# =====================

@app.route("/")
def index():
    """
    Startpagina van het dashboard.
    Geeft voorlopig een eenvoudige tekstboodschap terug.
    Wordt in een latere sessie vervangen door een echte HTML-pagina.
    """
    return """
        <h1>⚡ Energie Dashboard</h1>
        <p>Project is opgestart. Meer volgt...</p>
    """


# =====================
#  App opstarten
# =====================
if __name__ == "__main__":
    print("Energie Dashboard wordt opgestart op http://localhost:5000")
    app.run(debug=True)