import os
import sys
import multiprocessing
import threading
import logging
from logging.handlers import RotatingFileHandler, QueueHandler


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
LOG_FOLDER = os.path.join(PROJECT_ROOT, "logs")
############### user config variables ###############

LOGGER_NAME = "debug_logger"
LOGGER_FORMAT = "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s"
DEBUG_LOG_FILE_PATH = os.path.join(LOG_FOLDER, "debug.log")
IO_LOG_FILE_PATH = os.path.join(LOG_FOLDER, "io.log")
LOG_FILE_MAX_BYTES = 1024 * 1024
LOG_FILE_BACKUP_COUNT = 7

#####################################################

########## Gunicorn configuration variables ##########

bind = "0.0.0.0:8000"
workers = 4
# workers = multiprocessing.cpu_count() * 2 + 1  # Or any other number of workers you prefer
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 100
max_requests_jitter = 20
accesslog = os.path.join(LOG_FOLDER, "gunicorn_access.log")
errorlog = os.path.join(LOG_FOLDER, "gunicorn_error.log")
timeout = 30
pidfile = "gunicorn.pid"
daemon = True

#####################################################


# Queue that will save logs from multiple workers
log_queue = multiprocessing.Queue(-1)


def setup_queue_file_handler(queue: multiprocessing.Queue):
    '''
    Function that will run as daemon thread.
    This thread continuously watches the given queue,
        and if the queue is not empty, it dequeues the element
        and logs the element.
    '''
    formatter = logging.Formatter(LOGGER_FORMAT)

    # debug logger
    debug_file_handler = RotatingFileHandler(DEBUG_LOG_FILE_PATH, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT)
    debug_file_handler.setFormatter(formatter)

    # io logger
    io_file_handler = RotatingFileHandler(IO_LOG_FILE_PATH, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT)
    io_file_handler.setFormatter(formatter)

    while True:
        try:
            record = queue.get()
            if record is None:
                break
            debug_file_handler.emit(record)
            if record.levelno == logging.INFO:
                io_file_handler.emit(record)
        except Exception as e:
            import traceback
            print(f'Error in log handler: {e}', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def start_logging_handler_thread():
    logging_thread = threading.Thread(target=setup_queue_file_handler, args=(log_queue,), daemon=True)
    logging_thread.start()


def setup_logger_for_worker(worker_pid: int):
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    # Create a QueueHandler and add it to the logger
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)
    logger.debug(f"Logger handler setup done for worker PID: {worker_pid}")


def on_starting(server):
    '''
    Gunicorn server hook.
    '''
    start_logging_handler_thread()


def on_reload(server):
    '''
    Gunicorn server hook.
    '''
    start_logging_handler_thread()


def post_worker_init(worker):
    '''
    Gunicorn server hook.
    '''
    setup_logger_for_worker(worker.pid)
