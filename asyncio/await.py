import asyncio
import time


async def await1():
    await asyncio.sleep(1)


async def await2():
    await asyncio.sleep(3)


async def await3():
    await asyncio.sleep(1)
    await asyncio.sleep(3)


async def await4():
    await asyncio.gather(asyncio.sleep(1), asyncio.sleep(3))


time1 = time.time()
loop1 = asyncio.get_event_loop()
loop1.run_until_complete(await3())
time2 = time.time()
print(time2-time1)

time3 = time.time()
loop2 = asyncio.get_event_loop()
loop2.run_until_complete(asyncio.wait([await1(), await2()]))
time4 = time.time()
print(time4-time3)

time5 = time.time()
loop3 = asyncio.get_event_loop()
loop3.run_until_complete(await4())
time6 = time.time()
print(time6-time5)
