import argparse
import asyncio
import signal

from structlog import get_logger

from config import configure_structlog
from consumer import Consumer
from vm import VM

configure_structlog()
logger = get_logger()


async def main():
    await VM("Consumer VM", Consumer()).run()

if __name__ == "__main__":
    asyncio.run(main())
