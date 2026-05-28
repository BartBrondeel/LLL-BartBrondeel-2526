import smtplib, ssl


def send_email(message):
    host = "smtp.gmail.com"
    port = 465

    username = "brondeel.b@gmail.com"
    password = "ihibiwqydcqpxkgb"

    reciever = "b.brondeel@telenet.be"
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, reciever, message)