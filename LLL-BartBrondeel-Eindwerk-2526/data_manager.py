"""
=============================================================
  data_manager.py — Opslaan en ophalen van metingen
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Sessie:    5 — DataManager klasse

  OOP principe: alle data-logica zit in 1 klasse
  DRY principe: bestandspad staat 1x in de klasse

  Metingen worden opgeslagen in een CSV-bestand.
  CSV = Comma Separated Values — gewoon een tekstbestand
  dat je ook in Excel kan openen.

  Twee soorten data in het CSV-bestand:
  1. Fluvius historische data (gas = 0, eigen cumulatieve teller)
  2. Live meterdata (gas > 0, echte metertotalen)

  Belangrijk: beide datasets gebruiken een ANDERE referentie
  voor de cumulatieve totalen. Ze worden daarom nooit gemengd
  in berekeningen — elke periode gebruikt één consistente bron.

  Kolommen in het CSV-bestand:
    timestamp                     : tijdstip van de meting
    current_power_w               : huidig vermogen in Watt
    active_tariff                 : actief tarief (1=piek, 2=dal)
    total_consumption_kwh         : totaal verbruik ooit
    total_consumption_peak_kwh    : totaal verbruik piekuren
    total_consumption_off_peak_kwh: totaal verbruik daluren
    total_injection_kwh           : totaal injectie ooit
    total_injection_peak_kwh      : totaal injectie piekuren
    total_injection_off_peak_kwh  : totaal injectie daluren
    total_gas_m3                  : totaal gasverbruik
    is_simulation                 : True als het nep-data is
=============================================================
"""

# --- Standaard bibliotheken ---
import os
from datetime import datetime, timedelta

# --- Externe bibliotheken ---
import pandas as pd     # Lezen en schrijven van CSV-bestanden

# --- Eigen modules ---
from meter import HomeWizardMeter
from calculator import PriceCalculator


