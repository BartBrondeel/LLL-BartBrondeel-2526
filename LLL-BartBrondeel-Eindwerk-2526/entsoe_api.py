"""
=============================================================
  entsoe_api.py — ENTSO-E energieprijzen ophalen
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Sessie:    7 — EntsoEApi klasse

  OOP principe: alle ENTSO-E logica zit in 1 klasse
  DRY principe: API sleutel staat 1x in Config

  ENTSO-E = European Network of Transmission System Operators
            for Electricity

  We halen de DAY AHEAD prijzen op voor België (bidding zone BE).
  Dit zijn de uurprijzen die op de energiemarkt worden vastgesteld
  voor de volgende dag — de basis voor dynamische energiecontracten.

  API documentatie:
  https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html

  Gebruikte bibliotheek: entsoe-py
  https://github.com/EnergieID/entsoe-py
=============================================================
"""

# --- Standaard bibliotheken ---
from datetime import datetime, timedelta

# --- Externe bibliotheken ---
import pandas as pd
from entsoe import EntsoePandasClient   # Wrapper rond de ENTSO-E API

# --- Eigen modules ---
from config import Config


class EntsoEApi:
    """
    Klasse voor het ophalen van energieprijzen via de ENTSO-E API.

    Haalt DAY AHEAD prijzen op voor België in EUR/MWh.
    Zet deze automatisch om naar EUR/kWh voor gebruik in berekeningen.

    Gebruik:
    --------
    api = EntsoEApi()

    # Prijzen van vandaag
    prices = api.get_prices_today()

    # Prijs op dit moment
    current = api.get_current_price()
    print(current["price_eur_kwh"])
    """

    # Belgische bidding zone code voor ENTSO-E
    BIDDING_ZONE = "BE"

    def __init__(self):
        """Maak de ENTSO-E client aan met de API sleutel uit Config."""

        # API sleutel komt uit Config — DRY principe
        self.api_key = Config.ENTSOE_API_KEY

        # Maak de client aan — dit is de verbinding met de ENTSO-E API
        self.client = EntsoePandasClient(api_key=self.api_key)

        print(f"[INFO] ENTSO-E client aangemaakt voor zone: {self.BIDDING_ZONE}")

    # --------------------------------------------------
    #  Interne hulpmethoden (private)
    # --------------------------------------------------

    def _fetch_prices(self, start: datetime, end: datetime) -> pd.Series:
        """
        Haal ruwe prijsdata op van de ENTSO-E API.

        Parameters:
            start : startdatum van de periode
            end   : einddatum van de periode

        Geeft terug:
            pandas Series met prijzen in EUR/MWh per uur,
            of lege Series bij fout
        """
        try:
            # ENTSO-E verwacht tijdzones — we gebruiken Europees/Brussel
            start_ts = pd.Timestamp(start, tz="Europe/Brussels")
            end_ts   = pd.Timestamp(end,   tz="Europe/Brussels")

            # Haal de DAY AHEAD prijzen op
            prices = self.client.query_day_ahead_prices(
                country_code=self.BIDDING_ZONE,
                start=start_ts,
                end=end_ts
            )

            print(f"[INFO] {len(prices)} uurprijzen opgehaald van ENTSO-E")
            return prices

        except Exception as e:
            print(f"[FOUT] ENTSO-E API fout: {e}")
            return pd.Series(dtype=float)

    def _prices_to_list(self, prices: pd.Series) -> list:
        """
        Zet een pandas Series met prijzen om naar een lijst van dicts.

        Zet ook EUR/MWh om naar EUR/kWh:
        1 MWh = 1000 kWh → prijs / 1000

        Parameters:
            prices : pandas Series met prijzen in EUR/MWh

        Geeft terug:
            lijst van dicts met tijdstip en prijs per kWh
        """
        result = []

        for timestamp, price_mwh in prices.items():
            result.append({
                # Tijdstip omzetten naar leesbaar formaat zonder tijdzone
                "timestamp"      : timestamp.strftime("%d/%m/%Y %H:%M"),
                "price_eur_mwh"  : round(float(price_mwh), 2),
                # Delen door 1000: MWh → kWh
                "price_eur_kwh"  : round(float(price_mwh) / 1000, 6),
            })

        return result

    def _get_simulation_prices(self) -> list:
        """
        Geef nep-prijsdata terug als de API niet bereikbaar is.

        Simuleert een typisch dagpatroon met lagere prijzen 's nachts
        en hogere prijzen overdag.

        Geeft terug:
            lijst van 24 dicts met gesimuleerde uurprijzen
        """
        now   = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Typisch Belgisch dagpatroon in EUR/MWh
        simulation_prices = [
            45, 40, 38, 37, 36, 38,   # 00:00 - 05:00 (nacht, laag)
            55, 75, 95, 90, 85, 80,   # 06:00 - 11:00 (ochtendpiek)
            75, 70, 72, 78, 88, 98,   # 12:00 - 17:00 (middag)
            105, 100, 85, 70, 60, 50  # 18:00 - 23:00 (avondpiek → daling)
        ]

        result = []
        for hour, price_mwh in enumerate(simulation_prices):
            ts = today + timedelta(hours=hour)
            result.append({
                "timestamp"     : ts.strftime("%d/%m/%Y %H:%M"),
                "price_eur_mwh" : float(price_mwh),
                "price_eur_kwh" : round(price_mwh / 1000, 6),
            })

        return result

    # --------------------------------------------------
    #  Publieke methoden
    # --------------------------------------------------

    def get_prices_today(self) -> dict:
        """
        Haal de DAY AHEAD prijzen op voor vandaag.

        Geeft terug:
            dict met datum, prijslijst en statistieken
        """
        today    = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        prices = self._fetch_prices(start=today, end=tomorrow)

        # Val terug op simulatie als de API niet werkt
        if prices.empty:
            print("[INFO] Geen ENTSO-E data — simulatieprijzen worden gebruikt")
            price_list   = self._get_simulation_prices()
            is_simulation = True
        else:
            price_list    = self._prices_to_list(prices)
            is_simulation = False

        # Bereken statistieken
        kwh_prices = [p["price_eur_kwh"] for p in price_list]

        return {
            "date"          : today.strftime("%d/%m/%Y"),
            "is_simulation" : is_simulation,
            "prices"        : price_list,
            "stats"         : {
                "min_eur_kwh"  : round(min(kwh_prices), 6),
                "max_eur_kwh"  : round(max(kwh_prices), 6),
                "avg_eur_kwh"  : round(sum(kwh_prices) / len(kwh_prices), 6),
            }
        }

    def get_prices_tomorrow(self) -> dict:
        """
        Haal de DAY AHEAD prijzen op voor morgen.

        DAY AHEAD prijzen voor morgen zijn beschikbaar vanaf ~13:00.

        Geeft terug:
            dict met datum, prijslijst en statistieken
        """
        tomorrow        = datetime.now().replace(
                            hour=0, minute=0, second=0, microsecond=0
                          ) + timedelta(days=1)
        day_after       = tomorrow + timedelta(days=1)

        prices = self._fetch_prices(start=tomorrow, end=day_after)

        if prices.empty:
            return {
                "date"          : tomorrow.strftime("%d/%m/%Y"),
                "is_simulation" : False,
                "prices"        : [],
                "message"       : "Prijzen voor morgen nog niet beschikbaar (beschikbaar na 13:00)"
            }

        price_list = self._prices_to_list(prices)
        kwh_prices = [p["price_eur_kwh"] for p in price_list]

        return {
            "date"          : tomorrow.strftime("%d/%m/%Y"),
            "is_simulation" : False,
            "prices"        : price_list,
            "stats"         : {
                "min_eur_kwh"  : round(min(kwh_prices), 6),
                "max_eur_kwh"  : round(max(kwh_prices), 6),
                "avg_eur_kwh"  : round(sum(kwh_prices) / len(kwh_prices), 6),
            }
        }

    def get_current_price(self) -> dict:
        """
        Geef de actuele marktprijs terug voor dit uur.

        Geeft terug:
            dict met huidig tijdstip en bijhorende prijs
        """
        today_prices = self.get_prices_today()
        current_hour = datetime.now().strftime("%d/%m/%Y %H:00")

        # Zoek de prijs voor het huidige uur
        for entry in today_prices["prices"]:
            if entry["timestamp"] == current_hour:
                return {
                    "timestamp"     : entry["timestamp"],
                    "price_eur_mwh" : entry["price_eur_mwh"],
                    "price_eur_kwh" : entry["price_eur_kwh"],
                    "is_simulation" : today_prices["is_simulation"],
                }

        # Huidig uur niet gevonden — geef eerste beschikbare prijs
        if today_prices["prices"]:
            first = today_prices["prices"][0]
            return {
                "timestamp"     : first["timestamp"],
                "price_eur_mwh" : first["price_eur_mwh"],
                "price_eur_kwh" : first["price_eur_kwh"],
                "is_simulation" : today_prices["is_simulation"],
            }

        return {"error": "Geen prijsdata beschikbaar"}

    def get_prices_range(self, days_back: int = 7) -> list:
        """
        Haal prijzen op voor de laatste X dagen.

        Handig voor grafieken die meerdere dagen tonen.

        Parameters:
            days_back : aantal dagen terug (standaard: 7)

        Geeft terug:
            lijst met uurprijzen voor de volledige periode
        """
        end   = datetime.now()
        start = end - timedelta(days=days_back)

        prices = self._fetch_prices(start=start, end=end)

        if prices.empty:
            return []

        return self._prices_to_list(prices)