import sys
import multiprocessing
import threading
import logging
from logging.handlers import RotatingFileHandler, QueueHandler

############### user config variables ###############

LOGGER_NAME = "debug_logger"
LOGGER_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEBUG_LOG_FILE_NAME = "debug.log"
IO_LOG_FILE_NAME = "io.log"
LOG_FILE_MAX_BYTES = 1024 * 1024
LOG_FILE_BACKUP_COUNT = 7

#####################################################

########## Gunicorn configuration variables ##########

bind = "0.0.0.0:8000"
workers = 4
# workers = multiprocessing.cpu_count() * 2 + 1  # Or any other number of workers you prefer
worker_class = "uvicorn.workers.UvicornWorker"
max_requests = 100
max_requests_jitter = 10
accesslog = "access.log"
errorlog = "error.log"
timeout = 100000
# timeout = 30
pidfile = "gunicorn.pid"

#####################################################


log_queue = multiprocessing.Queue(-1)


def setup_queue_file_handler(queue):
    formatter = logging.Formatter(LOGGER_FORMAT)

    # debug logger
    debug_file_handler = RotatingFileHandler(DEBUG_LOG_FILE_NAME, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT)
    debug_file_handler.setFormatter(formatter)

    # io logger
    io_file_handler = RotatingFileHandler(IO_LOG_FILE_NAME, maxBytes=LOG_FILE_MAX_BYTES, backupCount=LOG_FILE_BACKUP_COUNT)
    io_file_handler.setFormatter(formatter)

    while True:
        try:
            record = queue.get()
            if record is None:
                break
            debug_file_handler.emit(record)
            if record.levelno >= logging.INFO:
                io_file_handler.emit(record)
        except Exception as e:
            import traceback
            print(f'Error in log handler: {e}', file=sys.stderr)
            traceback.print_exc(file=sys.stderr)


def start_logging_handler_thread():
    logging_thread = threading.Thread(target=setup_queue_file_handler, args=(log_queue,))
    logging_thread.daemon = True
    logging_thread.start()


def setup_worker_logging(worker_pid: int):
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    # Create a QueueHandler and add it to the logger
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)
    logger.debug(f"Logger handler setup done for worker PID: {worker_pid}")


def on_starting(server):
    start_logging_handler_thread()


def on_reload(server):
    start_logging_handler_thread()


def post_worker_init(worker):
    setup_worker_logging(worker.pid)
