import asyncio


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')


loop = asyncio.get_event_loop()

coroutine = is_coroutine(3)
asyncio.ensure_future(coroutine)

loop.run_forever()
