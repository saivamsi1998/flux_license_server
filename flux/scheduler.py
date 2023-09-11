import sched,time,threading

cond = threading.Condition()

def _schedule_sleep(t:float):
    cond.acquire()
    cond.wait(timeout=t)
    cond.release()

_task_scheduler = sched.scheduler(time.monotonic,_schedule_sleep)

def schedule_task(delay,func,keyword_args):
    cond.acquire()
    _task_scheduler.enter(delay,0,func,kwargs=keyword_args)
    cond.notify_all()
    cond.release()

def default_logger(taskId):
    print(f"Scheduling default task {taskId} running at {time.time()}")


def start_scheduler():
    def background_thread():
        _task_scheduler.enter(600,1,default_logger,kwargs={'taskId':'1'})
        _task_scheduler.run()
    threading.Thread(name='daemon', target=background_thread, daemon= True).start()