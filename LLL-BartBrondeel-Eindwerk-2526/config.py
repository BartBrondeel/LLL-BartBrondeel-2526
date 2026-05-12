"""
=============================================================
  config.py — Configuratie voor het Energie Dashboard
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee
  Sessie:    2 — Config klasse + python-dotenv integratie

  OOP principe: alle instellingen zitten in 1 klasse
  DRY principe: verander een waarde hier, werkt overal
=============================================================
"""

# --- Standaard bibliotheken ---
import os

# --- Externe bibliotheken ---
from dotenv import load_dotenv  # pip install python-dotenv

# Laad de .env file in
# .env bevat geheimen (API-sleutel, IP-adres) die NIET op GitHub mogen
# .env staat in .gitignore — .env.example staat WEL op GitHub als voorbeeld
load_dotenv()


class Config:
    """
    Centrale configuratieklasse voor het Energie Dashboard.

    Waarom een klasse?
    ------------------
    OOP (Object Oriented Programming) principe:
    Alle instellingen zitten op 1 centrale plaats.
    Als je bv. je IP-adres wil wijzigen, doe je dat
    hier en nergens anders in het project.

    DRY (Don't Repeat Yourself) principe:
    Zonder deze klasse zou je HOMEWIZARD_IP op 5 plaatsen
    moeten typen. Als het dan verandert, moet je het ook
    op 5 plaatsen aanpassen — met kans op fouten.
    Met Config.HOMEWIZARD_IP verander je het 1 keer.

    Gebruik:
    --------
    from config import Config

    print(Config.HOMEWIZARD_IP)
    print(Config.PRIJS_PIEK_PER_KWH)
    """

    # =====================
    #  HomeWizard P1 meter
    # =====================
    # os.getenv() leest de waarde uit je .env bestand
    HOMEWIZARD_IP: str = os.getenv("HOMEWIZARD_IP")

    # =====================
    #  ENTSO-E API
    # =====================
    ENTSOE_API_KEY: str = os.getenv("ENTSOE_API_KEY")

    # EAN-code van je digitale meter (staat op je elektriciteitsfactuur)
    EAN_CODE: str = os.getenv("EAN_CODE")

    # =====================
    #  Luminus tarieven (tweevoudige meter - sociaal tarief april-juni 2026)
    #  Bron: tariefkaart ESTC2.0
    # =====================

    # Energieprijs (incl. BTW 0% voor sociaal tarief)
    PRIJS_PIEK_ENERGIE_PER_KWH: float = 0.2547   # 25,47 c€/kWh
    PRIJS_DAL_ENERGIE_PER_KWH:  float = 0.2426   # 24,26 c€/kWh

    # Bijzondere accijns (zelfde voor piek en dal)
    BIJZONDERE_ACCIJNS_PER_KWH: float = 0.025037  # 2,5037 c€/kWh

    # Totaalprijs per kWh (energie + accijns)
    PRIJS_PIEK_PER_KWH: float = round(0.2547 + 0.025037, 4)  # = €0,2797
    PRIJS_DAL_PER_KWH:  float = round(0.2426 + 0.025037, 4)  # = €0,2676

    # Injectietarieven (excl. BTW — BTW is 0% op injectie)
    INJECTIE_PIEK_PER_KWH: float = 0.0602   # 6,02 c€/kWh piekuren
    INJECTIE_DAL_PER_KWH:  float = 0.0238   # 2,38 c€/kWh daluren

    # Gemiddelde toeslag (25% piek, 75% dal)
    VASTE_TOESLAG_PER_KWH: float = round(
        0.25 * 0.2797 + 0.75 * 0.2676, 4
    )  # = €0,2706

    # =====================
    #  Flask instellingen
    # =====================
    # debug=True: server herstart automatisch bij code-wijzigingen
    # Zet op False wanneer het project klaar is voor productie
    DEBUG: bool = os.getenv("FLASK_DEBUG", "True") == "True"
    PORT:  int  = int(os.getenv("FLASK_PORT", "5000"))
