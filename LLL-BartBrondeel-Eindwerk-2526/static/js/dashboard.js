/*
 * dashboard.js — Energie Dashboard JavaScript
 * Haalt data op van de Flask API en toont die in de pagina.
 *
 * Structuur:
 * 1. Thema schakelaar (dark/light)
 * 2. Live meterdata ophalen en tonen
 * 3. ENTSO-E energieprijzen ophalen en tonen
 * 4. Prijsgrafiek bouwen met Chart.js
 * 5. Historiek ophalen en tonen
 * 6. Automatisch verversen
 */

// =====================================================
//  1. THEMA SCHAKELAAR
// =====================================================

const themeToggle = document.getElementById("themeToggle");
const body        = document.body;

// Laad het opgeslagen thema uit localStorage (onthoudt de keuze)
const savedTheme = localStorage.getItem("theme") || "dark";
applyTheme(savedTheme);

// Luister naar klikken op de schakelaar
themeToggle.addEventListener("change", () => {
    const newTheme = themeToggle.checked ? "light" : "dark";
    applyTheme(newTheme);
    localStorage.setItem("theme", newTheme);  // Onthoud de keuze
});

function applyTheme(theme) {
    // Verwijder beide klassen en voeg de juiste toe
    body.classList.remove("dark-theme", "light-theme");
    body.classList.add(theme + "-theme");

    // Zet de schakelaar in de juiste stand
    themeToggle.checked = (theme === "light");

    // Pas ook de grafiek aan als die al bestaat
    if (window.priceChart) {
        updateChartTheme();
    }
}


// =====================================================
//  2. LIVE METERDATA
// =====================================================

async function loadMeterData() {
    try {
        // Haal data op van onze Flask API
        const response = await fetch("/meter");
        const data     = await response.json();

        // Haal ook de actuele marktprijs op
        const priceResponse = await fetch("/energy/prices/current");
        const priceData     = await priceResponse.json();

        document.getElementById("current-market-price").textContent =
            priceData.price_eur_kwh ? priceData.price_eur_kwh.toFixed(4) : "--";
        document.getElementById("price-time").textContent =
            priceData.timestamp || "--";

        // Vermogen — met kleur op basis van positief/negatief
        const powerEl = document.getElementById("current-power");
        powerEl.textContent = data.current_power_w;
        powerEl.className   = "card-value " +
            (data.current_power_w >= 0 ? "value-positive" : "value-negative");

        // Status tekst onder het vermogen
        document.getElementById("power-status").textContent =
            data.current_power_w >= 0 ? "Verbruik van net" : "Injectie naar net ☀️";

        // Tarief
        document.getElementById("current-tariff").textContent =
            data.active_tariff === 1 ? "Piek" : "Dal";
        document.getElementById("tariff-time").textContent =
            data.active_tariff === 1
                ? "Weekdag 07:00 - 22:00"
                : "Nacht / Weekend";

        // Totalen
        document.getElementById("total-consumption").textContent =
            data.total_consumption_kwh.toFixed(1);
        document.getElementById("total-injection").textContent =
            data.total_injection_kwh.toFixed(1);
        document.getElementById("total-gas").textContent =
            data.total_gas_m3.toFixed(1);

        // Fases
        document.getElementById("phase1").textContent = data.power_phase1_w;
        document.getElementById("phase2").textContent = data.power_phase2_w;
        document.getElementById("phase3").textContent = data.power_phase3_w;

        // Kleur per fase — positief = verbruik, negatief = injectie
        ["phase1", "phase2", "phase3"].forEach((id, i) => {
            const val = [data.power_phase1_w, data.power_phase2_w, data.power_phase3_w][i];
            document.getElementById(id).className =
                "card-value " + (val >= 0 ? "value-positive" : "value-negative");
        });

        // Tijdstip + simulatiebadge
        document.getElementById("last-update-time").textContent = data.timestamp;
        document.getElementById("simulation-badge").style.display =
            data.is_simulation ? "inline" : "none";

    } catch (error) {
        console.error("Fout bij laden meterdata:", error);
    }
}


// =====================================================
//  3. ENERGIEPRIJZEN
// =====================================================

