import logging, sys, os
from datetime import datetime

class Logger:
    def __init__(self, name="ZeniiXMusic"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        os.makedirs("logs", exist_ok=True)
        fh = logging.FileHandler(f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def info(self, msg): self.logger.info(msg)
    def error(self, msg): self.logger.error(msg)
    def warning(self, msg): self.logger.warning(msg)
    def debug(self, msg): self.logger.debug(msg)
