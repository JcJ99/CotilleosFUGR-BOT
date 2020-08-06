from webhook_tools import put
from apscheduler.schedulers.blocking import BlockingScheduler
import os
import threading

sched = BlockingScheduler()

PUT_INTERVAL = int(os.environ.get("PUT_INTERVAL", 10))

@sched.scheduled_job('interval', minutes=PUT_INTERVAL)
def timed_job():
    t = threading.Thread(target=put, kwargs={"print_log": False, "fail_register": True})
    t.run()
    print("Llamada a twitter para mantener el servidor activo")

sched.start()