from celery.task.schedules import crontab
from celery.decorators import periodic_task
from celery.utils.log import get_task_logger
from django.utils import timezone

from .views import send_summary_email

logger = get_task_logger(__name__)

@periodic_task(
	run_every=(crontab(minute='*/15')),
	name="task_send_summary_email",
	ignore_result=True
)
def task_send_summary_email():
	today = timezone.localtime(timezone.now())
	
	send_summary_email()
	logger.info("Sending summary email")