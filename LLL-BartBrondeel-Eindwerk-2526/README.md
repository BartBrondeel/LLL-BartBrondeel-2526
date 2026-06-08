# Energie Dashboard - Eindwerk Python

**Student:** Bart Brondeel  
**Opleiding:** Graduaat Programmeren - Odisee  
**Schooljaar:** 2025-2026  
**Deadline:** 12 juni 2026

## Beschrijving

Een webapplicatie gebouwd met Python en Flask die:
- Actuele meterdata uitleest van een HomeWizard P1 slimme meter via lokale WiFi API
- DAY AHEAD energieprijzen per uur ophaalt via de ENTSO-E Transparency API
- Kostprijzen berekent op basis van de Belgische tariefstructuur (piek/dal + injectie)
- Historische Fluvius verbruiksdata importeert en verwerkt (17 maanden)
- Verbruik en kostprijzen toont per dag, week, maand en jaar
- Alles visualiseert in een interactief dashboard met dark/light thema en grafieken

## Gebruikte OOP klassen

| Klasse | Bestand | Verantwoordelijkheid |
|--------|---------|---------------------|
| `Config` | config.py | Alle instellingen en tarieven (DRY principe) |
| `HomeWizardMeter` | meter.py | Live meterdata ophalen via lokale API |
| `PriceCalculator` | calculator.py | Kostprijsberekeningen piek/dal/injectie |
| `DataManager` | data_manager.py | Metingen opslaan en ophalen uit CSV |
| `FluviusImporter` | fluvius_importer.py | Historische Fluvius CSV importeren |
| `EntsoEApi` | entsoe_api.py | DAY AHEAD prijzen via ENTSO-E API |

## Status

Project volledig afgerond ✅

| Sessie | Inhoud | Status |
|--------|--------|--------|
| 1 | Project setup - Flask Hello World | ✅ Klaar |
| 2 | Config klasse - OOP + python-dotenv | ✅ Klaar |
| 3 | HomeWizardMeter klasse | ✅ Klaar |
| 4 | PriceCalculator klasse | ✅ Klaar |
| 5 | DataManager klasse | ✅ Klaar |
| 6 | FluviusImporter klasse | ✅ Klaar |
| 7 | EntsoEApi klasse | ✅ Klaar |
| 8 | Frontend dashboard | ✅ Klaar |
| 9 | Uitbreidingen + Foutafhandeling + Logging | ✅ Klaar |
| 10 | Eindtest en documentatie | ✅ Klaar |

## Technologieën

- Python 3.11
- Flask 3.0
- Pandas
- Requests
- APScheduler
- entsoe-py
- Chart.js
- HomeWizard P1 API (lokale WiFi)
- ENTSO-E Transparency Platform API

## Installatie

1. Clone dit project

2. Maak een virtuele omgeving aan
```
python -m venv .venv
```

3. Activeer de virtuele omgeving
```
.venv\Scripts\activate
```

4. Installeer de bibliotheken
```
pip install -r requirements.txt
```

5. Maak je .env bestand aan op basis van .env.example
```
cp .env.example .env
```

6. Vul je eigen waarden in .env (IP-adres meter, ENTSO-E API-sleutel, EAN-code)

7. Start de applicatie
```
python app.py
```

8. Open je browser op http://localhost:5000

## Beschikbare routes

| URL | Beschrijving |
|-----|-------------|
| `/` | Dashboard hoofdpagina |
| `/meter` | Live meterdata (JSON) |
| `/meter/info` | Meterinformatie (JSON) |
| `/prices` | Actuele kostprijs op basis van live vermogen (JSON) |
| `/energy/prices/today` | DAY AHEAD prijzen vandaag (JSON) |
| `/energy/prices/tomorrow` | DAY AHEAD prijzen morgen (JSON) |
| `/energy/prices/current` | Actuele marktprijs dit uur (JSON) |
| `/energy/prices/week` | Marktprijzen afgelopen week (JSON) |
| `/history/today` | Verbruik en kostprijs vandaag (JSON) |
| `/history/week` | Verbruik en kostprijs afgelopen week (JSON) |
| `/history/month` | Verbruik en kostprijs afgelopen maand (JSON) |
| `/history/year` | Verbruik en kostprijs afgelopen jaar (JSON) |
| `/fluvius/preview` | Fluvius bestand controleren zonder importeren (JSON) |
| `/fluvius/import` | Fluvius historische data importeren (JSON) |

## Projectstructuur

```
energie_dashboard/
|-- app.py                           <- Flask server, routes en APScheduler
|-- config.py                        <- Alle instellingen (OOP + DRY)
|-- meter.py                         <- HomeWizardMeter klasse
|-- calculator.py                    <- PriceCalculator klasse
|-- data_manager.py                  <- DataManager klasse
|-- fluvius_importer.py              <- FluviusImporter klasse
|-- entsoe_api.py                    <- EntsoEApi klasse
|-- requirements.txt                 <- Benodigde bibliotheken
|-- .env                             <- Geheimen (staat NIET op GitHub)
|-- .env.example                     <- Voorbeeld configuratie (geen echte waarden)
|-- .gitignore                       <- Bestanden die niet naar GitHub gaan
|-- README.md                        <- Deze documentatie
|-- templates/
|   └-- index.html                   <- Dashboard HTML template
|-- static/
|   |-- css/
|   |   └-- style.css                <- Dark/light thema stijl
|   └-- js/
|       └-- dashboard.js             <- Dashboard JavaScript + Chart.js
|-- data/
|   |-- measurements.csv             <- Opgeslagen metingen (staat NIET op GitHub)
|   |-- historiek_elektriciteit.csv  <- Fluvius export (staat NIET op GitHub)
|   └-- dashboard.log                <- Logging (staat NIET op GitHub)
```

## Databronnen

| Bron | Type | Gebruik |
|------|------|---------|
| HomeWizard P1 meter | Lokale WiFi API | Live vermogen, fase data, gas |
| ENTSO-E Transparency Platform | REST API | DAY AHEAD uurprijzen België |
| Fluvius (Mijn Fluvius) | CSV export | Historische kwartierdata |

## Auteur

Bart Brondeel - bart.brondeel@student.odisee.be