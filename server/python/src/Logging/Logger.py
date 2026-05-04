from datetime import datetime
from typing import Any


class Logger:
    def __init__(self, separator: str = '-' * 100, tab_size: int = 4):
        self.separator: str = separator
        if tab_size < 0:
            tab_size = 0
        if tab_size > 16:
            tab_size = 16
        self.tab: str = ' ' * tab_size

    def _generate_content(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True) -> str:
        if who:
            who = f'[ {who} ]: '
            x = f'{who}{f'{x}'.replace('\n', f'\n{' ' * len(who)}')}'

        content: str = f'{self.separator}\n' if use_separator else ''
        if use_timestamp:
            content += f'{datetime.now()}\n\n'
        if x:
            content += f'{x}\n\n'

        return content.replace('\t', self.tab)

    def log(self, x: Any, who: str | None = None, use_separator: bool = True, use_timestamp: bool = True) -> None:
        pass
