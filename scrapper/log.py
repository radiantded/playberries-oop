from datetime import datetime as dt
from random import choice

from config import CONSOLE_COLORS


class WildberriesLogger:
    
    def __init__(self, task_id) -> None:
        self.task_id = task_id
        self.color = choice(CONSOLE_COLORS)
        
    async def now(self):
        return dt.now().strftime("%H:%M:%S")
    
    async def log(self, message):
        print(
            f'{self.color}{await self.now()} |',
            f'Задача {self.task_id} | {message}'
        )
