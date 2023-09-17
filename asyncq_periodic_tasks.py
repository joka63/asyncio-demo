#!/usr/bin/env python3
# asyncq_periodic_tasks.py

import asyncio
import os
import random
import time
import argparse
import logging


jobs = {}


async def make_item(size: int = 5) -> str:
    return os.urandom(size).hex()


async def run(cmd) -> (int, str, str):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    out = stdout.decode() if stdout else ''
    err = stderr.decode() if stderr else ''
    return proc.returncode, out, err


async def run_sleep(caller=None, min_secs: int = 2, max_secs: int = 5) -> (int, str, str):
    i = random.randint(min_secs, max_secs)
    if caller:
        logging.debug(f"{caller} sleeping for {i} seconds.")
    ret, out, err = await run(f"sleep {i}; echo '{caller}'")
    return ret, out, err


async def rand_sleep(caller=None, min_secs: int = 2, max_secs: int = 5) -> None:
    i = random.randint(min_secs, max_secs)
    if caller:
        logging.debug(f"{caller} sleeping for {i} seconds.")
    await asyncio.sleep(i)


async def produce_submit_requests(i: int, max_submits: int, q: asyncio.Queue) -> None:
    logging.debug(f"Starting {max_submits} submits, each {i} seconds")
    for count in range(max_submits):
        if count > 0:
            await asyncio.sleep(i)
        t = time.perf_counter()
        await q.put((count, t))
        logging.debug(f"Added submit request #<{count}> to queue.")
    logging.debug(f"Finished sending submit requests")


async def produce_status_requests(i2: int, max_submits: int, q: asyncio.Queue) -> None:
    logging.debug(f"Watching status each {i2} seconds")
    num_finished_jobs = 0
    while num_finished_jobs < max_submits:
        await asyncio.sleep(i2)
        t = time.perf_counter()
        await q.put(t)
        logging.debug(f"Added status request to queue.")
        num_finished_jobs = len([j for j in jobs if jobs[j]['finished'] is not None])
    logging.debug(f"Finished watching status requests")


async def consume_submit_request(name: int, q: asyncio.Queue, q2: asyncio.Queue) -> None:
    while True:
        count, t = await q.get()
        ret, out, err = await run_sleep(caller=f"Consumer {name}, executing submit #{count}")
        now = time.perf_counter()
        if ret == 0:
            logging.info(f"{out.strip()} in {now-t:0.5f} seconds.")
            await q2.put((count, t, now))
            logging.info(f"Started job#<{count}>")
        else:
            logging.error(f"Submit failed with exit code {ret}")
        q.task_done()


async def consume_submitted_request(name: int, q: asyncio.Queue) -> None:
    global jobs
    while True:
        count, t0, t1 = await q.get()
        jobs[str(count)] = {'submitted': t0, 'started': t1, 'finished': None}
        await run_sleep(f"Consumer {name}, executing submitted #{count}", 10, 30)
        now = time.perf_counter()
        logging.debug(f"Consumer {name} processed job #<{count}>" 
                      f" in {now - t1:0.5f} seconds.")
        jobs[str(count)] = {'submitted': t0, 'started': t1, 'finished': now}
        q.task_done()


async def consume_status_request(name: int, q: asyncio.Queue) -> None:
    global jobs
    while True:
        await q.get()
        await run_sleep(f"Consumer {name}, executing status request", 1, 2)
        num_started_jobs = len([j for j in jobs if jobs[j]['finished'] is None])
        num_finished_jobs = len([j for j in jobs if jobs[j]['finished'] is not None])
        logging.info(f"{num_started_jobs} jobs are running, {num_finished_jobs} are finished")
        q.task_done()


async def main(interval: int, max: int, statusinterval: int, ncon: int, verbose: bool):
    submit_queue = asyncio.Queue()
    lsf_queue = asyncio.Queue()
    status_queue = asyncio.Queue()
    producers = [asyncio.create_task(produce_submit_requests(interval, max, submit_queue)),
                 asyncio.create_task(produce_status_requests(statusinterval, max, status_queue))
                 ]
    consumers = [asyncio.create_task(consume_submit_request(n, submit_queue, lsf_queue)) for n in range(ncon)]
    consumers2 = [asyncio.create_task(consume_submitted_request(n, lsf_queue)) for n in range(ncon)]
    consumers3 = [asyncio.create_task(consume_status_request(n, status_queue)) for n in range(2)]
    await asyncio.gather(*producers)
    logging.debug(f"All submit requests produced")
    await submit_queue.join()  # Implicitly awaits consumers, too
    logging.debug(f"All submit requests executed")
    for c in consumers:
        c.cancel()
    await lsf_queue.join()  # Implicitly awaits consumers, too
    logging.info(f"All job requests executed:")
    for c in consumers2:
        c.cancel()
    await status_queue.join()  # Implicitly awaits consumers, too
    for c in consumers3:
        c.cancel()
    print(f"Jobid;Runtime;Roundtriptime")
    for jobid in jobs:
        t0 = jobs[str(jobid)]['submitted']
        t1 = jobs[str(jobid)]['started']
        t2 = jobs[str(jobid)]['finished']
        print(f"{jobid};{t2-t1:0.2f};{t2-t0:0.2f}")


if __name__ == "__main__":
    random.seed(444)
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--interval", type=int, default=2)
    parser.add_argument("-m", "--max", type=int, default=20)
    parser.add_argument("-s", "--statusinterval", type=int, default=15)
    parser.add_argument("-c", "--ncon", type=int, default=10)
    parser.add_argument("-v", "--verbose", action='store_true')
    ns = parser.parse_args()
    if ns.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s :: %(levelname)s :: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')
    start = time.perf_counter()
    asyncio.run(main(**ns.__dict__))
    elapsed = time.perf_counter() - start
    logging.info(f"Program completed in {elapsed:0.5f} seconds.")
