import logging
import io
import sys
from typing import Optional


class Logger:
    log_stream = None

    def __init__(self, **kwargs):
        if (
            not logging.getLogger("Python API").hasHandlers()
            or len(logging.getLogger("Python API").handlers) == 0
        ):
            Logger.log_stream = self._create_logger(**kwargs)
        self.log = logging.getLogger("Python API")

    @staticmethod
    def _create_logger(
        file: str = None,
        file_level=logging.INFO,
        console=True,
        console_level=logging.DEBUG,
        variable=False,
        variable_level=logging.INFO,
    ) -> Optional[io.StringIO]:
        """
        Method that is called when no logger named AccCat exists.
        Registers logger, and based on parameters logs appropriate
        level to correct destination
        :param file: path for log file or None
        :param file_level: message level to be logged to file
        :param console: If True log is outputted to standard console
        :param console_level: message level for console
        :param variable: If True string stream is recorded as vh handler
        and can be retrieved to variable
        :param variable_level: message level for string stream
        :return: None
        """
        log = logging.getLogger("Python API")
        log.setLevel(logging.DEBUG)
        handlers = []
        if file is not None:
            fh = logging.FileHandler(file)
            fh.setLevel(file_level)
            handlers.append(fh)
        if console:
            ch = logging.StreamHandler(stream=sys.stdout)
            ch.setLevel(console_level)
            handlers.append(ch)
        if variable:
            log_stream = io.StringIO()
            vh = logging.StreamHandler(log_stream)
            vh.setLevel(variable_level)
            handlers.append(vh)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s: %(module)s: %(funcName)s  - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        for handler in handlers:
            handler.setFormatter(formatter)
            log.addHandler(handler)

        if variable:
            return log_stream
        else:
            return None
