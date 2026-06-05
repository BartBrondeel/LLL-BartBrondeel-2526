# Energie Dashboard - Eindwerk Python

**Student:** Bart Brondeel  
**Opleiding:** Graduaat Programmeren - Odisee  
**Schooljaar:** 2025-2026

## Beschrijving

Een webapplicatie gebouwd met Python en Flask die:
- Actuele energieprijzen per uur ophaalt via de ENTSO-E API
- Verbruiksdata uitleest van een digitale meter via HomeWizard P1
- Kostprijzen berekent per uur, dag, week, maand en jaar
- Alles visualiseert in een interactief dashboard met grafieken

## Status

In ontwikkeling - wordt stap voor stap uitgebouwd

| Sessie | Inhoud | Status |
|--------|--------|--------|
| 1 | Project setup - Flask Hello World | ✅ Klaar |
| 2 | Config klasse - OOP + python-dotenv | ✅ Klaar |
| 3 | HomeWizardMeter klasse | ✅ Klaar |
| 4 | PriceCalculator klasse | ✅ Klaar |
| 5 | DataManager klasse | ✅ Klaar |
| 6 | FluviusImporter klasse | ✅ Klaar |
| 7 | EntsoEApi klasse | ✅ Klaar |
| 8 | Frontend dashboard | ✅ Gepland |
| 9 | Uitbreidingen + Foutafhandeling + Logging | ✅ Klaar |
| 10 | Eindtest en documentatie | 🔲 Gepland |

## Technologieën

- Python 3.11
- Flask
- Pandas
- Requests
- Chart.js
- HomeWizard P1 API
- ENTSO-E Transparency API

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

6. Vul je eigen waarden in in .env (IP-adres meter, API-sleutel)

7. Start de applicatie
```
python app.py
```

8. Open je browser op http://localhost:5000

## Beschikbare pagina's

| URL | Beschrijving |
|-----|-------------|
| `/` | Startpagina |
| `/meter` | Actuele meterdata als JSON |
| `/meter/info` | Meterinformatie als JSON |
| `/energy/prices/today`   | DAY AHEAD prijzen vandaag  |
| `/energy/prices/tomorrow`| DAY AHEAD prijzen morgen   |
| `/energy/prices/current` | Actuele marktprijs         |
| `/energy/prices/week`    | Prijzen afgelopen week     |

## Projectstructuur

```
energie_dashboard/
|-- app.py                        <- Flask server en routes
|-- config.py                     <- Alle instellingen (OOP + DRY)
|-- meter.py                      <- HomeWizardMeter klasse (sessie 3)
|-- calculator.py                 <- PriceCalculator klasse (sessie 4)
|-- data_manager.py               <- DataManager klasse (sessie 5)
|-- fluvius_importer.py           <- FluviusImporter klasse (sessie 6)
|-- entsoe_api.py                 <- EntsoEApi klasse (sessie 7)
|-- requirements.txt              <- Benodigde bibliotheken
|-- .env                          <- Jouw geheimen (staat NIET op GitHub)
|-- .env.example                  <- Voorbeeld configuratie (geen echte waarden)
|-- .gitignore                    <- Bestanden die niet naar GitHub gaan
|-- README.md                     <- Deze documentatie
|-- templates/
|   └-- index.html                <- Dashboard HTML template (sessie 8)
|-- static/
|   |-- css/
|   |   └-- style.css             <- Dark/light thema stijl (sessie 8)
|   └-- js/
|       └-- dashboard.js          <- Dashboard JavaScript (sessie 8)
|-- data/
|   |-- measurements.csv          <- Live metingen (staat NIET op GitHub)
|   └-- historiek_elektriciteit.csv <- Fluvius export (staat NIET op GitHub)
```

## Auteur

Bart Brondeel - bart.brondeel@student.odisee.be