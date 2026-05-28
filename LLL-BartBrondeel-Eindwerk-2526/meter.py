"""
=============================================================
  meter.py — HomeWizard P1 meter uitlezen
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Sessie:    3 — HomeWizardMeter klasse

  OOP principe: alle meter-logica zit in 1 klasse
  DRY principe: IP-adres staat 1x in Config, nergens anders

  De HomeWizard P1 meter heeft een ingebouwde webserver.
  Via een eenvoudige HTTP-aanvraag krijgen we alle data
  als JSON terug — geen extra bibliotheek nodig.

  API documentatie (officieel, geraadpleegd mei 2026):
  https://api-documentation.homewizard.com/docs/v1/measurement
=============================================================
"""

# --- Standaard bibliotheken ---
from datetime import datetime

# --- Externe bibliotheken ---
import requests         # Verstuurt HTTP-aanvragen naar de meter

# --- Eigen modules ---
from config import Config


class HomeWizardMeter:
    """
    Klasse om data op te halen van de HomeWizard P1 slimme meter.

    De meter heeft twee API-eindpunten:
    - /api         → basisinfo (model, versie, serienummer)
    - /api/v1/data → actuele meetwaarden (verbruik, teruglevering, ...)

    Gebruik:
    --------
    meter = HomeWizardMeter()
    data = meter.get_data()
    print(data["active_power_w"])   # huidig vermogen in Watt
    """

    def __init__(self):
        """Sla het IP-adres op bij aanmaken van het object."""

        # IP-adres komt uit Config — DRY principe
        self.ip = Config.HOMEWIZARD_IP

        # Basis-URL voor alle API-aanvragen
        self.base_url = f"http://{self.ip}"

    # --------------------------------------------------
    #  Interne hulpmethoden (private)
    #  Naam begint met _ : bedoeld voor intern gebruik
    # --------------------------------------------------

    def _get(self, endpoint: str) -> dict:
        """
        Verstuur een GET-aanvraag naar de meter.

        Parameters:
            endpoint: het pad achter het IP, bv. '/api/v1/data'

        Geeft terug:
            dict met de JSON-respons, of lege dict bij fout
        """
        url = f"{self.base_url}{endpoint}"

        try:
            # timeout=5: wacht max 5 seconden op antwoord
            response = requests.get(url, timeout=5)

            # Gooi een fout als de statuscode niet 200 (OK) is
            response.raise_for_status()

            return response.json()

        except requests.exceptions.ConnectionError:
            print(f"[FOUT] Kan meter niet bereiken op {url}")
            print("[FOUT] Controleer of de meter aan staat en je op hetzelfde netwerk zit")
            return {}

        except requests.exceptions.Timeout:
            print(f"[FOUT] Meter reageert niet binnen 5 seconden op {url}")
            return {}

        except requests.exceptions.RequestException as e:
            print(f"[FOUT] Onverwachte fout bij aanvraag: {e}")
            return {}

    def _get_simulation(self) -> dict:
        """
        Geef nep-data terug als de meter niet bereikbaar is.

        Handig om toch verder te kunnen werken en te testen
        als je niet thuis bent of de meter tijdelijk offline is.
        Gebruikt dezelfde veldnamen als de echte meterdata.
        """
        return {
            "timestamp":                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "current_power_w":              850,
            "current_power_kw":             0.850,
            "power_phase1_w":               400,
            "power_phase2_w":               250,
            "power_phase3_w":               200,
            "active_tariff":                1,
            "total_consumption_kwh":        6259.542,
            "total_consumption_peak_kwh":   2479.151,
            "total_consumption_off_peak_kwh": 3780.391,
            "total_injection_kwh":          7634.517,
            "total_injection_peak_kwh":     5242.947,
            "total_injection_off_peak_kwh": 2391.570,
            "total_gas_m3":                 2626.361,
            "wifi_strength":                0,
            "is_simulation":                True,
        }

    # --------------------------------------------------
    #  Publieke methoden — bruikbaar van buitenaf
    # --------------------------------------------------

    def get_info(self) -> dict:
        """
        Haal basisinformatie op over de meter.

        Geeft terug:
            dict met o.a. 'product_name', 'serial', 'firmware_version'
        """
        return self._get("/api")

    def get_data(self) -> dict:
        """
        Haal de ruwe actuele meetwaarden op van de meter.

        Belangrijke velden in de respons:
            active_power_w            : huidig nettovermogen in Watt
            active_tariff             : actief tarief (1 = piek, 2 = dal)
            total_power_import_kwh    : totaal verbruik ooit (kWh)
            total_power_export_kwh    : totaal teruggeleverd ooit (kWh)
            total_gas_m3              : totaal gasverbruik (m³)

        Geeft terug:
            dict met alle ruwe meetwaarden, of lege dict bij fout
        """
        return self._get("/api/v1/data")

    def get_summary(self) -> dict:
        """
        Geef een overzichtelijke samenvatting van de actuele meterstand.

        Vertaalt de ruwe API-veldnamen naar leesbare namen
        en groepeert de waarden logisch per categorie.

        Jouw meter (Fluvius 253967035_D) gebruikt deze API-veldnamen:
            active_power_w              : huidig nettovermogen (+ verbruik, - injectie)
            active_tariff               : actief tarief (1 = piek, 2 = dal)
            total_power_import_t1_kwh   : totaal verbruik piekuren
            total_power_import_t2_kwh   : totaal verbruik daluren
            total_power_export_t1_kwh   : totaal injectie piekuren
            total_power_export_t2_kwh   : totaal injectie daluren
            total_gas_m3                : totaal gasverbruik

        Geeft terug:
            dict met alle nuttige waarden netjes gegroepeerd,
            of simulatiedata als de meter niet bereikbaar is
        """
        data = self.get_data()

        # Als er geen data is (meter offline), val terug op simulatiedata
        if not data:
            print("[INFO] Geen live data — simulatiedata wordt gebruikt")
            return self._get_simulation()

        return {
            # --- Tijdstip van de meting ---
            "timestamp":    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

            # --- Huidig vermogen ---
            # Positief = je verbruikt stroom van het net
            # Negatief = je levert stroom terug (zonnepanelen)
            "current_power_w":  data.get("active_power_w", 0),
            "current_power_kw": round(data.get("active_power_w", 0) / 1000, 3),

            # --- Vermogen per fase (handig voor diagnose) ---
            "power_phase1_w":   data.get("active_power_l1_w", 0),
            "power_phase2_w":   data.get("active_power_l2_w", 0),
            "power_phase3_w":   data.get("active_power_l3_w", 0),

            # --- Actief tarief ---
            # 1 = piekuren (weekdag 07:00-22:00)
            # 2 = daluren  (nacht + weekends)
            "active_tariff":    data.get("active_tariff", 0),

            # --- Totalen elektriciteit ---
            "total_consumption_kwh":            data.get("total_power_import_kwh", 0),
            "total_consumption_peak_kwh":       data.get("total_power_import_t1_kwh", 0),
            "total_consumption_off_peak_kwh":   data.get("total_power_import_t2_kwh", 0),
            "total_injection_kwh":              data.get("total_power_export_kwh", 0),
            "total_injection_peak_kwh":         data.get("total_power_export_t1_kwh", 0),
            "total_injection_off_peak_kwh":     data.get("total_power_export_t2_kwh", 0),

            # --- Gas ---
            "total_gas_m3":     data.get("total_gas_m3", 0),

            # --- Netwerkinformatie ---
            "wifi_strength":    data.get("wifi_strength", 0),

            # --- Simulatiestatus ---
            "is_simulation":    False,
        }