class DataManager:
    """
    Klasse voor het opslaan en ophalen van energiemetingen.

    Elke meting wordt als een rij toegevoegd aan een CSV-bestand.
    Zo bouw je automatisch historiek op zolang de app draait.

    Gebruik:
    --------
    manager = DataManager()

    # Sla een meting op
    manager.save_measurement()

    # Haal metingen op van vandaag
    data = manager.get_today()
    """

    # Bestandspad voor het CSV-bestand — relatief aan de projectmap
    DATA_FILE = os.path.join("data", "measurements.csv")

    # Kolomnamen van het CSV-bestand — volgorde is belangrijk!
    COLUMNS = [
        "timestamp",
        "current_power_w",
        "active_tariff",
        "total_consumption_kwh",
        "total_consumption_peak_kwh",
        "total_consumption_off_peak_kwh",
        "total_injection_kwh",
        "total_injection_peak_kwh",
        "total_injection_off_peak_kwh",
        "total_gas_m3",
        "is_simulation",
    ]

    def __init__(self):
        """Maak de DataManager aan en zorg dat het CSV-bestand bestaat."""

        # Objecten voor meterdata en berekeningen
        self.meter      = HomeWizardMeter()
        self.calculator = PriceCalculator()

        # Maak het CSV-bestand aan als het nog niet bestaat
        self._initialize_file()

    # --------------------------------------------------
    #  Interne hulpmethoden (private)
    # --------------------------------------------------

    def _initialize_file(self):
        """
        Maak het CSV-bestand aan als het nog niet bestaat.

        Zo hoef je nooit handmatig een bestand aan te maken.
        Bij een bestaand bestand wordt niets gewijzigd.
        """
        # Maak de data/ map aan als die nog niet bestaat
        os.makedirs("data", exist_ok=True)

        # Maak het CSV-bestand aan met kolomnamen als het nog niet bestaat
        if not os.path.exists(self.DATA_FILE):
            df = pd.DataFrame(columns=self.COLUMNS)
            df.to_csv(self.DATA_FILE, index=False)
            print(f"[INFO] Nieuw CSV-bestand aangemaakt: {self.DATA_FILE}")
        else:
            print(f"[INFO] Bestaand CSV-bestand gevonden: {self.DATA_FILE}")

    def _load_all(self) -> pd.DataFrame:
        """
        Laad alle metingen uit het CSV-bestand.

        Geeft terug:
            DataFrame met alle metingen, gesorteerd op tijdstip
        """
        try:
            df = pd.read_csv(self.DATA_FILE)

            # Zet de timestamp kolom om naar een echt datum-object
            # Zo kan pandas filteren op dag, week, maand
            df["timestamp"] = pd.to_datetime(
                df["timestamp"],
                format="%d/%m/%Y %H:%M:%S"
            )
            return df

        except pd.errors.EmptyDataError:
            # Bestand is leeg — geef een lege DataFrame terug
            return pd.DataFrame(columns=self.COLUMNS)

    def _load_fluvius_only(self) -> pd.DataFrame:
        """
        Laad enkel de Fluvius historische metingen.

        Fluvius data herken je aan:
          - is_simulation = False
          - total_gas_m3  = 0 (gas zit niet in de elektriciteits-export)

        Deze data heeft een eigen cumulatieve teller vanaf 01/01/2025.
        NOOIT mengen met live meterdata voor berekeningen!

        Geeft terug:
            DataFrame met enkel Fluvius metingen, gesorteerd op tijdstip
        """
        df = self._load_all()

        if df.empty:
            return df

        # Zet is_simulation om naar boolean voor correcte vergelijking
        df["is_simulation"] = df["is_simulation"].astype(str).str.lower() == "true"

        return df[
            (df["is_simulation"] == False) &
            (df["total_gas_m3"]   == 0)
        ].sort_values("timestamp").reset_index(drop=True)

    def _load_live_only(self) -> pd.DataFrame:
        """
        Laad enkel de live metingen van de echte meter.

        Live data herken je aan:
          - is_simulation = False
          - total_gas_m3  > 0 (echte meter levert gasdata)

        Deze data heeft de echte metertotalen (cumulatief
        vanaf de installatie van de meter — jaren geleden).
        NOOIT mengen met Fluvius data voor berekeningen!

        Geeft terug:
            DataFrame met enkel live metingen, gesorteerd op tijdstip
        """
        df = self._load_all()

        if df.empty:
            return df

        # Zet is_simulation om naar boolean voor correcte vergelijking
        df["is_simulation"] = df["is_simulation"].astype(str).str.lower() == "true"

        return df[
            (df["is_simulation"] == False) &
            (df["total_gas_m3"]   >  0)
        ].sort_values("timestamp").reset_index(drop=True)

    def _calculate_period_costs(self, df: pd.DataFrame) -> dict:
        """
        Bereken de kostprijzen voor een periode op basis van de metingen.

        Gebruikt het verschil tussen de eerste en laatste meting
        om het verbruik in de periode te berekenen.

        Beide metingen MOETEN uit dezelfde dataset komen
        (beide Fluvius OF beide live) anders zijn de totalen
        niet vergelijkbaar en geeft de berekening een fout resultaat.

        Parameters:
            df : DataFrame met metingen uit één consistente dataset

        Geeft terug:
            dict met verbruik en kostprijzen voor de periode
        """
        # Als er minder dan 2 metingen zijn, kunnen we niets berekenen
        if len(df) < 2:
            return {"error": "Niet genoeg metingen voor berekening"}

        # Eerste en laatste meting in de periode
        first = df.iloc[0]
        last  = df.iloc[-1]

        # Verbruik = verschil tussen laatste en eerste meting
        peak_kwh     = max(0, round(last["total_consumption_peak_kwh"]
                                    - first["total_consumption_peak_kwh"],     3))
        off_peak_kwh = max(0, round(last["total_consumption_off_peak_kwh"]
                                    - first["total_consumption_off_peak_kwh"], 3))
        inj_peak_kwh = max(0, round(last["total_injection_peak_kwh"]
                                    - first["total_injection_peak_kwh"],       3))
        inj_off_peak = max(0, round(last["total_injection_off_peak_kwh"]
                                    - first["total_injection_off_peak_kwh"],   3))
        gas_m3       = max(0, round(last["total_gas_m3"]
                                    - first["total_gas_m3"],                   3))

        # Bereken de kostprijs via de PriceCalculator
        costs = self.calculator.calculate_daily_cost(
            peak_kwh=peak_kwh,
            off_peak_kwh=off_peak_kwh,
            peak_injection_kwh=inj_peak_kwh,
            off_peak_injection_kwh=inj_off_peak,
        )

        return {
            "period_start"              : first["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "period_end"                : last["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "number_of_measurements"    : len(df),
            "consumption_peak_kwh"      : peak_kwh,
            "consumption_off_peak_kwh"  : off_peak_kwh,
            "injection_peak_kwh"        : inj_peak_kwh,
            "injection_off_peak_kwh"    : inj_off_peak,
            "gas_m3"                    : gas_m3,
            "costs"                     : costs,
        }

    # --------------------------------------------------
    #  Publieke methoden — bruikbaar van buitenaf
    # --------------------------------------------------

    def save_measurement(self) -> bool:
        """
        Haal een actuele meting op en sla ze op in het CSV-bestand.

        Geeft terug:
            True als de meting succesvol is opgeslagen, anders False
        """
        # Haal actuele data op van de meter
        data = self.meter.get_summary()

        # Maak een nieuwe rij aan met enkel de kolommen die we bewaren
        new_row = {
            "timestamp"                     : data.get("timestamp"),
            "current_power_w"               : data.get("current_power_w"),
            "active_tariff"                 : data.get("active_tariff"),
            "total_consumption_kwh"         : data.get("total_consumption_kwh"),
            "total_consumption_peak_kwh"    : data.get("total_consumption_peak_kwh"),
            "total_consumption_off_peak_kwh": data.get("total_consumption_off_peak_kwh"),
            "total_injection_kwh"           : data.get("total_injection_kwh"),
            "total_injection_peak_kwh"      : data.get("total_injection_peak_kwh"),
            "total_injection_off_peak_kwh"  : data.get("total_injection_off_peak_kwh"),
            "total_gas_m3"                  : data.get("total_gas_m3"),
            "is_simulation"                 : data.get("is_simulation"),
        }

        try:
            # Voeg de nieuwe rij toe aan het CSV-bestand
            # mode="a" = append (toevoegen aan bestaand bestand)
            # header=False = geen kolomnamen opnieuw schrijven
            df = pd.DataFrame([new_row])
            df.to_csv(self.DATA_FILE, mode="a", header=False, index=False)

            print(f"[INFO] Meting opgeslagen: {new_row['timestamp']} | "
                  f"{new_row['current_power_w']}W | "
                  f"tarief {new_row['active_tariff']}")
            return True

        except Exception as e:
            print(f"[FOUT] Meting kon niet worden opgeslagen: {e}")
            return False

    def get_today(self) -> dict:
        """
        Bereken het verbruik van vandaag.

        Gebruikt de laatste meting van gisteren als beginstand
        en vergelijkt die met de huidige live meterstand.

        Vandaag gebruikt LIVE data — die heeft de echte gas- en
        elektriciteitstotalen van de meter.

        Geeft terug:
            dict met verbruik en kostprijs van vandaag
        """
        df = self._load_all()

        if df.empty:
            return {"error": "Geen metingen beschikbaar"}

        # Begin van vandaag = middernacht
        today_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # Laatste meting van gisteren = beginstand van vandaag
        yesterday_df = df[df["timestamp"] < today_start].sort_values("timestamp")

        if yesterday_df.empty:
            return {"error": "Geen beginstand beschikbaar"}

        # Neem de laatste meting van gisteren als beginstand
        baseline = yesterday_df.iloc[-1]

        # Huidige live meterstand ophalen
        live_data = self.meter.get_summary()

        # Verbruik vandaag = live stand - beginstand gisteren
        peak_kwh     = max(0, round(live_data.get("total_consumption_peak_kwh", 0)
                                    - baseline["total_consumption_peak_kwh"],     3))
        off_peak_kwh = max(0, round(live_data.get("total_consumption_off_peak_kwh", 0)
                                    - baseline["total_consumption_off_peak_kwh"], 3))
        inj_peak     = max(0, round(live_data.get("total_injection_peak_kwh", 0)
                                    - baseline["total_injection_peak_kwh"],       3))
        inj_off_peak = max(0, round(live_data.get("total_injection_off_peak_kwh", 0)
                                    - baseline["total_injection_off_peak_kwh"],   3))
        gas_m3       = max(0, round(live_data.get("total_gas_m3", 0)
                                    - baseline["total_gas_m3"],                   3))

        # Bereken kostprijs
        costs = self.calculator.calculate_daily_cost(
            peak_kwh=peak_kwh,
            off_peak_kwh=off_peak_kwh,
            peak_injection_kwh=inj_peak,
            off_peak_injection_kwh=inj_off_peak,
        )

        return {
            "period_start"              : baseline["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "period_end"                : datetime.now().strftime("%d/%m/%Y %H:%M"),
            "consumption_peak_kwh"      : peak_kwh,
            "consumption_off_peak_kwh"  : off_peak_kwh,
            "injection_peak_kwh"        : inj_peak,
            "injection_off_peak_kwh"    : inj_off_peak,
            "gas_m3"                    : gas_m3,
            "costs"                     : costs,
        }

    def get_week(self) -> dict:
        """
        Geef verbruik en kostprijs van de laatste 7 dagen terug.

        Gebruikt live meterdata met baseline aanpak —
        zelfde methode als get_today() maar dan 7 dagen terug.

        Geeft terug:
            dict met verbruik en kostprijs van de laatste 7 dagen
        """
        df = self._load_live_only()

        if df.empty:
            return {"error": "Geen live metingen beschikbaar"}

        # Beginpunt = 7 dagen geleden
        week_start = datetime.now() - timedelta(days=7)

        # Laatste meting voor het beginpunt = beginstand
        before_df = df[df["timestamp"] < week_start].sort_values("timestamp")

        if before_df.empty:
            # Geen meting van 7 dagen geleden — gebruik oudste live meting
            before_df = df.sort_values("timestamp")
            print("[INFO] Geen meting van 7 dagen geleden — oudste live meting gebruikt")

        baseline = before_df.iloc[-1]
        live_data = self.meter.get_summary()

        # Verbruik = live stand - beginstand
        peak_kwh = max(0, round(live_data.get("total_consumption_peak_kwh", 0)
                                - baseline["total_consumption_peak_kwh"], 3))
        off_peak_kwh = max(0, round(live_data.get("total_consumption_off_peak_kwh", 0)
                                    - baseline["total_consumption_off_peak_kwh"], 3))
        inj_peak = max(0, round(live_data.get("total_injection_peak_kwh", 0)
                                - baseline["total_injection_peak_kwh"], 3))
        inj_off_peak = max(0, round(live_data.get("total_injection_off_peak_kwh", 0)
                                    - baseline["total_injection_off_peak_kwh"], 3))
        gas_m3 = max(0, round(live_data.get("total_gas_m3", 0)
                              - baseline["total_gas_m3"], 3))

        costs = self.calculator.calculate_daily_cost(
            peak_kwh=peak_kwh,
            off_peak_kwh=off_peak_kwh,
            peak_injection_kwh=inj_peak,
            off_peak_injection_kwh=inj_off_peak,
        )

        return {
            "period_start": baseline["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "period_end": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "consumption_peak_kwh": peak_kwh,
            "consumption_off_peak_kwh": off_peak_kwh,
            "injection_peak_kwh": inj_peak,
            "injection_off_peak_kwh": inj_off_peak,
            "gas_m3": gas_m3,
            "costs": costs,
        }

    def get_month(self) -> dict:
        """
        Geef verbruik en kostprijs van de laatste 30 dagen terug.

        Gebruikt enkel Fluvius data zodat de cumulatieve totalen
        consistent zijn (geen mix met live metertotalen).

        Opmerking: gas is niet beschikbaar in de Fluvius
        elektriciteits-export — gas_m3 is altijd 0 hier.

        Geeft terug:
            dict met verbruik en kostprijs van de laatste 30 dagen
        """
        df     = self._load_fluvius_only()
        cutoff = datetime.now() - timedelta(days=30)

        filtered = df[df["timestamp"] >= cutoff]

        if len(filtered) < 2:
            return {"error": "Niet genoeg Fluvius metingen voor deze periode"}

        return self._calculate_period_costs(filtered)

    def get_year(self) -> dict:
        """
        Geef verbruik en kostprijs van het afgelopen jaar terug.

        Gebruikt enkel Fluvius data zodat de cumulatieve totalen
        consistent zijn. Vergelijkt eerste en laatste meting
        binnen het jaarbereik.

        Opmerking: gas is niet beschikbaar in de Fluvius
        elektriciteits-export — gas_m3 is altijd 0 hier.

        Geeft terug:
            dict met verbruik en kostprijs van het afgelopen jaar
        """
        df     = self._load_fluvius_only()
        cutoff = datetime.now() - timedelta(days=365)

        # Laatste meting voor het beginpunt als baseline
        before_df = df[df["timestamp"] < cutoff].sort_values("timestamp")

        if before_df.empty:
            # Geen meting van voor een jaar geleden — gebruik oudste meting
            before_df = df.sort_values("timestamp")
            print("[INFO] Geen meting van 365 dagen geleden — oudste meting gebruikt")

        if df.empty:
            return {"error": "Geen Fluvius metingen beschikbaar"}

        baseline = before_df.iloc[-1]
        last     = df.iloc[-1]

        # Verbruik = laatste Fluvius meting - beginstand
        peak_kwh     = max(0, round(last["total_consumption_peak_kwh"]
                                    - baseline["total_consumption_peak_kwh"],     3))
        off_peak_kwh = max(0, round(last["total_consumption_off_peak_kwh"]
                                    - baseline["total_consumption_off_peak_kwh"], 3))
        inj_peak     = max(0, round(last["total_injection_peak_kwh"]
                                    - baseline["total_injection_peak_kwh"],       3))
        inj_off_peak = max(0, round(last["total_injection_off_peak_kwh"]
                                    - baseline["total_injection_off_peak_kwh"],   3))

        # Kostprijs berekenen
        costs = self.calculator.calculate_daily_cost(
            peak_kwh=peak_kwh,
            off_peak_kwh=off_peak_kwh,
            peak_injection_kwh=inj_peak,
            off_peak_injection_kwh=inj_off_peak,
        )

        return {
            "period_start"              : baseline["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "period_end"                : last["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "consumption_peak_kwh"      : peak_kwh,
            "consumption_off_peak_kwh"  : off_peak_kwh,
            "injection_peak_kwh"        : inj_peak,
            "injection_off_peak_kwh"    : inj_off_peak,
            "gas_m3"                    : 0,   # niet beschikbaar in Fluvius elektriciteits-export
            "costs"                     : costs,
        }

    def get_recent_measurements(self, limit: int = 10) -> list:
        """
        Geef de meest recente metingen terug als lijst.

        Parameters:
            limit : aantal metingen om terug te geven (standaard: 10)

        Geeft terug:
            lijst van dicts, gesorteerd van nieuw naar oud
        """
        df = self._load_all()

        if df.empty:
            return []

        # Sorteer van nieuw naar oud en neem de laatste X metingen
        df = df.sort_values("timestamp", ascending=False).head(limit)

        # Zet timestamp terug naar leesbare string
        df["timestamp"] = df["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")

        return df.to_dict(orient="records")