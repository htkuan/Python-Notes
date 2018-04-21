import asyncio


async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')

print(asyncio.iscoroutinefunction(is_coroutine))
print(asyncio.iscoroutine(is_coroutine))

coroutine_obj = is_coroutine(5)  # 調用 async def 函數會返回一個 coroutine object

print(asyncio.iscoroutine(coroutine_obj))

# 出現警告，因為並沒有辦法直接運行 coroutine object
# sys:1: RuntimeWarning: coroutine 'is_coroutine' was never awaited
