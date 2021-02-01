import logging

class Log():
    def __init__(self, log_level):
        self.log_level = log_level
    def configure(self):
        self.logger = logging
        self.logger.basicConfig(
            format="%(asctime)s %(levelname)s:%(message)s", level=self.log_level)
        self.logger.getLogger('asyncio').setLevel(logging.WARNING)

log = Log(logging.INFO)