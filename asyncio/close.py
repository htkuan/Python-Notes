import asyncio


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')


loop = asyncio.get_event_loop()
loop.run_until_complete(is_coroutine(1))
loop.run_until_complete(is_coroutine(1))
tasks = asyncio.gather(is_coroutine(1), is_coroutine(2))
# loop.close()
loop.run_until_complete(tasks)
loop.close()
