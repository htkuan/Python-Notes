import asyncio


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')


loop = asyncio.get_event_loop()

# run multi coroutines in loop
loop.run_until_complete(asyncio.gather(is_coroutine(1), is_coroutine(2)))

# or

# tasks = [is_coroutine(1), is_coroutine(2)]
# loop.run_until_complete(asyncio.gather(*tasks))

# or
# tasks2 = [asyncio.ensure_future(is_coroutine(1)),
#           asyncio.ensure_future(is_coroutine(2))]
# loop.run_until_complete(asyncio.gather(*tasks2))

# gather 起聚合的作用，把多個 futures 包裝成單個 future，
# 因為 loop.run_until_complete 只接受單個 future