"""
=============================================================
  app.py — Energie Dashboard
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Versie:    0.4 — PriceCalculator klasse toegevoegd

  Wijziging t.o.v. sessie 3:
  - PriceCalculator geïmporteerd
  - Nieuwe routes /prices en /prices/daily toegevoegd
=============================================================
"""

# --- Externe bibliotheken ---
from flask import Flask, jsonify, request

# --- Eigen modules ---
from config import Config
from meter import HomeWizardMeter
from calculator import PriceCalculator

# =====================
#  Flask app aanmaken
# =====================
app = Flask(__name__)

# Maak objecten aan — worden hergebruikt in alle routes (DRY)
meter      = HomeWizardMeter()
calculator = PriceCalculator()


# =====================
#  Routes
# =====================

@app.route("/")
def index():
    """Startpagina — tijdelijke testpagina tot sessie 8."""
    return """
        <h1>Energie Dashboard</h1>
        <p>Project is opgestart.</p>
        <hr>
        <h3>Beschikbare pagina's:</h3>
        <ul>
            <li><a href="/meter">Meterdata (JSON)</a></li>
            <li><a href="/meter/info">Meterinformatie (JSON)</a></li>
            <li><a href="/prices">Actuele kostprijs (JSON)</a></li>
            <li><a href="/prices/daily?peak=5&off_peak=3">Dagkostprijs voorbeeld (JSON)</a></li>
        </ul>
        <p><em>Mooie pagina volgt in sessie 8.</em></p>
    """


@app.route("/meter")
def meter_data():
    """Geef actuele meterdata terug als JSON."""
    data = meter.get_summary()
    return jsonify(data)


@app.route("/meter/info")
def meter_info():
    """Geef basisinformatie over de meter terug als JSON."""
    info = meter.get_info()
    return jsonify(info)


@app.route("/prices")
def current_prices():
    """
    Geef de actuele kostprijs terug op basis van live meterdata.

    Combineert meterdata + berekening in 1 aanroep.
    """
    # Haal live data op van de meter
    meter_data = meter.get_summary()

    # Lees het vermogen en tarief uit de meterdata
    power_w = meter_data.get("current_power_w", 0)
    tariff = meter_data.get("active_tariff", calculator.get_current_tariff())

    # Bereken de kostprijs
    summary = calculator.get_summary(power_w=power_w, tariff=tariff)

    return jsonify(summary)


@app.route("/prices/daily")
def daily_cost():
    """
    Bereken de dagkostprijs op basis van opgegeven verbruik.

    Parameters via URL (query string):
        peak     : verbruik piekuren in kWh (standaard: 0)
        off_peak : verbruik daluren in kWh  (standaard: 0)

    Voorbeeld:
        /prices/daily?peak=5&off_peak=3
        → kostprijs voor 5 kWh piek + 3 kWh dal
    """
    # Lees de parameters uit de URL — standaard 0 als ze ontbreken
    peak_kwh     = float(request.args.get("peak",     0))
    off_peak_kwh = float(request.args.get("off_peak", 0))

    result = calculator.calculate_daily_cost(
        peak_kwh=peak_kwh,
        off_peak_kwh=off_peak_kwh
    )

    return jsonify(result)


# =====================
#  App opstarten
# =====================
if __name__ == "__main__":
    print(f"Energie Dashboard wordt opgestart op http://localhost:{Config.PORT}")
    app.run(debug=Config.DEBUG, port=Config.PORT)