import asyncio
import aiohttp
import requests
import time

def run(tasks):
    t1 = time.time()
    asyncio.get_event_loop().run_until_complete(tasks)
    return time.time() - t1

async def request1(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# 這樣是沒用的，底層還是block
@asyncio.coroutine
def request2(url):
    return requests.get(url).text 

url = 'https://www.google.com.tw/search?q=wiki&oq=wiki&aqs=chrome..69i57j0j69i60l3j0.4125j1j8&sourceid=chrome&ie=UTF-8'
r1_lt = [request1(url) for _ in range(20)]
tasks1 = asyncio.gather(*r1_lt)

print('async non-block request time:', run(tasks1))

r2_lt = [request2(url) for _ in range(20)]
tasks2 = asyncio.gather(*r2_lt)

print('fake async block request time', run(tasks2))
