
from django_celery_beat.models import PeriodicTask
from twilio_sms.twilio_api import Twilio


def end_task(task_name, message):
    # Send sms if balance has changed
    service = Twilio()
    service.send_sms(body=message)

    # Disable task once wallet is changes and SMS is sent
    task = PeriodicTask.objects.get(name=task_name)
    task.enabled = False
    task.save()