async function loadPrices() {
    try {
        const response = await fetch("/energy/prices/today");
        const data     = await response.json();

        // Statistieken
        document.getElementById("price-min").textContent =
            data.stats.min_eur_kwh.toFixed(4);
        document.getElementById("price-avg").textContent =
            data.stats.avg_eur_kwh.toFixed(4);
        document.getElementById("price-max").textContent =
            data.stats.max_eur_kwh.toFixed(4);

        // Bouw de grafiek
        buildPriceChart(data.prices);

    } catch (error) {
        console.error("Fout bij laden prijzen:", error);
    }
}


// =====================================================
//  4. PRIJSGRAFIEK (Chart.js)
// =====================================================

window.priceChart = null;   // Globale referentie naar de grafiek

function buildPriceChart(prices) {
    const ctx = document.getElementById("priceChart").getContext("2d");

    // Labels = tijdstippen, data = prijzen per kWh
    const labels = prices.map(p => p.timestamp.split(" ")[1]);  // Enkel het uur
    const values = prices.map(p => p.price_eur_kwh);

    // Bepaal kleuren op basis van huidig thema
    const isDark      = body.classList.contains("dark-theme");
    const gridColor   = isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.05)";
    const textColor   = isDark ? "#94a3b8" : "#64748b";
    const lineColor   = isDark ? "#38bdf8" : "#0284c7";
    const fillColor   = isDark ? "rgba(56,189,248,0.15)" : "rgba(2,132,199,0.1)";

    // Verwijder bestaande grafiek als die er al is (DRY)
    if (window.priceChart) {
        window.priceChart.destroy();
    }

    window.priceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label       : "Prijs (EUR/kWh)",
                data        : values,
                borderColor : lineColor,
                backgroundColor: fillColor,
                borderWidth : 2,
                fill        : true,
                tension     : 0.3,     // Vloeiende lijn
                pointRadius : 2,
            }]
        },
        options: {
            responsive : true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: textColor }
                },
                tooltip: {
                    callbacks: {
                        // Toon prijs met 4 decimalen in tooltip
                        label: (ctx) => ` €${ctx.parsed.y.toFixed(4)}/kWh`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: textColor,
                        maxTicksLimit: 12   // Toon max 12 labels op X-as
                    },
                    grid: { color: gridColor }
                },
                y: {
                    ticks: {
                        color: textColor,
                        callback: (val) => `€${val.toFixed(3)}`
                    },
                    grid: { color: gridColor }
                }
            }
        }
    });
}

function updateChartTheme() {
    // Herlaad de prijzen zodat de grafiek opnieuw wordt gebouwd met het nieuwe thema
    loadPrices();
}


// =====================================================
//  5. HISTORIEK
// =====================================================

// Bijhouden welke periode actief is
let activePeriod = "today";

async function loadHistory(period = "today") {
    activePeriod = period;

    // Juiste API route kiezen op basis van periode
    const routes = {
        today: "/history/today",
        week : "/history/week",
        month: "/history/month"
    };

    try {
        const response = await fetch(routes[period]);
        const data     = await response.json();

        if (data.error) {
            // Nog niet genoeg metingen
            document.getElementById("hist-peak-kwh").textContent   = "--";
            document.getElementById("hist-offpeak-kwh").textContent = "--";
            document.getElementById("hist-net-cost").textContent    = "--";
            return;
        }

        document.getElementById("hist-peak-kwh").textContent =
            data.consumption_peak_kwh.toFixed(3);
        document.getElementById("hist-offpeak-kwh").textContent =
            data.consumption_off_peak_kwh.toFixed(3);
        document.getElementById("hist-net-cost").textContent =
            "€" + data.costs.net_cost_eur.toFixed(2);

    } catch (error) {
        console.error("Fout bij laden historiek:", error);
    }
}

// Periode knoppen — klik event
document.querySelectorAll(".period-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        // Verwijder 'active' van alle knoppen
        document.querySelectorAll(".period-btn").forEach(b =>
            b.classList.remove("active"));

        // Voeg 'active' toe aan de geklikte knop
        btn.classList.add("active");

        // Laad de historiek voor de geselecteerde periode
        loadHistory(btn.dataset.period);
    });
});


// =====================================================
//  6. AUTOMATISCH VERVERSEN
// =====================================================

// Laad alles bij het opstarten van de pagina
loadMeterData();
loadPrices();
loadHistory("today");

// Ververs meterdata elke 30 seconden
setInterval(loadMeterData, 30000);

// Ververs prijzen elke 5 minuten (prijzen veranderen niet snel)
setInterval(loadPrices, 300000);