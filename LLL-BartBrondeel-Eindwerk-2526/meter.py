"""
=============================================================
  meter.py — HomeWizard P1 meter uitlezen
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee

  OOP principe: alle meter-logica zit in 1 klasse
  DRY principe: IP-adres staat 1x in Config, nergens anders

  De HomeWizard P1 meter heeft een ingebouwde webserver.
  Via een eenvoudige HTTP-aanvraag krijgen we alle data
  als JSON terug — geen extra bibliotheek nodig.

  API documentatie:
  https://api-documentation.homewizard.com/docs/category/p1-meter
=============================================================
"""

# --- Standaard bibliotheken ---
import json
from datetime import datetime

# --- Externe bibliotheken ---
import requests         # Verstuurt HTTP-aanvragen naar de meter

# --- Eigen modules ---
from config import Config


class HomeWizardMeter:
    """
    Klasse om data op te halen van de HomeWizard P1 slimme meter.

    De meter heeft twee API-eindpunten:
    - /api          → basisinfo (model, versie, serienummer)
    - /api/v1/data  → actuele meetwaarden (verbruik, teruglevering, ...)

    Gebruik:
    --------
    meter = HomeWizardMeter()
    data = meter.get_data()
    print(data["power_w"])   # huidig vermogen in Watt
    """

    def __init__(self):
        """Sla het IP-adres op bij aanmaken van het object."""

        # IP-adres komt uit Config — DRY principe
        self.ip = Config.HOMEWIZARD_IP

        # Basis-URL voor alle API-aanvragen
        self.base_url = f"http://{self.ip}"

    # --------------------------------------------------
    #  Interne hulpmethode (private)
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

    # --------------------------------------------------
    #  Publieke methodes — bruikbaar van buitenaf
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
        Haal actuele meetwaarden op van de meter.

        Belangrijke velden in de respons:
            wifi_ssid           : naam van het wifi-netwerk
            wifi_strength_pct   : wifi signaalsterkte (%)
            smr_version         : versie van het DSMR-protocol
            meter_model         : metertype
            power_w             : huidig verbruik in Watt (+ = verbruik, - = teruglevering)
            total_power_import_kwh  : totaal verbruik ooit (kWh)
            total_power_export_kwh  : totaal teruggeleverd ooit (kWh)

        Geeft terug:
            dict met alle meetwaarden, of lege dict bij fout
        """
        return self._get("/api/v1/data")

    def get_samenvatting(self) -> dict:
        """
        Geef een overzichtelijke samenvatting van de actuele meterstand.

        Dit is een hulpmethode die de ruwe data omzet naar
        een eenvoudig woordenboek met enkel de nuttige waarden.

        Geeft terug:
            dict met vermogen, totalen en tijdstip
        """
        data = self.get_data()

        # Als er geen data is (fout), geef simulatiedata terug
        if not data:
            print("[INFO] Geen live data — simulatiedata wordt gebruikt")
            return self._get_simulatie()

        return {
            "tijdstip":             datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "huidig_vermogen_w":    data.get("power_w", 0),
            "huidig_vermogen_kw":   round(data.get("power_w", 0) / 1000, 3),
            "totaal_verbruik_kwh":  data.get("total_power_import_kwh", 0),
            "totaal_injectie_kwh":  data.get("total_power_export_kwh", 0),
            "wifi_sterkte":         data.get("wifi_strength_pct", 0),
            "is_simulatie":         False,
        }

    def _get_simulatie(self) -> dict:
        """
        Geef nep-data terug als de meter niet bereikbaar is.

        Handig om toch verder te kunnen werken en te testen
        als je niet thuis bent of de meter tijdelijk offline is.
        """
        return {
            "tijdstip":             datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "huidig_vermogen_w":    850,
            "huidig_vermogen_kw":   0.850,
            "totaal_verbruik_kwh":  12345.678,
            "totaal_injectie_kwh":  4567.890,
            "wifi_sterkte":         0,
            "is_simulatie":         True,
        }