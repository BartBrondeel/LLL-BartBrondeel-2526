import requests
from send_email import send_email

topic = "tesla"

API_KEY = "0c9a81aaf9624e4fa91b06c7c4a188a3"
url = f"https://newsapi.org/v2/everything?q={topic}&from=2026-04-28&sortBy=publishedAt&apiKey=0c9a81aaf9624e4fa91b06c7c4a188a3&language=nl"

# Make a request
request = requests.get(url)

# Get a dictionary with data
content = request.json()

# Acces the article titles and description
body = ""
for article in content["articles"][0:20]:
    title = article["title"] or ""
    description = article["description"] or ""
    link = article["url"] or ""
    body = body + title + "\n" + description + "\n" + link + 2*"\n"

body = "subject: Het nieuws voor vandaag\n\n" + body

body = body.encode("utf-8")
send_email(message=body)
