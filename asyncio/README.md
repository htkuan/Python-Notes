# asyncio 內部實現機制

首先因為 GIL 的關係，python 在單進程(process)的情況下，

線程(thread)無法真正的並行(parallelism)，但是可以並發(concurrency)，

而多線程的並發在切換線程時，需要耗費較大的資源，

所以發展了協程(co-routine)的概念，即在單一線程下，當遇到I/O阻塞的時候，

把控制流讓出來給別的程式執行，並且等待回覆後續處理的過程。

asyncio 透過 event loop & coroutines & futures 來構造並發的能力！

## Coroutine

在 python 中，coroutine 是借用了 generator 的特性來實現，

利用 yield 可以暫停執行並且向外返回數據，以及 send() 方法向 generator 發送數據等特性，

實現了 coroutine 遇到 I/O 阻塞時可以讓出執行流，和等待 I/O 完成時再繼續執行等，

在 python 3.4 可以利用 @asyncio.coroutine 的 decorator 來定義，

然而在 python 3.5 之後則是直接在，function 前面加入 async 即可:

ex. coroutine.py
```python
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


print(asyncio.iscoroutinefunction(is_coroutine1))  # True
print(asyncio.iscoroutinefunction(is_coroutine2))  # True
print(asyncio.iscoroutine(is_coroutine1))  # False
print(asyncio.iscoroutine(is_coroutine2))  # False

coroutine_obj = is_coroutine1(5)  # 調用 async def 函數會返回一個 coroutine object

print(asyncio.iscoroutine(coroutine_obj))  # True

# 出現警告，因為並沒有辦法直接運行 coroutine object
# sys:1: RuntimeWarning: coroutine 'is_coroutine1' was never awaited
```

## Future

Future 顧名思義代表著未來對象，也就是用來儲存 coroutine 的 I/O 的結果，

所以在 asyncio 中的 class Future，有 result() 和 set_result() 方法用來儲存結果，

也有 add_done_callback() 方法，來添加 callback，

所以一般來說在註冊 coroutine 到 event loop 時，會用 future 打包 coroutine:

ex. future_callback.py
```python
import asyncio


async def is_coroutine(sec):
    print(f'sleep {sec} second')
    await asyncio.sleep(sec)


def callback(future):
    print(type(future))
    print('Done')

# 把 coroutine 包成 future
future = asyncio.ensure_future(is_coroutine(3))
# 添加 callback 到 future
future.add_done_callback(callback)

loop = asyncio.get_event_loop()
loop.run_until_complete(future)
```
## Task

有了 coroutine 可以遇到I/O時掛起讓出執行流，又有 future 可以儲存 coroutine 異步調用結果，

好像還缺了什麼？ 要怎麼恢復執行呢？

那就建立角色來負責管理 coroutine 的狀態吧，就叫做 Task!

Task 繼承了 Future，並且利用其 *_stop()*  方法 ， 在 Event loop 管理 coroutine 狀態，

stop() 會調用 generator send() 方法來驅動 coroutine (喚醒)，

括遇到 blocking 時 coroutine 得執行，得到結果時 set_result 和調用 callback 以及下一個 future

ex. create_task.py
```python
import asyncio


async def is_coroutine(sec):
    print(f'sleep {sec} second')
    await asyncio.sleep(sec)


loop = asyncio.get_event_loop()

# 其實這裡與 future_callback.py 並沒有什麼差別
# 因為 run_until_complete() 接收到 future 時也會自動封裝成 task
# 事實上直接傳一個 coroutine 也可以
task = loop.create_task(is_coroutine(3))
loop.run_until_complete(task)
```

## Event loop

而事件循環本質上是一個程序運行時開啟的無限循環，把 coroutine 註冊進去後，

當滿足某些事件時，會調用相應的程序，所以叫做 "事件循環"，

可以透過 asyncio.get_event_loop() 來得到一個 event loop!

然後調用這個阻塞式的函數 run_until_complete() 來得到結果，

在 python 中，要執行 coroutine 有兩種方法，第一種是 coroutine 把註冊到 event loop 中，

