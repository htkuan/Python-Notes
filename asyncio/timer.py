import asyncio


async def timer(x, cb):
    futu = asyncio.ensure_future(asyncio.sleep(x))
    futu.add_done_callback(cb)
    await futu


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')

t = timer(3, lambda futu: print('Timer Done'))
loop = asyncio.get_event_loop()
tasks = asyncio.gather(is_coroutine(2), is_coroutine(4), t)
loop.run_until_complete(tasks)
