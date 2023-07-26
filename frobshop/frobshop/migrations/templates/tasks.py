from celery import shared_task

@shared_task
def remove_past_bookings():
    command = remove_past_bookings.Command()
    command.handle()  # call the command here
