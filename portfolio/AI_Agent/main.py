"""
=============================================================
  ai_agent.py — AI Chatbot met geheugen en zoekfunctie
  Student:   Bart Brondeel
  Opleiding: Graduaat Programmeren - Odisee

  Wat doet dit programma?
  -----------------------
  Een chatbot die:
    - Vragen beantwoordt via een lokaal taalmodel (Qwen via Ollama)
    - Actuele info opzoekt via Tavily (webbrowser voor de AI)
    - De huidige datum kan opvragen
    - Gesprekken onthoudt via een SQLite database
    - Een webinterface toont via Gradio

  Gebruikte bibliotheken:
  -----------------------
  | Bibliotheek            | Waarvoor                                     |
  |------------------------|----------------------------------------------|
  | os                     | Omgevingsvariabelen lezen (.env)             |
  | sqlite3                | Lokale database voor geheugen                |
  | uuid                   | Unieke ID aanmaken per gesprek               |
  | datetime               | Huidige datum ophalen                        |
  | gradio                 | Webinterface voor de chatbot                 |
  | dotenv                 | .env bestand inladen (API-sleutels)          |
  | langgraph              | AI-agent bouwen met tools en geheugen        |
  | langchain_community    | Tavily zoektool integreren                   |
  | langchain_ollama       | Lokaal taalmodel (Qwen) aansturen            |

  Gebruikte methodes:
  -------------------
  | Methode / Functie      | Wat het doet                                 |
  |------------------------|----------------------------------------------|
  | load_dotenv()          | Laadt API-sleutels uit .env bestand          |
  | os.getenv()            | Leest een specifieke omgevingsvariabele      |
  | datetime.now()         | Geeft huidige datum en tijd terug            |
  | strftime()             | Formatteert datum naar leesbare string       |
  | sqlite3.connect()      | Opent of maakt een SQLite database           |
  | SqliteSaver()          | Slaat gespreksgeschiedenis op in database    |
  | ChatOllama()           | Verbindt met lokaal Ollama taalmodel         |
  | TavilySearchResults()  | Zoekt actuele info op het web                |
  | create_react_agent()   | Bouwt de AI-agent met tools en model         |
  | agent.invoke()         | Stuurt een bericht naar de agent             |
  | uuid.uuid4()           | Genereert een unieke gespreks-ID             |
  | gr.Blocks()            | Bouwt de Gradio webinterface op              |
  | gr.ChatInterface()     | Toont het chatvenster in de browser          |
  | demo.launch()          | Start de webserver voor de interface         |
=============================================================
"""

# --- Standaard Python bibliotheken ---
import os           # Lees omgevingsvariabelen (API-sleutels)
import sqlite3      # Lokale database voor gespreksgeheugen
import uuid         # Unieke ID per gesprek genereren
from datetime import datetime  # Datum en tijd ophalen

# --- Externe bibliotheken ---
import gradio as gr  # Webinterface bouwen (chatvenster in browser)
from dotenv import load_dotenv  # Laad .env bestand in

# --- LangChain / LangGraph bibliotheken ---
from langgraph.prebuilt import create_react_agent       # AI-agent bouwen
from langchain_community.tools.tavily_search import TavilySearchResults  # Zoektool
from langchain_ollama import ChatOllama                 # Lokaal taalmodel
from langgraph.checkpoint.sqlite import SqliteSaver     # Geheugen opslaan in database

# =====================
#  Configuratie laden
# =====================
# Laad de .env file zodat API-sleutels beschikbaar zijn via os.getenv()
load_dotenv()

# =====================
#  Tool: datum ophalen
# =====================
def get_date() -> str:
    """
    Geeft de huidige datum terug als tekst.

    De agent roept deze tool aan als de gebruiker vraagt
    naar de datum van vandaag. Zo hoeft het taalmodel
    de datum niet zelf te "raden" (modellen kennen hun
    trainingsdatum, niet de echte huidige datum).

    Geeft terug:
        str: datum in het formaat JJJJ-MM-DD (bv. "2026-05-29")
    """
    return datetime.now().strftime("%Y-%m-%d")


# =====================
#  Zoektool instellen
# =====================
# Tavily is een zoekmachine speciaal voor AI-agents.
# Ze geeft korte, bruikbare antwoorden terug i.p.v. een volledige webpagina.
tavily_api_key = os.getenv("TAVILY_API_KEY")

