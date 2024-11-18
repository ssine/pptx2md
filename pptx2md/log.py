import logging
import sys

from tqdm import tqdm


class TqdmStreamHandler(logging.StreamHandler):

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(compat_tqdm=True):
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    if compat_tqdm:
        stream_handler = TqdmStreamHandler(sys.stdout)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)

    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stream_handler)
