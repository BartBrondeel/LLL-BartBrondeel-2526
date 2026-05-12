"""
=============================================================
  app.py — Energie Dashboard
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Versie:    0.2 — Config klasse geintegreerd

  Wijziging t.o.v. sessie 1:
  - Losse variabelen vervangen door Config klasse
  - Config wordt geimporteerd uit config.py
=============================================================
"""

# --- Externe bibliotheken ---
from flask import Flask

# --- Eigen modules ---
from config import Config  # Onze nieuwe configuratieklasse

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
    Toont ook de actieve configuratie als test.
    Wordt in sessie 8 vervangen door echte HTML-pagina.
    """
    return f"""
        <h1>Energie Dashboard</h1>
        <p>Project is opgestart.</p>
        <hr>
        <h3>Actieve configuratie (test sessie 2):</h3>
        <ul>
            <li>HomeWizard IP: {Config.HOMEWIZARD_IP}</li>
            <li>Piekprijs: {Config.PRIJS_PIEK_PER_KWH} EUR/kWh</li>
            <li>Dalprijs: {Config.PRIJS_DAL_PER_KWH} EUR/kWh</li>
            <li>Debug modus: {Config.DEBUG}</li>
        </ul>
        <p><em>Deze testpagina verdwijnt in sessie 8.</em></p>
    """


# =====================
#  App opstarten
# =====================
if __name__ == "__main__":
    print(f"Energie Dashboard wordt opgestart op http://localhost:{Config.PORT}")
    app.run(debug=Config.DEBUG, port=Config.PORT)
