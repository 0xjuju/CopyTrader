
from django.test import TestCase
from twilio_sms.twilio_api import Twilio


class TestTwilioApi(TestCase):
    def setUp(self):
        self.client = Twilio()

    def test_send_sms(self):
        message = self.client.send_sms(body="Second Test")




