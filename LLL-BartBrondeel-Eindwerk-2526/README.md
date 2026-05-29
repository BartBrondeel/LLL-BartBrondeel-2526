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
| 4 | PrijsBerekening klasse | ✅ Gepland |
| 5 | DataManager klasse | ✅ Gepland |
| 6 | EntsoEApi klasse | 🔲 Gepland |
| 7 | Flask routes refactoren | 🔲 Gepland |
| 8 | Frontend dashboard | 🔲 Gepland |
| 9 | Foutafhandeling en logging | 🔲 Gepland |
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

## Projectstructuur

```
energie_dashboard/
|-- data/
|   └── measurements.csv <- Opgeslagen metingen (niet op GitHub)
|-- app.py               <- Flask server en routes
|-- calculator.py        <- PriceCalculator klasse (sessie 4)
|-- config.py            <- Alle instellingen (OOP + DRY)
|-- data_manager.py      <- DataManager klasse (sessie 5)
|-- meter.py             <- HomeWizardMeter klasse (sessie 3)
|-- requirements.txt     <- Benodigde bibliotheken
|-- .env                 <- Jouw geheimen (staat NIET op GitHub)
|-- .env.example         <- Voorbeeld configuratie (geen echte waarden)
|-- .gitignore           <- Bestanden die niet naar GitHub gaan
|-- README.md            <- Deze documentatie
```

## Auteur

Bart Brondeel - bart.brondeel@student.odisee.be