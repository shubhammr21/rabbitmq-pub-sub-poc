import argparse
import asyncio
import signal

from structlog import get_logger

from config import configure_structlog
from connection import connect_to_rabbitmq
from publisher import Publisher
from vm import VM

configure_structlog()
logger = get_logger()


if __name__ == "__main__":
    publisher = Publisher(connect_to_rabbitmq)
    vm = VM(publisher, consumers=5, connect_func=connect_to_rabbitmq)

    try:
        asyncio.run(vm.run())
    except KeyboardInterrupt:
        print("Shutting down...")
