import asyncio


async def is_coroutine(sec):
    print(f'sleep {sec} second')
    await asyncio.sleep(sec)


loop = asyncio.get_event_loop()
task = loop.create_task(is_coroutine(3))
loop.run_until_complete(task)
