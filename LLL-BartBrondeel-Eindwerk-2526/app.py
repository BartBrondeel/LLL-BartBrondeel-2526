"""
=============================================================
  app.py — Energie Dashboard
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Versie:    0.5 — DataManager + automatisch opslaan toegevoegd

  Wijziging t.o.v. sessie 4:
  - DataManager geïmporteerd
  - APScheduler toegevoegd voor automatisch opslaan (elke minuut)
  - Nieuwe routes: /history, /history/today, /history/week, /history/month
=============================================================
"""

# --- Externe bibliotheken ---
from flask import Flask, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler

# --- Eigen modules ---
from config import Config
from meter import HomeWizardMeter
from calculator import PriceCalculator
from data_manager import DataManager

# =====================
#  Flask app aanmaken
# =====================
app = Flask(__name__)

# Maak objecten aan — worden hergebruikt in alle routes (DRY)
meter        = HomeWizardMeter()
calculator   = PriceCalculator()
data_manager = DataManager()


# =====================
#  Automatisch opslaan
# =====================

def save_measurement_job():
    """
    Achtergrondtaak die automatisch elke minuut een meting opslaat.
    Wordt gestart via APScheduler bij het opstarten van de app.
    """
    data_manager.save_measurement()


# APScheduler: voert save_measurement_job() uit op de achtergrond
# interval_minutes=1: sla elke minuut een meting op
scheduler = BackgroundScheduler()
scheduler.add_job(save_measurement_job, "interval", minutes=1)
scheduler.start()

print("[INFO] Automatisch opslaan gestart — elke minuut een meting")


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
            <li><a href="/history">Recente metingen (JSON)</a></li>
            <li><a href="/history/today">Kostprijs vandaag (JSON)</a></li>
            <li><a href="/history/week">Kostprijs deze week (JSON)</a></li>
            <li><a href="/history/month">Kostprijs deze maand (JSON)</a></li>
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
    """Geef de actuele kostprijs terug op basis van live meterdata."""
    meter_reading = meter.get_summary()
    power_w       = meter_reading.get("current_power_w", 0)
    tariff        = meter_reading.get("active_tariff", calculator.get_current_tariff())
    summary       = calculator.get_summary(power_w=power_w, tariff=tariff)
    return jsonify(summary)


@app.route("/prices/daily")
def daily_cost():
    """
    Bereken de dagkostprijs op basis van opgegeven verbruik.

    Parameters via URL:
        peak     : verbruik piekuren in kWh (standaard: 0)
        off_peak : verbruik daluren in kWh  (standaard: 0)

    Voorbeeld: /prices/daily?peak=5&off_peak=3
    """
    peak_kwh     = float(request.args.get("peak",     0))
    off_peak_kwh = float(request.args.get("off_peak", 0))
    result       = calculator.calculate_daily_cost(peak_kwh=peak_kwh,
                                                   off_peak_kwh=off_peak_kwh)
    return jsonify(result)


@app.route("/history")
def history():
    """Geef de 10 meest recente metingen terug als JSON."""
    measurements = data_manager.get_recent_measurements(limit=10)
    return jsonify(measurements)


@app.route("/history/today")
def history_today():
    """Geef de kostprijs en het verbruik van vandaag terug."""
    return jsonify(data_manager.get_today())


@app.route("/history/week")
def history_week():
    """Geef de kostprijs en het verbruik van de laatste 7 dagen terug."""
    return jsonify(data_manager.get_week())


@app.route("/history/month")
def history_month():
    """Geef de kostprijs en het verbruik van de laatste 30 dagen terug."""
    return jsonify(data_manager.get_month())


# =====================
#  App opstarten
# =====================
if __name__ == "__main__":
    print(f"Energie Dashboard wordt opgestart op http://localhost:{Config.PORT}")
    app.run(debug=Config.DEBUG, port=Config.PORT)