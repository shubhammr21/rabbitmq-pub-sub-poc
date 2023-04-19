import asyncio
from typing import Any, Callable

from publisher import Consumer, Publisher


class VM:
    def __init__(
        self,
        publisher: Publisher,
        consumers: int,
        connect_func: Callable[..., Any],
    ) -> None:
        self.publisher = publisher
        self.consumers = [Consumer(connect_func) for _ in range(consumers)]

    async def run(self) -> None:
        tasks = [self.publisher.generate_data()]
        tasks.extend([c.start_consuming() for c in self.consumers])
        await asyncio.gather(*tasks)