search_tool = TavilySearchResults(
    tavily_api_key=tavily_api_key
)

# =====================
#  Geheugen (database)
# =====================
# SQLite is een eenvoudige lokale database (één bestand op schijf).
# check_same_thread=False is nodig omdat Gradio meerdere threads gebruikt.
conn = sqlite3.connect("chatbot_memory.db", check_same_thread=False)

# SqliteSaver slaat de gespreksgeschiedenis op per thread_id.
# Zo onthoudt de chatbot wat eerder gezegd werd in hetzelfde gesprek.
checkpoint = SqliteSaver(conn)

# =====================
#  Taalmodel instellen
# =====================
# ChatOllama gebruikt een lokaal geïnstalleerd model via Ollama.
# Qwen2.5:7b is een sterk compact model dat goed werkt op een gewone PC.
# Geen API-sleutel nodig — het draait volledig lokaal!
llm = ChatOllama(model="qwen2.5:7b")

# =====================
#  Systeemprompt
# =====================
# Dit zijn de instructies die de agent altijd meekrijgt.
# Het bepaalt het gedrag van de chatbot.
SYSTEM_PROMPT = """
<<<<<<< HEAD
You are a helpful assistant.
Answer all user's queries.
ONLY use the get_date tool if the user is explicitly asking about today's date.
Use the search tool for answering questions that require up-to-date information.
=======
You are a helpful and concise assistant.

## Tool usage rules
- Use the get_date tool ONLY when the user explicitly asks what today's date is.
- Use the search tool when the question requires recent or real-time information
  (news, prices, current events, sports results, weather, etc.).
- Do NOT search for things you already know (definitions, history, general knowledge).
- Never make up information — if you are unsure, search first.

## Answer rules
- Answer in the same language the user is writing in.
- Keep answers clear and to the point.
- If you used the search tool, briefly mention where the information comes from.
- If you cannot find a reliable answer, say so honestly.
>>>>>>> d54a119 (werkende code AI Agent voorzien van commentaar)
"""

# =====================
#  Agent aanmaken
# =====================
# create_react_agent bouwt een AI-agent die zelf beslist welke tool te gebruiken.
# ReAct = Reason + Act: de agent denkt na, kiest een tool, gebruikt die, denkt opnieuw.
agent = create_react_agent(
    llm,
    tools=[get_date, search_tool],  # Beschikbare tools voor de agent
    checkpointer=checkpoint,         # Geheugen: slaat gesprek op in database
    state_modifier=SYSTEM_PROMPT,            # Gedragsinstructies voor de agent
)

# =====================
#  Chatfunctie
# =====================
def chat(message: str, history: list, thread_id: str) -> str:
    """
    Verwerkt een gebruikersbericht en geeft een antwoord terug.

    Deze functie wordt aangeroepen door Gradio bij elk nieuw bericht.
    De thread_id zorgt ervoor dat de agent het gesprek onthoudt.

    Parameters:
        message   (str):  Het nieuwe bericht van de gebruiker
        history   (list): Vorige berichten (beheerd door Gradio zelf)
        thread_id (str):  Unieke ID voor dit gesprek (voor het geheugen)

    Geeft terug:
        str: Het antwoord van de agent als tekst
    """
    # config vertelt de agent welk gesprek dit is (via thread_id)
    config = {"configurable": {"thread_id": thread_id}}

    # Stuur het bericht naar de agent
    response = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config
    )

    # Het laatste bericht in de lijst is het antwoord van de agent
    return response["messages"][-1].content


# =====================
#  Webinterface (Gradio)
# =====================
with gr.Blocks() as demo:
    # Titel bovenaan de pagina
    gr.Markdown("# AI Dot11 Chatbot")

    # thread_id is een unieke code per browservenster/sessie.
    # uuid4() genereert een willekeurige unieke ID.
    # lambda zorgt ervoor dat elke nieuwe sessie een NIEUWE ID krijgt.
    thread_id = gr.State(value=lambda: str(uuid.uuid4()))

    # ChatInterface toont het chatvenster en roept automatisch chat() aan
    # additional_inputs geeft thread_id mee aan de chat() functie
    gr.ChatInterface(fn=chat, additional_inputs=[thread_id])

# =====================
#  App opstarten
# =====================
# demo.launch() start een lokale webserver.
# Open je browser op http://localhost:7860
if __name__ == "__main__":
    demo.launch()