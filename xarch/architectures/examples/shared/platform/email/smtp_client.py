import smtplib

# knows SMTP and no module: a module's adapter turns its own words into this call
class SmtpClient:
    def __init__(self, host: str, sender: str): self._host, self._sender = host, sender

    def send(self, to: str, subject: str, body: str) -> None:
        with smtplib.SMTP(self._host) as smtp:
            smtp.sendmail(self._sender, to, f"Subject: {subject}\n\n{body}")
