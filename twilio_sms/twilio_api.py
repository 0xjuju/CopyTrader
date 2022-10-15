import twilio.rest.api.v2010.account.message
from decouple import config
from twilio.rest import Client


class Twilio:

    def __init__(self):
        self.ACCOUNT_SID = config("TWILIO_ACCOUNT_SID")
        self.AUTH_TOKEN = config("TWILIO_AUTH_TOKEN")
        self.TWILIO_NUMBER = config("TWILIO_NUMBER")
        self.client = Client(self.ACCOUNT_SID, self.AUTH_TOKEN)

    NUMBER = config("MAIN_NUMBER")

    def send_sms(self, *, body: str, to_number=NUMBER):

        message = self.client.messages.create(
            body=body,
            from_=self.TWILIO_NUMBER,
            to=to_number,
        )

        return message





