import asyncio
import time
import threading

async def afunc():
    print('async', threading.current_thread())
    await asyncio.sleep(1)
    
def func():
    print('sync', threading.current_thread())
    return time.sleep(1)

def async_to_sync(afunc):
    new_loop = asyncio.get_event_loop()
    return new_loop.run_until_complete(afunc)

@asyncio.coroutine
def sync_to_async(func):
    new_thread = threading.Thread(target=func)
    return new_thread.start()

# sync 的 code，沒辦法跑在 async 的 event loop 中，
# 所以開一個 thread 去跑這個 sync 的 code
sync_to_async(func())

# async 的 code，沒辦法在 sync 的 code 中 run，
# 所以開一個 event loop 去跑這個 async 的 code
async_to_sync(afunc())

# 非同步的環境
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.gather(afunc(), sync_to_async(func())))

# 同步的環境
func()
async_to_sync(afunc())

