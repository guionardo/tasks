import logging
import unittest

from src.tasks.service.logging_service import get_log_bytes, setup_logging


class TestLoggingService(unittest.TestCase):
    def test_setup_logging(self):
        setup_logging('%(levelname)s - %(message)s')
        logging.info('test')
        logging.error('error')

        self.assertEqual(get_log_bytes(), b'INFO - test\nERROR - error\n')
