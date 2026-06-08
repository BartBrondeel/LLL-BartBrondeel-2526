"""
=============================================================
  calculator.py — Kostprijsberekeningen voor het Energie Dashboard
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Sessie:    4 — PriceCalculator klasse

  OOP principe: alle berekeningslogica zit in 1 klasse
  DRY principe: tarieven komen uit Config, nergens anders

  Tarievenstructuur (Luminus ESTC2.0, sociaal tarief april-juni 2026):
  - Piekuren  (tarief 1): ma-vr 07:00-22:00
  - Daluren   (tarief 2): ma-vr 22:00-07:00 + weekends
=============================================================
"""

# --- Standaard bibliotheken ---
from datetime import datetime

# --- Eigen modules ---
from config import Config


class PriceCalculator:
    """
    Klasse voor het berekenen van energiekostprijzen.

    Gebruikt de tarieven uit Config om te berekenen
    hoeveel een bepaald verbruik kost in euro's.

    Gebruik:
    --------
    calc = PriceCalculator()

    # Kostprijs voor 3.5 kWh tijdens piekuren
    cost = calc.calculate_cost(kwh=3.5, tariff=1)

    # Huidige kostprijs per uur op basis van live vermogen
    hourly = calc.calculate_hourly_cost(power_w=850, tariff=1)
    """

    def __init__(self):
        """Laad de tarieven uit Config bij aanmaken van het object."""

        # --- Aankoop tarieven (wat je betaalt aan het net) ---
        self.peak_price    = Config.PRIJS_PIEK_PER_KWH   # piekuren  (tarief 1)
        self.off_peak_price = Config.PRIJS_DAL_PER_KWH   # daluren   (tarief 2)

        # --- Injectie tarieven (wat je krijgt voor teruglevering) ---
        self.injection_peak_price    = Config.INJECTIE_PIEK_PER_KWH
        self.injection_off_peak_price = Config.INJECTIE_DAL_PER_KWH

    # --------------------------------------------------
    #  Hulpmethoden (private)
    # --------------------------------------------------

    def _get_price_for_tariff(self, tariff: int, injection: bool = False) -> float:
        """
        Geef de juiste prijs terug op basis van het actieve tarief.

        Parameters:
            tariff    : 1 = piek, 2 = dal (komt rechtstreeks van de meter)
            injection : True als het gaat om teruglevering aan het net

        Geeft terug:
            prijs per kWh in euro
        """
        if injection:
            # Injectietarief: je krijgt geld terug voor zonnepanelen
            return self.injection_peak_price if tariff == 1 else self.injection_off_peak_price
        else:
            # Aankooptarief: je betaalt voor verbruik van het net
            return self.peak_price if tariff == 1 else self.off_peak_price

    def _is_peak_hour(self, dt: datetime = None) -> bool:
        """
        Bepaal of een tijdstip een piekuur is.

        Piekuren: maandag t/m vrijdag tussen 07:00 en 22:00
        Daluren : weekends + weekdagen buiten piekuren

        Parameters:
            dt : tijdstip om te controleren (standaard = nu)

        Geeft terug:
            True als het een piekuur is, anders False
        """
        # Gebruik het huidige tijdstip als er geen tijdstip meegegeven is
        if dt is None:
            dt = datetime.now()

        # weekday(): 0 = maandag, 6 = zondag
        is_weekday    = dt.weekday() < 5           # ma t/m vr
        is_peak_time  = 7 <= dt.hour < 22          # tussen 07:00 en 22:00

        return is_weekday and is_peak_time

    # --------------------------------------------------
    #  Publieke methoden
    # --------------------------------------------------

    def get_current_tariff(self, dt: datetime = None) -> int:
        """
        Geef het huidige tarief terug als getal.

        Geeft terug:
            1 = piekuren, 2 = daluren
        """
        return 1 if self._is_peak_hour(dt) else 2

    def calculate_cost(self, kwh: float, tariff: int, injection: bool = False) -> float:
        """
        Bereken de kostprijs voor een bepaald verbruik.

        Parameters:
            kwh       : verbruik in kilowattuur
            tariff    : 1 = piek, 2 = dal
            injection : True als het gaat om teruglevering

        Geeft terug:
            kostprijs in euro (afgerond op 4 decimalen)

        Voorbeeld:
            calculate_cost(kwh=5.0, tariff=1)
            → 5.0 × 0.2797 = €1.3985
        """
        price = self._get_price_for_tariff(tariff, injection)
        return round(kwh * price, 4)

    def calculate_hourly_cost(self, power_w: float, tariff: int) -> dict:
        """
        Bereken de geschatte kostprijs voor 1 uur op basis van huidig vermogen.

        Als het vermogen negatief is (teruglevering via zonnepanelen),
        wordt automatisch het injectietarief gebruikt.

        Parameters:
            power_w : huidig vermogen in Watt (positief = verbruik, negatief = injectie)
            tariff  : 1 = piek, 2 = dal

        Geeft terug:
            dict met verbruik, kostprijs en tarief info
        """
        # Zet Watt om naar kWh voor 1 uur: kWh = W / 1000
        kwh = abs(power_w) / 1000

        # Bepaal of het verbruik of teruglevering is
        is_injection = power_w < 0

        # Bereken de kostprijs
        cost = self.calculate_cost(kwh=kwh, tariff=tariff, injection=is_injection)

        # Bij injectie ontvang je geld (positief getal = winst)
        if is_injection:
            cost = cost  # je ontvangt dit bedrag
        else:
            cost = -cost  # je betaalt dit bedrag (negatief = uitgave)

        return {
            "power_w"       : power_w,
            "kwh_per_hour"  : round(kwh, 4),
            "tariff"        : tariff,
            "tariff_label"  : "piek" if tariff == 1 else "dal",
            "is_injection"  : is_injection,
            "price_per_kwh" : self._get_price_for_tariff(tariff, is_injection),
            "cost_eur"      : cost,   # negatief = betalen, positief = ontvangen
        }

    def calculate_daily_cost(self, peak_kwh: float, off_peak_kwh: float,
                              peak_injection_kwh: float = 0.0,
                              off_peak_injection_kwh: float = 0.0) -> dict:
        """
        Bereken de totale dagkostprijs op basis van piek- en dalverbruik.

        Parameters:
            peak_kwh              : verbruik tijdens piekuren (kWh)
            off_peak_kwh          : verbruik tijdens daluren (kWh)
            peak_injection_kwh    : teruglevering tijdens piekuren (kWh)
            off_peak_injection_kwh: teruglevering tijdens daluren (kWh)

        Geeft terug:
            dict met alle deelkosten en het totaal
        """
        # Kosten voor aankoop
        peak_cost     = self.calculate_cost(peak_kwh, tariff=1)
        off_peak_cost = self.calculate_cost(off_peak_kwh, tariff=2)

        # Opbrengst voor injectie (teruglevering zonnepanelen)
        peak_injection_revenue     = self.calculate_cost(peak_injection_kwh,     tariff=1, injection=True)
        off_peak_injection_revenue = self.calculate_cost(off_peak_injection_kwh, tariff=2, injection=True)

        # Totaal: kosten min opbrengsten
        total_cost    = peak_cost + off_peak_cost
        total_revenue = peak_injection_revenue + off_peak_injection_revenue
        net_cost      = round(total_cost - total_revenue, 4)

        return {
            "peak_kwh"                  : peak_kwh,
            "off_peak_kwh"              : off_peak_kwh,
            "peak_injection_kwh"        : peak_injection_kwh,
            "off_peak_injection_kwh"    : off_peak_injection_kwh,
            "peak_cost_eur"             : peak_cost,
            "off_peak_cost_eur"         : off_peak_cost,
            "total_purchase_eur"        : round(total_cost, 4),
            "peak_injection_revenue_eur"    : peak_injection_revenue,
            "off_peak_injection_revenue_eur": off_peak_injection_revenue,
            "total_revenue_eur"         : round(total_revenue, 4),
            "net_cost_eur"              : net_cost,  # negatief = je hebt geld verdiend!
        }

    def calculate_period_cost(self, daily_cost: float, days: int) -> dict:
        """
        Schaal een dagkostprijs op naar week, maand of jaar.

        Parameters:
            daily_cost : netto dagkostprijs in euro
            days       : aantal dagen in de periode

        Geeft terug:
            dict met kosten per week, maand en jaar
        """
        return {
            "daily_eur"   : round(daily_cost, 4),
            "weekly_eur"  : round(daily_cost * 7, 4),
            "monthly_eur" : round(daily_cost * 30, 4),
            "yearly_eur"  : round(daily_cost * 365, 4),
        }

    def get_summary(self, power_w: float, tariff: int) -> dict:
        """
        Geef een volledige samenvatting van de actuele kostprijssituatie.

        Dit is de hoofdmethode die het dashboard zal gebruiken.
        Combineert huidig vermogen met tariefinformatie.

        Parameters:
            power_w : huidig vermogen in Watt (van de meter)
            tariff  : actief tarief (van de meter of berekend)

        Geeft terug:
            dict met alle relevante kostprijsinformatie
        """
        hourly = self.calculate_hourly_cost(power_w=power_w, tariff=tariff)

        return {
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "current_tariff": "peak" if tariff == 1 else "off_peak",
            "peak_price": self.peak_price,
            "off_peak_price": self.off_peak_price,
            "injection_peak": self.injection_peak_price,
            "injection_off_peak": self.injection_off_peak_price,
            "current_power": hourly,
        }