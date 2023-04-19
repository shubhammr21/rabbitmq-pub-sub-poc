import asyncio
import signal

from structlog import configure, get_logger
from structlog.dev import ConsoleRenderer
from structlog.processors import (JSONRenderer, StackInfoRenderer, TimeStamper,
                                  format_exc_info)
from structlog.stdlib import LoggerFactory

from consumer import Consumer
from publisher import Publisher
from vm import VM

configure(
    processors=[
        StackInfoRenderer(),
        format_exc_info,
        TimeStamper(fmt="ISO"),
        ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=get_logger().__class__,
    cache_logger_on_first_use=True,
)

logger = get_logger()


async def main():
    publisher_vm = VM("Publisher VM", Publisher())
    consumer_vms = [VM("Consumer VM", Consumer()) for _ in range(5)]

    tasks = [publisher_vm.run()] + [vm.run() for vm in consumer_vms]

    async def cancel_tasks(signal):
        logger.info(f"Received signal {signal}, cancelling tasks...")
        for task in tasks:
            task.cancel()

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(cancel_tasks(s)))

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Tasks cancelled, shutting down...")
    finally:
        for s in signals:
            loop.remove_signal_handler(s)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.exception("Unhandled exception", exc_info=e)
    finally:
        loop.close()
