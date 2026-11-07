import smtplib
import ssl
from email.mime.text import MIMEText
from email import charset

SMTP_TIMEOUT_SECONDS = 30


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

            context = ssl.create_default_context()

            if smtp.ssl:
                server = smtplib.SMTP_SSL(
                    smtp.host, smtp.port, timeout=SMTP_TIMEOUT_SECONDS, context=context
                )
            else:
                server = smtplib.SMTP(smtp.host, smtp.port, timeout=SMTP_TIMEOUT_SECONDS)

            with server:
                if smtp.tls:
                    server.starttls(context=context)

                if smtp.user and smtp.password:
                    server.login(smtp.user, smtp.password)

                server.sendmail(message.fromEmail, message.toEmail, msg.as_string())
        except Exception as e:
            raise Exception("Failed to send email: {}".format(e))
