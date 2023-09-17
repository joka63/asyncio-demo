[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![de](https://img.shields.io/badge/lang-de-yellow.svg)](README.de.md)

# asyncio-demo
Exploring features of Python's asyncio

## Examples

### async_periodic_tasks.py

- Submit periodically up to 20 jobs for a fictive batch system (each 2 seconds)
- Check status of submitted jobs periodically, each 15 seconds
- Finish when all fictive jobs have terminated and print a turn-around statistics of all jobs as table in a .csv format

- Long lasting commands are simulated by a sleep command or by a call to asyncio.sleep() with a random duration
- Use producer/consumer design pattern with 3 queues
- Periodic tasks are implemted by loops adding a request to the asyncio.Queue and sleeping for a fix duration
- Consumers process the submits and status checks
  

## Related Asyncio Tutorials

- [RealPython: Async IO in Python - A Complete Walkthrough](https://realpython.com/async-io-python)
