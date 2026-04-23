from __future__ import annotations

import textwrap
from typing import List, Tuple

import tcod.console

from game import color


class Message:
    def __init__(self, text: str, fg: Tuple[int, int, int]) -> None:
        self.plain_text = text
        self.fg         = fg
        self.count      = 1

    @property
    def full_text(self) -> str:
        return f"{self.plain_text} (x{self.count})" if self.count > 1 else self.plain_text


class MessageLog:
    def __init__(self) -> None:
        self.messages: List[Message] = []

    def add(self, text: str, fg: Tuple[int, int, int] = color.WHITE) -> None:
        if self.messages and self.messages[-1].plain_text == text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))

    def render(
        self,
        console: tcod.console.Console,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        y_offset = height - 1
        for msg in reversed(self.messages):
            for line in reversed(textwrap.wrap(msg.full_text, width)):
                console.print(x, y + y_offset, line, fg=msg.fg)
                y_offset -= 1
                if y_offset < 0:
                    return
