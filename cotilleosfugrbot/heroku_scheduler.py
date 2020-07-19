from webhook_tools import put
from apscheduler.schedulers.blocking import BlockingScheduler
import os

sched = BlockingScheduler()

PUT_INTERVAL = int(os.environ.get("PUT_INTERVAL", 10))

@sched.scheduled_job('interval', minutes=PUT_INTERVAL)
def timed_job():
    put(print_log=False)
    print("Llamada a twitter para mantener el servidor activo")

sched.start()