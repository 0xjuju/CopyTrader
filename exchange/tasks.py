from asyc_modules.periodic_functions import end_task
from celery import shared_task
from exchange.coinbase import Coinbase
from twilio_sms.twilio_api import Twilio


@shared_task()
def check_for_new_listings_coinbase() -> None:
    """
    Check for new product listings on Coinbase. Add new entries to database and send SMS alert
    """

    try:
        cb = Coinbase()
        new_products = cb.check_for_new_products()
        if new_products:
            # Send sms of new products
            Twilio().send_sms(body=f"New Products present on Coinbase:\n{new_products}")
        else:
            print(f"NONE: {new_products}")

    except Exception as e:
        end_task(task_name="check_coinbase_listings",
                 message=f"Unknown Error detected for Coinbase function:\n{e}")


