"""
=============================================================
  fluvius_importer.py — Fluvius historische data importeren
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Sessie:    6 — FluviusImporter klasse

  OOP principe: alle import-logica zit in 1 klasse
  DRY principe: bestandspaden staan 1x in de klasse

  Het Fluvius CSV-bestand heeft deze kenmerken:
  - Scheidingsteken : puntkomma (;)
  - Decimaalteken   : komma (,) — Belgisch formaat
  - Datumformaat    : d/MM/yyyy (zonder voorloopnul)
  - Twee rijen per kwartier: één Afname, één Injectie
  - Registers: 'Afname Nacht', 'Afname Dag',
               'Injectie Nacht', 'Injectie Dag'

  Bron: Mijn Fluvius — mijn.fluvius.be
=============================================================
"""

# --- Standaard bibliotheken ---
import os
from datetime import datetime

# --- Externe bibliotheken ---
import pandas as pd

# --- Eigen modules ---
from calculator import PriceCalculator


class FluviusImporter:
    """
    Klasse voor het importeren van Fluvius historische verbruiksdata.

    Leest het Fluvius CSV-bestand in, verwerkt de data en
    voegt ze toe aan het bestaande measurements.csv bestand.

    Gebruik:
    --------
    importer = FluviusImporter()
    result = importer.import_data()
    print(result["imported_rows"])
    """

    # Bestandspaden — relatief aan de projectmap
    FLUVIUS_FILE     = os.path.join("data", "historiek_elektriciteit.csv")
    MEASUREMENTS_FILE = os.path.join("data", "measurements.csv")

    # Kolomnamen zoals Fluvius ze gebruikt in het CSV-bestand
    COL_DATE_FROM = "Van (datum)"
    COL_TIME_FROM = "Van (tijdstip)"
    COL_REGISTER  = "Register"
    COL_VOLUME    = "Volume"

    # Mogelijke waarden in de Register kolom
    REGISTER_CONSUMPTION_DAY      = "Afname Dag"       # piekuren verbruik
    REGISTER_CONSUMPTION_NIGHT    = "Afname Nacht"     # daluren verbruik
    REGISTER_INJECTION_DAY        = "Injectie Dag"     # piekuren injectie
    REGISTER_INJECTION_NIGHT      = "Injectie Nacht"   # daluren injectie

    def __init__(self):
        """Maak de FluviusImporter aan."""
        self.calculator = PriceCalculator()

    # --------------------------------------------------
    #  Interne hulpmethoden (private)
    # --------------------------------------------------

    def _load_fluvius_csv(self) -> pd.DataFrame:
        """
        Laad het Fluvius CSV-bestand in als DataFrame.

        Let op de Belgische CSV-kenmerken:
        - Scheidingsteken is puntkomma (;) niet komma (,)
        - Decimaalteken is komma (,) niet punt (.)

        Geeft terug:
            DataFrame met de ruwe Fluvius data
        """
        try:
            df = pd.read_csv(
                self.FLUVIUS_FILE,
                sep=";",            # Fluvius gebruikt puntkomma als scheidingsteken
                decimal=",",        # Belgisch decimaalteken
                encoding="utf-8-sig" # Verwijdert eventuele BOM-tekens aan het begin
            )
            print(f"[INFO] Fluvius bestand geladen: {len(df)} rijen")
            return df

        except FileNotFoundError:
            print(f"[FOUT] Bestand niet gevonden: {self.FLUVIUS_FILE}")
            print(f"[FOUT] Zet het bestand in de data/ map")
            return pd.DataFrame()

        except Exception as e:
            print(f"[FOUT] Fout bij laden van Fluvius bestand: {e}")
            return pd.DataFrame()

    def _parse_timestamp(self, date_str: str, time_str: str) -> datetime:
        """
        Zet datum en tijdstip strings om naar een datetime object.

        Fluvius formaat: '1/01/2025' en '0:00:00'
        Pandas verwacht: '01/01/2025 00:00:00'

        Parameters:
            date_str : datum als string, bv. '1/01/2025'
            time_str : tijdstip als string, bv. '0:00:00'

        Geeft terug:
            datetime object
        """
        combined = f"{date_str} {time_str}"
        return pd.to_datetime(combined, format="%d/%m/%Y %H:%M:%S",
                              dayfirst=True)

    def _determine_tariff(self, register: str) -> int:
        """
        Bepaal het tarief op basis van het Fluvius register.

        Dag   = piekuren = tarief 1
        Nacht = daluren  = tarief 2

        Parameters:
            register : waarde uit de Register kolom

        Geeft terug:
            1 voor piek, 2 voor dal
        """
        if "Dag" in register:
            return 1    # piekuren
        else:
            return 2    # daluren (Nacht, of onbekend)

    def _process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Verwerk de ruwe Fluvius data naar ons measurements formaat.

        Stappen:
        1. Maak een timestamp kolom
        2. Splits op in Afname en Injectie
        3. Voeg samen per tijdstip (pivot)
        4. Bereken totaalkolommen
        5. Formatteer naar measurements.csv formaat

        Parameters:
            df : ruwe DataFrame van Fluvius

        Geeft terug:
            verwerkte DataFrame klaar voor opslaan
        """
        print("[INFO] Data verwerken...")

        # Stap 1: Maak een timestamp kolom van datum + tijdstip
        df["timestamp"] = pd.to_datetime(
            df[self.COL_DATE_FROM].astype(str) + " " +
            df[self.COL_TIME_FROM].astype(str),
            dayfirst=True
        )

        # Stap 2: Tarief bepalen op basis van register
        df["tariff"] = df[self.COL_REGISTER].apply(self._determine_tariff)

        # Stap 3: Volume kolom schoonmaken — zorg dat het een getal is
        df["volume"] = pd.to_numeric(df[self.COL_VOLUME], errors="coerce").fillna(0)

        # Stap 4: Maak aparte kolommen voor elk register type
        # pivot_table groepeert per tijdstip en maakt kolommen van de registers
        pivot = df.pivot_table(
            index=["timestamp", "tariff"],
            columns=self.COL_REGISTER,
            values="volume",
            aggfunc="sum"
        ).reset_index()

        # Zorg dat alle verwachte kolommen bestaan (niet alle registers zijn altijd aanwezig)
        for col in [self.REGISTER_CONSUMPTION_DAY,
                    self.REGISTER_CONSUMPTION_NIGHT,
                    self.REGISTER_INJECTION_DAY,
                    self.REGISTER_INJECTION_NIGHT]:
            if col not in pivot.columns:
                pivot[col] = 0.0

        # Stap 5: Verbruik en injectie per kwartier samenvoegen
        # Afname Dag + Afname Nacht = totaal verbruik per kwartier
        pivot["consumption_kwh"] = (
            pivot[self.REGISTER_CONSUMPTION_DAY].fillna(0) +
            pivot[self.REGISTER_CONSUMPTION_NIGHT].fillna(0)
        )
        pivot["injection_kwh"] = (
            pivot[self.REGISTER_INJECTION_DAY].fillna(0) +
            pivot[self.REGISTER_INJECTION_NIGHT].fillna(0)
        )

        # Stap 6: Vermogen berekenen in Watt
        # kWh per kwartier × 4 × 1000 = gemiddeld Watt in dat kwartier
        # (want 1 kwartier = 1/4 uur, dus kWh × 4 = kW, × 1000 = W)
        pivot["current_power_w"] = (
            (pivot["consumption_kwh"] - pivot["injection_kwh"]) * 4 * 1000
        ).round(0).astype(int)

        # Stap 7: Formatteer timestamp naar ons formaat
        pivot["timestamp_str"] = pivot["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")

        print(f"[INFO] {len(pivot)} kwartiermetingen verwerkt")
        return pivot

    def _convert_to_measurements_format(self, pivot: pd.DataFrame) -> pd.DataFrame:
        """
        Zet de verwerkte Fluvius data om naar het measurements.csv formaat.

        We berekenen cumulatieve totalen omdat measurements.csv
        de lopende teller bijhoudt (net zoals de echte meter).

        Parameters:
            pivot : verwerkte DataFrame van _process_data()

        Geeft terug:
            DataFrame klaar om toe te voegen aan measurements.csv
        """
        print("[INFO] Omzetten naar measurements formaat...")

        # Sorteer op tijdstip — oudste eerst
        pivot = pivot.sort_values("timestamp").reset_index(drop=True)

        # Bereken cumulatieve totalen (lopende teller)
        # cumsum() telt alle vorige waarden op — net zoals een echte meter
        pivot["total_consumption_peak_kwh"]     = pivot.apply(
            lambda r: r["consumption_kwh"] if r["tariff"] == 1 else 0, axis=1
        ).cumsum().round(3)

        pivot["total_consumption_off_peak_kwh"] = pivot.apply(
            lambda r: r["consumption_kwh"] if r["tariff"] == 2 else 0, axis=1
        ).cumsum().round(3)

        pivot["total_injection_peak_kwh"]       = pivot.apply(
            lambda r: r["injection_kwh"] if r["tariff"] == 1 else 0, axis=1
        ).cumsum().round(3)

        pivot["total_injection_off_peak_kwh"]   = pivot.apply(
            lambda r: r["injection_kwh"] if r["tariff"] == 2 else 0, axis=1
        ).cumsum().round(3)

        pivot["total_consumption_kwh"] = (
            pivot["total_consumption_peak_kwh"] +
            pivot["total_consumption_off_peak_kwh"]
        ).round(3)

        pivot["total_injection_kwh"] = (
            pivot["total_injection_peak_kwh"] +
            pivot["total_injection_off_peak_kwh"]
        ).round(3)

        # Bouw de uiteindelijke DataFrame op in measurements.csv formaat
        result = pd.DataFrame({
            "timestamp"                     : pivot["timestamp_str"],
            "current_power_w"               : pivot["current_power_w"],
            "active_tariff"                 : pivot["tariff"],
            "total_consumption_kwh"         : pivot["total_consumption_kwh"],
            "total_consumption_peak_kwh"    : pivot["total_consumption_peak_kwh"],
            "total_consumption_off_peak_kwh": pivot["total_consumption_off_peak_kwh"],
            "total_injection_kwh"           : pivot["total_injection_kwh"],
            "total_injection_peak_kwh"      : pivot["total_injection_peak_kwh"],
            "total_injection_off_peak_kwh"  : pivot["total_injection_off_peak_kwh"],
            "total_gas_m3"                  : 0.0,   # gas zit niet in elektriciteitsbestand
            "is_simulation"                 : False,
        })

        return result

    def _check_already_imported(self, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Verwijder rijen die al in measurements.csv staan.

        Zo kan je de import meerdere keren uitvoeren zonder duplicaten.

        Parameters:
            new_df : nieuwe data om te importeren

        Geeft terug:
            DataFrame zonder duplicaten
        """
        if not os.path.exists(self.MEASUREMENTS_FILE):
            return new_df

        try:
            existing = pd.read_csv(self.MEASUREMENTS_FILE)
            if existing.empty:
                return new_df

            # Verwijder rijen waarvan de timestamp al bestaat
            existing_timestamps = set(existing["timestamp"].astype(str))
            filtered = new_df[~new_df["timestamp"].astype(str).isin(existing_timestamps)]

            skipped = len(new_df) - len(filtered)
            if skipped > 0:
                print(f"[INFO] {skipped} rijen overgeslagen — al geïmporteerd")

            return filtered

        except Exception:
            return new_df

    # --------------------------------------------------
    #  Publieke methoden
    # --------------------------------------------------

    def import_data(self) -> dict:
        """
        Importeer de Fluvius historische data naar measurements.csv.

        Dit is de hoofdmethode die alles in de juiste volgorde uitvoert.

        Geeft terug:
            dict met resultaat van de import
        """
        print("[INFO] Fluvius import gestart...")

        # Stap 1: Laad het Fluvius bestand
        raw_df = self._load_fluvius_csv()
        if raw_df.empty:
            return {"success": False, "error": "Fluvius bestand niet gevonden of leeg"}

        # Stap 2: Verwerk de data
        processed = self._process_data(raw_df)

        # Stap 3: Zet om naar measurements formaat
        measurements = self._convert_to_measurements_format(processed)

        # Stap 4: Verwijder duplicaten
        measurements = self._check_already_imported(measurements)

        if measurements.empty:
            return {
                "success"       : True,
                "imported_rows" : 0,
                "message"       : "Alle data was al geïmporteerd"
            }

        # Stap 5: Voeg toe aan measurements.csv
        try:
            measurements.to_csv(
                self.MEASUREMENTS_FILE,
                mode="a",       # toevoegen aan bestaand bestand
                header=False,   # geen kolomnamen opnieuw schrijven
                index=False
            )

            print(f"[INFO] Import geslaagd: {len(measurements)} rijen toegevoegd")

            return {
                "success"       : True,
                "imported_rows" : len(measurements),
                "first_date"    : measurements["timestamp"].iloc[0],
                "last_date"     : measurements["timestamp"].iloc[-1],
                "message"       : f"{len(measurements)} kwartiermetingen geïmporteerd"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_summary(self) -> dict:
        """
        Geef een samenvatting van het Fluvius bestand zonder te importeren.

        Handig om eerst te controleren wat er in het bestand zit
        voordat je de import uitvoert.

        Geeft terug:
            dict met info over het bestand
        """
        raw_df = self._load_fluvius_csv()
        if raw_df.empty:
            return {"error": "Bestand niet gevonden"}

        # Datum kolom omzetten
        raw_df["timestamp"] = pd.to_datetime(
            raw_df[self.COL_DATE_FROM].astype(str) + " " +
            raw_df[self.COL_TIME_FROM].astype(str),
            dayfirst=True
        )

        return {
            "total_rows"     : len(raw_df),
            "first_date"     : raw_df["timestamp"].min().strftime("%d/%m/%Y"),
            "last_date"      : raw_df["timestamp"].max().strftime("%d/%m/%Y"),
            "register_types" : raw_df[self.COL_REGISTER].unique().tolist(),
            "file_path"      : self.FLUVIUS_FILE,
        }