並且運行 event loop ，此時事件循環會透過 Task 來調用 coroutine，

另一種是從一個運行中的 coroutine 去調用下一個(await) coroutine，

***run_until_complete 會把所有協程運行完畢才回傳結果***

run_until_complete() 所接的參數是 future，而為什麼我們把 coroutine 對象傳進去，

也不會有問題是因為，函數內部透過 ensure_future 檢查，把協程對象包裝(wrap)成了future，

要注意的是，需要讓 event loop 接受到 "事件"，才能在 I/O 時被掛起，然後繼續調用下一個 coroutine，

所以大家可以來看看以下的腳本，到底會執行多久，三個 event loop 到最後都會 await 兩個 sleep 的 sleep 函數，

一個 sleep 1 秒，一個 sleep 3 秒，在不阻塞的情況下，總執行時間應該會是接近 3 秒，如果是阻塞就會是 4 秒！

透過下面的三個 event loop 比較相信大家可以感受到，什麼樣的配置才能夠不阻塞！

首先 loop1 裡面有兩個 coroutine1 & coroutine2，他們都各自 await 一個 sleep 的 coroutine，

所以先運行 coroutine1 然後 await sleep 時遇到 I/O 於是掛起，Task 調用 step()，

就會換執行 coroutine2，然後又遇到 await sleep，即可達成不阻塞;

而 loop2 只註冊了一個 coroutine3，然後 coroutine3 裡面接連的 await 兩個 sleep 函數，

當 loop2 開始運行調用 coroutine3 然後 await 第一個 I/O 被掛起，但是這時並沒有下一個 await 的 sleep，

並沒有辦法被 Task 的 step() 調用到，因為被上一個 await 阻塞了，所以這樣的配置並無法達成非阻塞的調用，

***這點要非常的注意!!***

再來是 loop3，註冊了 coroutine4，而這時候多做了一件事，把兩個 sleep gather 起來，然後看看運行的秒數，

是非阻塞式的 3 秒!! 在之後的章節會討論 gather 這個函數！

ex. event_loop.py
```python
import asyncio
import time


async def coroutine1():
    await asyncio.sleep(1)


async def coroutine2():
    await asyncio.sleep(3)


async def coroutine3():
    await asyncio.sleep(1)
    await asyncio.sleep(3)


async def coroutine4():
    await asyncio.gather(asyncio.sleep(1), asyncio.sleep(3))


loop1_start = time.time()
loop1 = asyncio.get_event_loop()
loop1.run_until_complete(asyncio.wait([coroutine1(), coroutine2()]))
loop1_end = time.time()
print(f'loop1 running time = {loop1_end - loop1_start} sec')  # 3 sec

loop2_start = time.time()
loop2 = asyncio.get_event_loop()
loop2.run_until_complete(coroutine3())
loop2_end = time.time()
print(f'loop2 running time = {loop2_end - loop2_start} sec')  # 4 sec

loop3_start = time.time()
loop3 = asyncio.get_event_loop()
loop3.run_until_complete(coroutine4())
loop3_end = time.time()
print(f'loop3 running time = {loop3_end - loop3_start} sec')  # 3 sec
```

## await

為了執行 coroutine 我們必須把它註冊到 event loop 中，讓 event loop 調度，

而 coroutine 註冊進 event loop 時會被包裝成一個 task，而 future 就代表了這個 task 的結果。

這個結果可能是被執行的結果，或者尚未被執行的又或者他可能是一個被執行後拋出的例外！

await 做了什麼:
* 等待一個 future 結束
* 等待另一個協程（產生一個結果，或引發一個異常）
* 產生一個結果給正在等它的協程
* 引發一個異常給正在等它的協程

於是我們就要來探討一下，在 event loop 中，遇到 await 的時候，流程會怎麼走!

### flow of control

1. the event loop is running in a thread
2. the event loop get a task from queue
3. run coroutine1 from task1
4. coroutine1 call another coroutine( await <coroutine> )
5. I/O blocking or not:
    * yes: current coroutine1 gets suspended and control is passed back to the event loop.
    * no: current coroutine1 gets suspended and context switch occurs.
