import asyncio
import functools


async def is_coroutine(loop, x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print(f'done by sleep {x} second')


def callback(loop, future):
    print(type(loop))
    print(type(future))
    loop.stop()


loop = asyncio.get_event_loop()

futures = asyncio.gather(is_coroutine(loop, 1), is_coroutine(loop, 3))
futures.add_done_callback(functools.partial(callback, loop))

loop.run_forever()

# 其實這基本上就是 run_until_complete 的實現了，
# run_until_complete 在內部也是調用 run_forever
