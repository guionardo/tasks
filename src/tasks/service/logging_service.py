import io
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from tasks.consts import BASE_CONFIG_PATH

_log_bytes_buffer = io.BytesIO()
_log_text_stream = io.TextIOWrapper(_log_bytes_buffer, encoding='utf-8')
_log_file: Path = None


def setup_logging(
    format: str = '%(asctime)s %(name)-10s [%(levelname)-8s] %(message)s',
    config_path: Path = BASE_CONFIG_PATH,
    log_level: str = logging.INFO,
    log_file: str = (BASE_CONFIG_PATH / 'tasks.log').as_posix(),
) -> None:
    global _log_file
    _log_file = log_file
    _log_bytes_buffer.seek(0)
    _log_bytes_buffer.truncate(0)

    handler = logging.StreamHandler(_log_text_stream)
    handler.setFormatter(logging.Formatter(format, datefmt='%H:%M:%S'))
    log_file = (Path(config_path) / 'tasks.log').as_posix()

    file_handler = TimedRotatingFileHandler(
        log_file, when='M', interval=2, backupCount=10
    )

    file_handler.setFormatter(logging.Formatter(format, datefmt='%H:%M:%S'))
    logging.basicConfig(
        level=log_level,
        handlers=[handler, file_handler],
        force=True,
    )


def get_log_bytes() -> bytes:
    _log_text_stream.flush()
    lines = _log_bytes_buffer.getvalue()
    _log_bytes_buffer.seek(0)
    _log_bytes_buffer.truncate(0)

    return lines


def get_logger(log_name: str = __name__) -> logging.Logger:
    return logging.getLogger(log_name.split('.')[-1].removesuffix('_service'))


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