6. event loop gets next task from queue2, ...n
7. then the event loop goes back to task 1 from where it left off

大家先想想下面的腳本，在兩個 event loop 中，output 應該會打印出什麼順序！ 

ex. work_flow1.py
```python
import asyncio


async def coroutine1():
    print('in to coroutine1')
    print('meet I/O block 1')
    await asyncio.sleep(1)
    print('return from I/O 1')
    print('out of coroutine1')


async def coroutine2():
    print('in to coroutine2')
    print('meet I/O block 2')
    await asyncio.sleep(2)
    print('return from I/O 2')
    print('out of coroutine2')


async def coroutine3():
    print('in to coroutine3')
    await coroutine1()
    print('out of coroutine3')


async def coroutine4():
    print('in to coroutine4')
    await coroutine2()
    print('out of coroutine4')


loop1 = asyncio.get_event_loop()
loop1.run_until_complete(asyncio.wait([coroutine1(), coroutine2()]))
print("")
loop2 = asyncio.get_event_loop()
loop2.run_until_complete(asyncio.wait([coroutine3(), coroutine4()]))

```

## 多個協程

實際項目中，往往有多個協程，同時在一個 loop 裡運行。為了把多個協程交給 loop，需要藉助 asyncio.gather 函數。

gather 起聚合的作用，把多個 futures 包裝成單個 future，因為 loop.run_until_complete 只接受單個 future

## run_until_complete 和 run_forever

通過 run_until_complete 來運行 loop ，等到 future 完成，run_until_complete 也就返回了

run_forever 則是直到調用 stop() 才會返回。

ex. 
```bash
$ python run_complete.py 
>sleep 5 second
>done
$
表示程序退出
```

```bash
$ python run_forever.py
>sleep 3 second
>done


... 不會結束，只好 control + c
```

調用 stop
```bash
$ python run_forever_and_stop.py 
>sleep 3 second
>done by sleep 3 second
$
```

注意一旦調用了 stop() loop 就會停止，所以若是把 run_forever_and_stop.py 中，

第 21~22 行註解拿掉在運行一次:

```
$ python run_forever_and_stop.py 
>sleep 3 second
>sleep 1 second
>done by sleep 1 second
$
```

程式等待了一秒就返回停止，並沒有等待 coroutine 回傳，因為 loop 在執行 coroutine2 時已經被 stop()!

要解決這個問題，可以用 gather 把多個協程合併成一個 future，並添加回調，然後在回調裡再去停止 loop。

可以查看 forever_to_complete.py 代碼，並運行看看結果！

## loop close

上面的範例代碼，都沒有調用 loop.close()，到底要不要調用呢？

簡單的來說，只要 loop 不被關閉，都可以在運行！

但是如果先關閉的，之後在運行 loop 會發生錯誤，

大家可以嘗試著運行腳本 close.py，並且解除第 14 行註解，在運行看看差異！

建議調用 close 來關閉 loop，以免在之後 loop 對象遭到誤用！

## gather vs. wait

asyncio.gather 和 asyncio.wait 功能相似。

```
coroutines = [is_coroutine(loop, 1), is_coroutine(loop, 3)]
loop.run_until_complete(asyncio.wait(coroutines))
```
可以得到跟 gather 差不多得結果，為什麼呢？

gather 在命名的意義上是等待蒐集全部 future 的回傳的 results，

而 await 相對於 gather 是較為底層的應用，await 只是單純等待 future！

差異可以參考這篇 [stack overflow](https://stackoverflow.com/questions/42231161/asyncio-gather-vs-asyncio-wait)

## Timer

python 在 acyncio 並沒有提供原生的計時器，不過可以透過 asynic.sleep() 的方式實作，

```python
import asyncio

async def timer(x, cb):
    futu = asyncio.ensure_future(asyncio.sleep(x))
    futu.add_done_callback(cb)
    await futu

t = timer(3, lambda futu: print('Done'))
```

可以試著看一下 timer.py 腳本，並且運行看看！

