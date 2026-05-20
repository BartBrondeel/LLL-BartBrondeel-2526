"""
=============================================================
  app.py — Energie Dashboard
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Versie:    0.3 — HomeWizardMeter klasse toegevoegd

  Wijziging t.o.v. sessie 2:
  - Nieuwe route /meter toegevoegd
  - HomeWizardMeter wordt hier gebruikt
=============================================================
"""

# --- Externe bibliotheken ---
from flask import Flask, jsonify

# --- Eigen modules ---
from config import Config
from meter import HomeWizardMeter

# =====================
#  Flask app aanmaken
# =====================
app = Flask(__name__)

# Maak 1 meter-object aan — wordt hergebruikt in alle routes (DRY)
meter = HomeWizardMeter()


# =====================
#  Routes
# =====================

@app.route("/")
def index():
    
    return f"""
        <h1>Energie Dashboard</h1>
        <p>Project is opgestart.</p>
        <hr>
        <h3>Beschikbare pagina's:</h3>
        <ul>
            <li><a href="/meter">Meterdata (JSON)</a></li>
            <li><a href="/meter/info">Meterinformatie (JSON)</a></li>
        </ul>
        <p><em>Mooie pagina volgt in sessie 8.</em></p>
    """


@app.route("/meter")
def meter_data():
    """
    Geef actuele meterdata terug als JSON.

    jsonify() zet een Python dict om naar een nette JSON-respons
    die elke browser of applicatie kan lezen.
    """
    data = meter.get_samenvatting()
    return jsonify(data)


@app.route("/meter/info")
def meter_info():
    """Geef basisinformatie over de meter terug als JSON."""
    info = meter.get_info()
    return jsonify(info)


# =====================
#  App opstarten
# =====================
if __name__ == "__main__":
    print(f"Energie Dashboard wordt opgestart op http://localhost:{Config.PORT}")
    print(f"Meterdata bekijken: http://localhost:{Config.PORT}/meter")
    app.run(debug=Config.DEBUG, port=Config.PORT)