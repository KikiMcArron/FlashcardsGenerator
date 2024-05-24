import logging


class DebugFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == logging.DEBUG


# Root logger configuration
logger = logging.getLogger('flashcards_generator')
logger.setLevel(logging.DEBUG)

# Handler for AI interactions logs
queries_logger = logging.getLogger('flashcards_generator.queries')
queries_logger.setLevel(logging.DEBUG)
queries_handler = logging.FileHandler('queries_history.log')
queries_formatter = logging.Formatter('%(asctime)s\n%(message)s')
queries_handler.setFormatter(queries_formatter)
queries_handler.addFilter(DebugFilter())
queries_logger.addHandler(queries_handler)

# Handler for monitoring application behavior logs
monitoring_handler = logging.FileHandler('app_monitoring.log')
monitoring_handler.setLevel(logging.INFO)
monitoring_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
monitoring_handler.setFormatter(monitoring_formatter)
logger.addHandler(monitoring_handler)

# Handler for error logs (detailed logs to file)
error_file_handler = logging.FileHandler('error_details.log')
error_file_handler.setLevel(logging.ERROR)
error_file_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s\nPath: %(pathname)s - Line: %(lineno)d\n%(message)s', '%Y-%m-%d %H:%M:%S')
error_file_handler.setFormatter(error_file_formatter)
logger.addHandler(error_file_handler)