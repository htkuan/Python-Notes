import asyncio


async def is_coroutine1(sec):
    print(f'sleep {sec} second')
    await asyncio.sleep(sec)
    print('done')


@asyncio.coroutine
def is_coroutine2(sec):
    print(f'sleep {sec} second')
    yield from asyncio.sleep(sec)
    print('done')


print(asyncio.iscoroutinefunction(is_coroutine1))
print(asyncio.iscoroutinefunction(is_coroutine2))
print(asyncio.iscoroutine(is_coroutine1))
print(asyncio.iscoroutine(is_coroutine2))

coroutine_obj = is_coroutine1(5)  # 調用 async def 函數會返回一個 coroutine object

print(asyncio.iscoroutine(coroutine_obj))

# 出現警告，因為並沒有辦法直接運行 coroutine object
# sys:1: RuntimeWarning: coroutine 'is_coroutine1' was never awaited
