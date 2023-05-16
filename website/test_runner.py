import logging
from time import time
from unittest.runner import TextTestResult, TextTestRunner
from django.test.runner import DiscoverRunner


class LogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        logformat = '%(name)s: %(levelname)s: %(message)s'
        fmt = logging.Formatter(logformat)
        self.setFormatter(fmt)
        self.buffer = []

    def emit(self, record):
        msg = self.format(record)
        self.buffer.append(msg)

    def flush(self):
        pass

    def clear(self):
        self.buffer.clear()


class TimedTextTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        root_logger = logging.getLogger()
        if hasattr(root_logger, "handlers"):
            for handler in root_logger.handlers:
                root_logger.removeHandler(handler)
        root_logger.setLevel('DEBUG')
        self.handler = LogHandler()
        root_logger.addHandler(self.handler)
        self.clocks = dict()

    def startTest(self, test):
        self.clocks[test] = time()
        super().startTest(test)
        self.stream.write(self.getDescription(test))
        self.stream.write(' ... ')
        self.stream.flush()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.writeln('(%.6fs)' % (time() - self.clocks[test]))
        self.handler.clear()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.writeln()
        if self.handler.buffer:
            test.captured_logs = self.handler.buffer.copy()
        self.handler.clear()

    def addError(self, test, err):
        super().addError(test, err)
        self.stream.writeln()
        if self.handler.buffer:
            test.captured_logs = self.handler.buffer.copy()
        self.handler.clear()

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)
            if hasattr(test, 'captured_logs'):
                self.stream.writeln(self.separator2)
                self.stream.writeln('>> begin captured logging <<')
                self.stream.write('\n'.join(test.captured_logs))
                self.stream.writeln('\n>> end captured logging <<')
            self.stream.flush()


class TimedTextTestRunner(TextTestRunner):
    resultclass = TimedTextTestResult


class TestRunner(DiscoverRunner):
    test_runner = TimedTextTestRunner
