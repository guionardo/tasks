import io
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

_log_bytes_buffer = io.BytesIO()
_log_text_stream = io.TextIOWrapper(_log_bytes_buffer, encoding='utf-8')


def setup_logging(
    format: str = '%(asctime)s %(name)-10s [%(levelname)-8s] %(message)s',
) -> None:
    _log_bytes_buffer.seek(0)
    _log_bytes_buffer.truncate(0)

    handler = logging.StreamHandler(_log_text_stream)
    handler.setFormatter(logging.Formatter(format, datefmt='%H:%M:%S'))

    file_handler = RotatingFileHandler(
        'app.log', maxBytes=1024 * 1024 * 5, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(format, datefmt='%H:%M:%S'))
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler, file_handler],
        force=True,
    )


def get_log_bytes() -> bytes:
    _log_text_stream.flush()
    return _log_bytes_buffer.getvalue()


def get_logger(log_name: str = __name__) -> logging.Logger:
    return logging.getLogger(log_name.split('.')[-1])


def save_log_to_file(log_file: Path = None) -> Path:
    log_file = (
        log_file
        or Path(f'./{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.log').absolute()
    )
    try:
        with open(log_file, 'wb') as f:
            f.write(get_log_bytes())
    except Exception as e:
        get_logger().exception('Failed to save log to file: %s', e)
        return None
    return Path(log_file)
