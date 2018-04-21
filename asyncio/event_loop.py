import asyncio


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')


loop = asyncio.get_event_loop()
loop.run_until_complete(is_coroutine(5))

# or
# loop.run_until_complete(asyncio.ensure_future(is_coroutine(5)))
