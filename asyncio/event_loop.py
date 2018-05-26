import asyncio
import time


async def coroutine1():
    await asyncio.sleep(1)


async def coroutine2():
    await asyncio.sleep(3)


async def coroutine3():
    await asyncio.sleep(1)
    await asyncio.sleep(3)


async def coroutine4():
    await asyncio.gather(asyncio.sleep(1), asyncio.sleep(3))


loop1_start = time.time()
loop1 = asyncio.get_event_loop()
loop1.run_until_complete(asyncio.wait([coroutine1(), coroutine2()]))
loop1_end = time.time()
print(f'loop1 running time = {loop1_end - loop1_start} sec')

loop2_start = time.time()
loop2 = asyncio.get_event_loop()
loop2.run_until_complete(coroutine3())
loop2_end = time.time()
print(f'loop2 running time = {loop2_end - loop2_start} sec')

loop3_start = time.time()
loop3 = asyncio.get_event_loop()
loop3.run_until_complete(coroutine4())
loop3_end = time.time()
print(f'loop3 running time = {loop3_end - loop3_start} sec')
