import os
import time
import requests

from datetime import datetime
from dotenv import load_dotenv
from send_email import send_email
from langchain.chat_models import init_chat_model

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
API_KEY = os.getenv("API_KEY")

# Current date
today = datetime.now().strftime("%d-%m-%Y")

# News API URL
url = (
    "https://newsapi.org/v2/top-headlines?"
    "country=us&"
    "category=business&"
    "pageSize=8&"
    "apiKey=" + API_KEY
)

try:
    # Request news
    request = requests.get(url, timeout=10)

    # Check HTTP errors
    request.raise_for_status()

    # Convert response to dictionary
    content = request.json()

    print(content)

    # Get articles
    articles = content.get("articles", [])

    # Stop if no articles found
    if not articles:
        print("Geen nieuwsartikels gevonden.")
        exit()

    # Build cleaner text for AI
    articles_text = ""

    for article in articles:
        title = article.get("title", "Geen titel")
        description = article.get("description", "")

        # Limit description length
        if description:
            description = description[:200]

        articles_text += f"""
Titel: {title}
Beschrijving: {description}

"""

    # Initialize Gemini model
    model = init_chat_model(
        model="gemini-2.5-flash",
        model_provider="google-genai",
        api_key=GOOGLE_API_KEY
    )

    # Prompt
    prompt = f"""
You are a professional financial news analyst.

Summarize the most important business news in 1 short paragraph.

Then write a second paragraph explaining the possible impact on:
- stock markets
- AI companies
- tech sector
- investors

Articles:
{articles_text}
"""

    # Retry mechanism
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = model.invoke(prompt)
            break

        except Exception as e:
            print(f"AI fout: {e}")

            if attempt < max_retries - 1:
                print("30 seconden wachten...")
                time.sleep(30)
            else:
                raise

    # Convert AI response
    response_str = response.content

    # Build email
    body = f"Subject: News Summary {today}\n\n"
    body += response_str

    # Encode email
    body = body.encode("utf-8")

    # Send email
    send_email(message=body)

    print("Email succesvol verzonden.")

except requests.exceptions.RequestException as e:
    print(f"News API fout: {e}")

except Exception as e:
    print(f"Algemene fout: {e}")