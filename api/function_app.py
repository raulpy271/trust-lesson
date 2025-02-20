import azure.functions as func
import datetime
import json
import logging

from api.jobs.update_status_lesson import run

app = func.FunctionApp()

@app.timer_trigger(schedule="*/1 * * * *", arg_name="timer", run_on_startup=False, use_monitor=False)
def updateStatusLesson(timer: func.TimerRequest) -> None:
    logging.info('Python timer trigger function running.')
    run()
    logging.info('Python timer trigger function executed.')

