import asyncio

# 注意 1.
# loop.stop() 必須要被調用才會停止 loop 運行
# 這意味著你必須要把 loop.stop() 寫在被調用的協程內
# 假若你把 loop.stop() 寫在 loop.run_forever() 下一行
# 那 loop 將永遠不會調用到 stop() 來停止


async def is_coroutine(loop, x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print(f'done by sleep {x} second')
    loop.stop()


loop = asyncio.get_event_loop()

coroutine = is_coroutine(loop, 3)
asyncio.ensure_future(coroutine)
coroutine2 = is_coroutine(loop, 1)
asyncio.ensure_future(coroutine2)

loop.run_forever()
