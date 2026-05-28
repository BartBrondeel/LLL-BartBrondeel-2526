import smtplib
import ssl
import os

from dotenv import load_dotenv

load_dotenv()


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = "brondeel.b@gmail.com"
    password = os.getenv("GMAIL_APP_PASSWORD")

    receiver = "b.brondeel@telenet.be"

    context = ssl.create_default_context()

    print("Verbinden met Gmail...")

    try:
        with smtplib.SMTP_SSL(host, port, context=context) as server:

            print("Inloggen...")
            server.login(username, password)

            print("Email verzenden...")
            server.sendmail(username, receiver, message)

            print("Email succesvol verzonden!")

    except Exception as e:
        print(f"Email fout: {e}")