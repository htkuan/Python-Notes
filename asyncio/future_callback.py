import asyncio


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)


def callback(future):
    print(type(future))
    print('Done')


future = asyncio.ensure_future(is_coroutine(3))
future.add_done_callback(callback)

loop = asyncio.get_event_loop()
loop.run_until_complete(future)
