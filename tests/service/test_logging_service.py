import logging
import tempfile
import unittest

from tasks.service.logging_service import get_log_bytes, setup_logging


class TestLoggingService(unittest.TestCase):
    def test_setup_logging(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            setup_logging('%(levelname)s - %(message)s', config_path=tmp_dir)
            logging.info('test')
            logging.error('error')

            self.assertEqual(get_log_bytes(), b'INFO - test\nERROR - error\n')
