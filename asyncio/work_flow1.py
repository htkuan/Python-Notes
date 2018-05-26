import asyncio


async def coroutine1():
    print('in to coroutine1')
    print('meet I/O block 1')
    await asyncio.sleep(1)
    print('return from I/O 1')
    print('out of coroutine1')


async def coroutine2():
    print('in to coroutine2')
    print('meet I/O block 2')
    await asyncio.sleep(2)
    print('return from I/O 2')
    print('out of coroutine2')


async def coroutine3():
    print('in to coroutine3')
    await coroutine1()
    print('out of coroutine3')


async def coroutine4():
    print('in to coroutine4')
    await coroutine2()
    print('out of coroutine4')


loop1 = asyncio.get_event_loop()
loop1.run_until_complete(asyncio.wait([coroutine1(), coroutine2()]))
print("")
loop2 = asyncio.get_event_loop()
loop2.run_until_complete(asyncio.wait([coroutine3(), coroutine4()]))
