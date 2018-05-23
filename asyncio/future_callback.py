import asyncio


async def is_coroutine(sec):
    print(f'sleep {sec} second')
    await asyncio.sleep(sec)


def callback(future):
    print(type(future))
    print('Done')


future = asyncio.ensure_future(is_coroutine(3))
future.add_done_callback(callback)

loop = asyncio.get_event_loop()
loop.run_until_complete(future)
