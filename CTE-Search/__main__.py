
from cli import Interface
from asyncio import create_task, sleep, run, gather
from LogManager import *

async def start_multitasking():
    # LOGGER MUST START FIRST FOR LOGGING TO WORK
    logger_task = create_task(logger_loop()) #Start the Logger loop in a separate task
    inter = Interface()
    interface_task = create_task(inter.run())  # Start curses in a separate task
    await gather(interface_task,logger_task)

if __name__ == "__main__":
    run(start_multitasking())
