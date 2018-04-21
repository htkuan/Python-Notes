import threading
import asyncio


async def hello1():
    print('Hello world 1! (%s)' % threading.currentThread())
    await asyncio.sleep(1)
    print('Hello again 1! (%s)' % threading.currentThread())


@asyncio.coroutine
def hello2():
    print('Hello world 22 (%s)' % threading.currentThread())
    yield from asyncio.sleep(1)
    print('Hello again 22 (%s)' % threading.currentThread())


loop = asyncio.get_event_loop()
tasks = [hello1(), hello2()]
loop.run_until_complete(asyncio.wait(tasks))

loop.close()
