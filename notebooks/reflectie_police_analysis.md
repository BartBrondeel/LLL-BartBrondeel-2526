# Reflectie – Analyse van dodelijke politieschietincidenten in de VS

## Hoe heb ik het project aangepakt?

Dit project verschilde fundamenteel van de vorige analyses omdat het gaat over
een uiterst gevoelig en politiek beladen onderwerp. Dat beïnvloedde meteen
mijn aanpak: ik begon niet met coderen, maar met nadenken over hoe je dit
onderwerp op een eerlijke, methodologisch verantwoorde manier kunt aanpakken.

Mijn stap-voor-stap aanpak:

1. **Databronnen identificeren** — de Washington Post-database, aangevuld met
   US Census-data over inkomen, armoede, opleiding en raciale samenstelling.
2. **Onderzoeksvragen formuleren** vóórdat ik ook maar één grafiek bouwde —
   anders loop je het risico om data te zoeken die een conclusie bevestigt
   die je al had (confirmation bias).
3. **Data laden, inspecteren en opschonen** — missing values controleren,
   datatypes corrigeren, afgeleide kolommen aanmaken (jaar, maand, raciale labels).
4. **Visualisaties bouwen** die verschillende perspectieven tonen: niet alleen
   absolute aantallen maar ook verhoudingen t.o.v. de bevolking.
5. **Methodologische kanttekeningen toevoegen** — dit was bewust een aparte
   stap, niet een bijgedachte.

---

## Wat was makkelijk?

- **Pandas en Matplotlib** voelden na de vorige projecten vertrouwd aan.
  Groeperen, samenvoegen en aggregeren ging vlot.
- **Disproportionaliteitsratio's berekenen** was technisch eenvoudig:
  deel het aandeel slachtoffers door het bevolkingsaandeel — maar de
  interpretatie is complexer dan de berekening.
- **Heatmaps met Seaborn** voor de maand × jaar combinatie waren snel gebouwd
  en gaven meteen een duidelijk seizoenspatroon.

---

## Wat was moeilijk?

- **De methodologische valkuilen** zijn hier groter dan bij andere datasets.
  Het is verleidelijk om een correlatie (armoede ↔ incidenten) te presenteren
  als een oorzaak. Ras en armoede zijn sterk gecorreleerd in de VS-data —
  je kunt ze niet zomaar onafhankelijk van elkaar analyseren zonder
  multivariabele regressie.
- **Registratiebias**: de WaPo-database is de meest volledige die bestaat,
  maar registreert niet alle incidenten. Dat maakt vergelijkingen tussen
  staten moeilijker dan ze lijken.
- **De juiste visualisatie kiezen**: een absolute staaf voor ras ziet er
  anders uit dan een disproportionaliteitsratio. Beide zijn "correct" maar
  geven een heel ander beeld — welke je kiest, beïnvloedt de boodschap.
  Ik heb ervoor gekozen om beide te tonen.
- **Databeschikbaarheid**: de originele WaPo-database en Census-bestanden
  waren niet downloadbaar via script (HTTP 403). Ik heb een representatieve
  synthetische dataset gebruikt gebaseerd op gepubliceerde statistieken —
  voor een echte beleidsanalyse is de originele data onmisbaar.

---

## Hoe zou ik het bij een volgend project verbeteren?

- **Multivariabele regressie toepassen** om te controleren voor confounding
  variabelen. De vraag "is ras X significant, ook na controle voor armoede?"
  kan alleen met regressie beantwoord worden, niet met bivariabele grafieken.
- **Per capita normaliseren van bij het begin** — absolute aantallen per staat
  zijn misleidend zonder bevolkingscorrectie. Ik heb dit gedaan in de staats-
  grafiek, maar het had door de hele analyse een standaard moeten zijn.
- **Peer review inbouwen**: bij gevoelige onderwerpen is het waardevol om
  je analyses en conclusies te laten controleren door iemand anders voordat
  je ze publiceert.

---

## Mijn belangrijkste leerpunt van vandaag

Het belangrijkste inzicht was het verschil tussen **beschrijvende statistiek**
en **causale inferentie**. Data-analyse kan patronen beschrijven — "Zwarte
Amerikanen zijn 2x oververtegenwoordigd als slachtoffer" — maar kan zelden
alleen op basis van de ruwe data verklaren *waarom* dat zo is.

De verklaring vereist aanvullend onderzoek, contextuele kennis, en vaak
methoden uit de sociale wetenschappen die verder gaan dan pandas en matplotlib.
Dit is een les die ik bij elke dataset wil onthouden: de grafiek is het begin
van het gesprek, niet het einde.

---

## Wat zou ik anders doen?

- **De originele data handmatig downloaden** van washingtonpost.com/graphics/
  investigations/police-shootings-database/ om met werkelijke, niet-gesimuleerde
  data te werken.
- **Meer Census-variabelen opnemen**: werkloosheidsgraad, bevolkingsdichtheid,
  politie-budget per hoofd van de bevolking — die geven een vollediger beeld.
- **Interactieve Plotly-kaarten** bouwen per staat en stad zodat de lezer
  zelf kan filteren op jaar, ras of andere variabelen — dat is transparanter
  dan statische grafieken.
- **Een duidelijkere scheidingslijn** trekken tussen "wat de data laat zien"
  en "wat de data niet kan laten zien" — en dat prominent vermelden,
  niet als voetnoot maar als inleiding.
