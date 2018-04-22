# asyncio 內部實現機制

首先因為 GIL 的關係，python 在單進程(process)的情況下，

線程(thread)無法並行(parallelism)，但是可以並發(concurrency)，

而多線程的並發在切換線程時，需要耗費較大的資源，

所以發展了協程(coroutine)的概念，即在單一線程下，當遇到I/O阻塞的時候，

把控制流讓出來給別的程式執行，並且等待回覆後續處理的過程。

asyncio 透過 event loop & coroutines & futures 來構造並發的能力！

這篇教學是參考 [此教程](https://segmentfault.com/a/1190000008814676) 寫得非常棒，大家也可以去看看！

## async

定義 coroutine，它是一個特別的函數，類似於 python 中的 generators，

可以利用 await 來掛起控制流，並且把控制流歸還給 event loop 調度，

在 def 前加上 async

如何運行 coroutine：
* 在另一個已經運行的協程中用 `await` 等待它
* 通過 `ensure_future` 函數計劃它的執行

***簡單來說只有 event loop 運行了，協程才會運行***

## await

什麼是 future？ 

為了執行 coroutine 我們必須把它註冊到 event loop 中，讓 event loop 調度，

而 coroutine 註冊進 event loop 時會被包裝成一個 task，而 future 就代表了這個 task 的結果。

這個結果可能是被執行的結果，或者尚未被執行的又或者他可能是一個被執行後拋出的例外！

await 做了什麼:
* 等待一個 future 結束
* 等待另一個協程（產生一個結果，或引發一個異常）
* 產生一個結果給正在等它的協程
* 引發一個異常給正在等它的協程

## event loop

要運行協程，要先有一個 event loop，

event loop 實質上就是用來管理和分配不同 tasks 的執行，

把所有的 tasks 註冊給 event loop，讓 event loop 調度控制流程，

可以透過 asyncio.get_event_loop() 來得到一個 event loop!

然後調用這個阻塞式的函數 run_until_complete() 來得到結果

***run_until_complete 會把所有協程運行完畢才回傳結果***

ex.
```python
import asyncio

async def is_coroutine(x):
    print(f'sleep {x} second')
    await asyncio.sleep(x)
    print('done')
    
loop = asyncio.get_event_loop()
loop.run_until_complete(is_coroutine(5))
```

run_until_complete() 所接的參數是 future，而為什麼我們把 coroutine 對象傳進去，

也不會有問題是因為，函數內部透過 ensure_future 檢查，把協程對象包裝(wrap)成了future

所以寫的正確一點應該是:

```python
loop.run_until_complete(asyncio.ensure_future(is_coroutine(5)))
```

p.s. 我們有提到 await 跟 coroutine 的關係，再看看上述範例的 await asyncio.sleep(x)，

你就可以知道，asyncio.sleep(x)，本身其實就是一個 coroutine！

## callback

future 對象，可以透過 add_done_callback 函數，給 callback！

## 多個協程

實際項目中，往往有多個協程，同時在一個 loop 裡運行。為了把多個協程交給 loop，需要藉助 asyncio.gather 函數。

gather 起聚合的作用，把多個 futures 包裝成單個 future，因為 loop.run_until_complete 只接受單個 future

## run_until_complete 和 run_forever

通過 run_until_complete 來運行 loop ，等到 future 完成，run_until_complete 也就返回了

run_forever 則是直到調用 stop() 才會返回。

ex.
```bash
$ python event_loop.py 
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
```
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

## flow of control

1. the event loop is running in a thread
2. the event loop get a task from queue
3. run coroutine1 from task1
4. coroutine1 call another coroutine( await <coroutine> )
5. I/O blocking or not:
    * yes: current coroutine1 gets suspended and control is passed back to the event loop.
    * no: current coroutine1 gets suspended and context switch occurs.
6. event loop gets next task from queue2, ...n
7. then the event loop goes back to task 1 from where it left off
