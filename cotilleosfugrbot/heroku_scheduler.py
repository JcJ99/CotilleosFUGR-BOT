from webhook_tools import put
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=10)
def timed_job():
    put(print=False)
    print("Llamada a twitter para mantener el servidor activo")

sched.start()