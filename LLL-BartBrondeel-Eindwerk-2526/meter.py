"""
=============================================================
  meter.py — HomeWizard P1 meter uitlezen
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee

  OOP principe: alle meter-logica zit in 1 klasse
  DRY principe: IP-adres staat 1 keer in Config, nergens anders

  De HomeWizard P1 meter heeft een ingebouwde webserver.
  Via een eenvoudige HTTP-aanvraag krijgen we alle data
  als JSON terug — geen extra bibliotheek nodig.

  API documentatie:
  https://api-documentation.homewizard.com/docs/v1/measurement
=============================================================
"""

# --- Standaard bibliotheken ---
from datetime import datetime

# --- Externe bibliotheken ---
import requests         # Verstuurt HTTP-aanvragen naar de meter

# --- Eigen modules ---
from config import Config

def _get_simulatie(self) -> dict:
    """
    Geef nep-data terug als de meter niet bereikbaar is.
    Gebruikt dezelfde veldnamen als de echte meter.
    """
    return {
        "tijdstip":                 datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "huidig_vermogen_w":        850,
        "huidig_vermogen_kw":       0.850,
        "vermogen_fase1_w":         400,
        "vermogen_fase2_w":         250,
        "vermogen_fase3_w":         200,
        "actief_tarief":            1,
        "totaal_verbruik_kwh":      6259.542,
        "totaal_verbruik_piek_kwh": 2479.151,
        "totaal_verbruik_dal_kwh":  3780.391,
        "totaal_injectie_kwh":      7634.517,
        "totaal_injectie_piek_kwh": 5242.947,
        "totaal_injectie_dal_kwh":  2391.570,
        "totaal_gas_m3":            2626.361,
        "wifi_sterkte":             0,
        "is_simulatie":             True,
    }

class HomeWizardMeter:
    """
    Klasse om data op te halen van de HomeWizard P1 slimme meter.

    De meter heeft twee API-eindpunten:
    - /API → basisinfo (model, versie, serienummer)
    - /API/v1/data → actuele meetwaarden (verbruik, teruglevering, ...)

    Gebruik:
    --------
    meter = HomeWizardMeter()
    data = meter.get_data()
    print(data["power_w"]) # huidig vermogen in Watt
    """

    def __init__(self):
        """Sla het IP-adres op bij aanmaken van het object."""

        # IP-adres komt uit Config — DRY-principe
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
    #  Publieke methodes  bruikbaar van buitenaf
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
            meter_model         : meter type
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

        Jouw meter (Fluvius 253967035_D) gebruikt deze veldnamen:
            active_power_w          : huidig nettovermogen (+ verbruik, - injectie)
            active_tariff           : actief tarief (1 = dag/piek, 2 = nacht/dal)
            total_power_import_t1_kwh : totaal verbruik piekuren (tarief 1)
            total_power_import_t2_kwh : totaal verbruik daluren (tarief 2)
            total_power_export_t1_kwh : totaal injectie piekuren
            total_power_export_t2_kwh : totaal injectie daluren
            total_gas_m3            : totaal gasverbruik
            active_voltage_l1_v     : spanning fase 1
            active_current_a        : totale stroomsterkte

        Geeft terug:
            dict met alle nuttige waarden netjes gegroepeerd
        """
        data = self.get_data()

        # Als er geen data is, geef simulatiedata terug
        if not data:
            print("[INFO] Geen live data — simulatiedata wordt gebruikt")
            return self._get_simulatie()

        return {
            # --- Tijdstip ---
            "tijdstip": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),

            # - - - Huidig vermogen - - -
            # Positief = je verbruikt van het net
            # Negatief = je injecteert naar het net (zonnepanelen)
            "huidig_vermogen_w": data.get("active_power_w", 0),
            "huidig_vermogen_kw": round(data.get("active_power_w", 0) / 1000, 3),

            # --- Per fase (handig voor diagnose) ---
            "vermogen_fase1_w": data.get("active_power_l1_w", 0),
            "vermogen_fase2_w": data.get("active_power_l2_w", 0),
            "vermogen_fase3_w": data.get("active_power_l3_w", 0),

            # --- Actief tarief ---
            # 1 = piekuren (dag), 2 = daluren (nacht/weekend)
            "actief_tarief": data.get("active_tariff", 0),

            # --- Totalen elektriciteit ---
            "totaal_verbruik_kwh": data.get("total_power_import_kwh", 0),
            "totaal_verbruik_piek_kwh": data.get("total_power_import_t1_kwh", 0),
            "totaal_verbruik_dal_kwh": data.get("total_power_import_t2_kwh", 0),
            "totaal_injectie_kwh": data.get("total_power_export_kwh", 0),
            "totaal_injectie_piek_kwh": data.get("total_power_export_t1_kwh", 0),
            "totaal_injectie_dal_kwh": data.get("total_power_export_t2_kwh", 0),

            # --- Gas ---
            "totaal_gas_m3": data.get("total_gas_m3", 0),

            # --- Netwerk ---
            "wifi_sterkte": data.get("wifi_strength", 0),

            # --- Meta ---
            "is_simulatie": False,
        }

