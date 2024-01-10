import smtplib
from email.mime.text import MIMEText
from email import charset


class SMTP:
    def __init__(
        self, host=None, port=587, ssl=False, tls=False, user=None, password=None
    ):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.tls = tls
        self.user = user
        self.password = password


class Message:
    def __init__(self, subject=None, body=None, fromEmail=None, toEmail=None):
        self.subject = subject
        self.body = body
        self.fromEmail = fromEmail
        self.toEmail = toEmail


class Email:
    @staticmethod
    def send(message: Message, smtp: SMTP):
        try:
            if not smtp.host:
                raise Exception("SMTP host is required")

            if not message.fromEmail:
                raise Exception("From email is required")

            if not message.toEmail:
                raise Exception("To email is required")

            msg = MIMEText(message.body, "plain", "utf-8")
            msg["From"] = message.fromEmail
            msg["To"] = message.toEmail
            msg["Subject"] = message.subject

            charset.add_charset("utf-8", charset.SHORTEST, charset.QP)

            if smtp.ssl:
                server = smtplib.SMTP_SSL(smtp.host, smtp.port)
            else:
                server = smtplib.SMTP(smtp.host, smtp.port)

            if smtp.tls:
                server.starttls()

            if smtp.user and smtp.password:
                server.login(smtp.user, smtp.password)

            text = msg.as_string()
            server.sendmail(message.fromEmail, message.toEmail, text)
            server.quit()
        except Exception as e:
            raise Exception("Failed to send email: {}".format(e))
