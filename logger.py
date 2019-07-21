from datetime import datetime
from typing import Optional

LOGFILE_NAME = 'log.txt'


class Logger:
    @classmethod
    def add_entry(cls, text: Optional[str]):
        with open(LOGFILE_NAME, 'a') as file:
            if text is None:
                file.write("\n")
            else:
                file.write(f"{datetime.now().replace(microsecond=0)}: {text}\n")
