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

  Kolommen in het CSV-bestand:
    timestamp                   : tijdstip van de meting
    current_power_w             : huidig vermogen in Watt
    active_tariff               : actief tarief (1=piek, 2=dal)
    total_consumption_kwh       : totaal verbruik ooit
    total_consumption_peak_kwh  : totaal verbruik piekuren
    total_consumption_off_peak_kwh: totaal verbruik daluren
    total_injection_kwh         : totaal injectie ooit
    total_injection_peak_kwh    : totaal injectie piekuren
    total_injection_off_peak_kwh: totaal injectie daluren
    total_gas_m3                : totaal gasverbruik
    is_simulation               : True als het nep-data is
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
            df["timestamp"] = pd.to_datetime(df["timestamp"],
                                             format="%d/%m/%Y %H:%M:%S")
            return df

        except pd.errors.EmptyDataError:
            # Bestand is leeg — geef een lege DataFrame terug
            return pd.DataFrame(columns=self.COLUMNS)

    def _filter_by_period(self, days: int) -> pd.DataFrame:
        """
        Geef metingen terug van de laatste X dagen.
        Sorteert op tijdstip zodat eerste/laatste correct zijn.
        """
        df = self._load_all()

        if df.empty:
            return df

        cutoff = datetime.now() - timedelta(days=days)
        filtered = df[df["timestamp"] >= cutoff]

        # Sorteer op tijdstip — oudste eerst
        return filtered.sort_values("timestamp").reset_index(drop=True)

    def _calculate_period_costs(self, df: pd.DataFrame) -> dict:
        """
        Bereken de kostprijzen voor een periode op basis van de metingen.

        Gebruikt het verschil tussen de eerste en laatste meting
        om het verbruik in de periode te berekenen.

        Parameters:
            df : DataFrame met metingen uit een bepaalde periode

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
        peak_kwh     = round(last["total_consumption_peak_kwh"]     - first["total_consumption_peak_kwh"],     3)
        off_peak_kwh = round(last["total_consumption_off_peak_kwh"] - first["total_consumption_off_peak_kwh"], 3)
        inj_peak_kwh = round(last["total_injection_peak_kwh"]       - first["total_injection_peak_kwh"],       3)
        inj_off_peak = round(last["total_injection_off_peak_kwh"]   - first["total_injection_off_peak_kwh"],   3)
        gas_m3       = round(last["total_gas_m3"]                   - first["total_gas_m3"],                   3)

        # Bereken de kostprijs via de PriceCalculator
        costs = self.calculator.calculate_daily_cost(
            peak_kwh=peak_kwh,
            off_peak_kwh=off_peak_kwh,
            peak_injection_kwh=inj_peak_kwh,
            off_peak_injection_kwh=inj_off_peak,
        )

        return {
            "period_start"          : first["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "period_end"            : last["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "number_of_measurements": len(df),
            "consumption_peak_kwh"  : peak_kwh,
            "consumption_off_peak_kwh": off_peak_kwh,
            "injection_peak_kwh"    : inj_peak_kwh,
            "injection_off_peak_kwh": inj_off_peak,
            "gas_m3"                : gas_m3,
            "costs"                 : costs,
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

        # Sla simulatiedata ook op — handig voor testen
        # Maak een nieuwe rij aan met enkel de kolommen die we willen bewaren
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
        peak_kwh = round(live_data.get("total_consumption_peak_kwh", 0)
                         - baseline["total_consumption_peak_kwh"], 3)
        off_peak_kwh = round(live_data.get("total_consumption_off_peak_kwh", 0)
                             - baseline["total_consumption_off_peak_kwh"], 3)
        inj_peak = round(live_data.get("total_injection_peak_kwh", 0)
                         - baseline["total_injection_peak_kwh"], 3)
        inj_off_peak = round(live_data.get("total_injection_off_peak_kwh", 0)
                             - baseline["total_injection_off_peak_kwh"], 3)
        gas_m3 = round(live_data.get("total_gas_m3", 0)
                       - baseline["total_gas_m3"], 3)

        # Negatieve waarden vermijden bij afrondingsverschillen
        peak_kwh = max(0, peak_kwh)
        off_peak_kwh = max(0, off_peak_kwh)
        inj_peak = max(0, inj_peak)
        inj_off_peak = max(0, inj_off_peak)
        gas_m3 = max(0, gas_m3)

        # Bereken kostprijs
        costs = self.calculator.calculate_daily_cost(
            peak_kwh=peak_kwh,
            off_peak_kwh=off_peak_kwh,
            peak_injection_kwh=inj_peak,
            off_peak_injection_kwh=inj_off_peak,
        )

        return {
            "period_start": baseline["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "period_end": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "baseline_date": baseline["timestamp"].strftime("%d/%m/%Y %H:%M"),
            "consumption_peak_kwh": peak_kwh,
            "consumption_off_peak_kwh": off_peak_kwh,
            "injection_peak_kwh": inj_peak,
            "injection_off_peak_kwh": inj_off_peak,
            "gas_m3": gas_m3,
            "costs": costs,
        }

    def get_week(self) -> dict:
        """Geef de metingen en kostprijs van de laatste 7 dagen terug."""
        df = self._filter_by_period(days=7)
        return self._calculate_period_costs(df)

    def get_month(self) -> dict:
        """Geef de metingen en kostprijs van de laatste 30 dagen terug."""
        df = self._filter_by_period(days=30)
        return self._calculate_period_costs(df)

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