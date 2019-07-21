import os
from typing import Set

DB_NAME = 'database'


class Database:
    @classmethod
    def store(cls, content: Set[str]):
        with open(DB_NAME, 'a') as file:
            file.write('\n'.join(content) + '\n')

    @classmethod
    def retrieve_all_trip_ids(cls) -> Set[str]:
        if os.path.exists(DB_NAME):
            with open(DB_NAME, 'r') as file:
                return {trip_id.strip() for trip_id in file}

        return set()
