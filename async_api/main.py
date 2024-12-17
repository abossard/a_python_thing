import logging  # Added import for logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiocache import cached
import aiohttp
import asyncio
import time
import random


# Shared aiohttp ClientSession
session: aiohttp.ClientSession = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global session
    session = aiohttp.ClientSession()
    print("ClientSession created")
    yield
    # Clean up the ML models and release the resources
    await session.close()
    print("ClientSession closed")

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# ----------------------------------------
# Basic Async Patterns
# ----------------------------------------
urls_to_fetch = [
    "https://jsonplaceholder.typicode.com/posts/1",
    "https://jsonplaceholder.typicode.com/posts/2",
    "https://jsonplaceholder.typicode.com/posts/3",
]

# Asynchronous HTTP requests using the shared aiohttp session with multiple URLs
async def fetch_data(url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()  # Change to JSON for better demonstration

@app.get("/fetch-multiple", description="Fetch data from multiple external APIs concurrently.")
async def get_multiple_external_data():
    urls = urls_to_fetch
    tasks = [fetch_data(url) for url in urls]
    data = await asyncio.gather(*tasks)
    return {"data": data}

@app.get("/fetch-multiple-with-errors", description="Fetch data from multiple external APIs concurrently with error handling.")
async def get_multiple_external_data_with_errors():
    urls = urls_to_fetch + ["https://jsonplaceholder.typicode.com/posts/invalid"]
    tasks = [fetch_data(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful_data = []
    failed_urls = []
    
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            logging.error(f"Error fetching {url}: {result}")
            failed_urls.append({"url": url, "error": str(result)})
        else:
            successful_data.append(result)
    
    return {"data": successful_data, "failed_urls": failed_urls}

# Concurrent execution with asyncio.gather (100 tasks)
async def sample_task(task_id):
    await asyncio.sleep(random.uniform(0.5, 2))  # Variable sleep time
    return f"Task {task_id} completed"

@app.get("/concurrent-tasks", description="Run 100 concurrent asynchronous tasks with variable sleep times.")
async def run_concurrent_tasks():
    tasks = [sample_task(i) for i in range(100)]
    results = await asyncio.gather(*tasks)
    return {"results": results}

# Background task with increased complexity
async def background_task():
    await asyncio.sleep(10)
    print("Background task completed after 10 seconds")

@app.get("/background-task", description="Trigger a background task that runs for 10 seconds.")
async def trigger_background_task():
    asyncio.create_task(background_task())
    return {"message": "Background task started with extended duration"}

# Visual concurrent tasks with increased number and duration
async def visual_task(task_id):
    duration = random.uniform(2, 5)  # Increased duration
    print(f"Task {task_id:02} |{'-' * task_id} Start")
    await asyncio.sleep(duration)
    print(f"Task {task_id:02} |{'-' * task_id} Done ({duration:.2f}s)")

@app.get("/concurrent-tasks-visual", description="Execute 100 visual concurrent tasks with increased load.")
async def run_visual_concurrent_tasks():
    tasks = [visual_task(i) for i in range(100)]
    await asyncio.gather(*tasks)
    return {"message": "Visual concurrent tasks completed with increased load"}

# Visual limited concurrency with fewer semaphore permits
async def visual_limited_task(task_id, semaphore):
    async with semaphore:
        duration = random.uniform(2, 5)
        print(f"Task {task_id:02} |{'=' * task_id} Start (Semaphore)")
        await asyncio.sleep(duration)
        print(f"Task {task_id:02} |{'=' * task_id} Done ({duration:.2f}s)")

@app.get("/limited-concurrency", description="Run 100 tasks with limited concurrency using a semaphore.")
async def run_visual_limited_concurrency():
    semaphore = asyncio.Semaphore(10)  # Increased limit to 10
    tasks = [visual_limited_task(i, semaphore) for i in range(100)]
    await asyncio.gather(*tasks)
    return {"message": "Visual limited concurrency tasks completed with increased tasks"}

# Visual queue concurrency with more workers and tasks
async def visual_worker(name, queue):
    while not queue.empty():
        task_id = await queue.get()
        duration = random.uniform(2, 5)
        print(f"{name} |{'#' * task_id} Task {task_id:02} Start")
        await asyncio.sleep(duration)
        print(f"{name} |{'#' * task_id} Task {task_id:02} Done ({duration:.2f}s)")
        queue.task_done()

@app.get("/queue-concurrency", description="Process 100 tasks using a queue with 10 worker coroutines.")
async def run_visual_queue_concurrency():
    queue = asyncio.Queue()
    for i in range(100):
        await queue.put(i)
    
    workers = [asyncio.create_task(visual_worker(f"Worker-{i}", queue)) for i in range(10)]
    await queue.join()
    for w in workers:
        w.cancel()
    return {"message": "Visual queue concurrency tasks completed with more workers"}

# ----------------------------------------
# Caching Example
# ----------------------------------------

# Caching Example with reduced TTL and more access
@cached(ttl=30)
async def get_cached_data():
    await asyncio.sleep(3)
    return {"data": "This is cached data with shorter TTL"}

@app.get("/cached-data", description="Retrieve cached data with a TTL of 30 seconds, accessed multiple times.")
async def read_cached_data():
    data = await get_cached_data()
    # Access cached data multiple times
    return {"data1": data, "data2": data, "data3": data}

# ----------------------------------------
# Handling Blocking I/O
# ----------------------------------------

# Handling blocking I/O with longer duration
def blocking_io():
    time.sleep(10)
    return "Blocking I/O operation completed after 10 seconds"

@app.get("/blocking-io", description="Handle a blocking I/O operation by running it in a separate thread.")
async def handle_blocking_io():
    result = await asyncio.to_thread(blocking_io)
    return {"result": result}

# ----------------------------------------
# Bad Blocking Examples
# ----------------------------------------

# Bad Blocking Examples intensified
@app.get("/bad-blocking-sleep", description="Endpoint demonstrating a blocking sleep of 10 seconds.")
async def bad_blocking_sleep():
    time.sleep(10)  # Increased blocking sleep
    return {"message": "This endpoint used a longer blocking sleep!"}

@app.get("/bad-blocking-while", description="Endpoint demonstrating a CPU-bound blocking loop.")
async def bad_blocking_while():
    i = 0
    while i < 5e8:  # Increased CPU-bound blocking loop
        i += 1
    return {"message": "This endpoint used a longer blocking while loop!"}

@app.get("/bad-blocking-file-io", description="Endpoint performing extensive blocking file I/O operations.")
async def bad_blocking_file_io():
    with open("very_large_file.txt", "w") as f:
        for i in range(50000000):
            f.write(f"Line {i}\n")  # Increased number of lines
    return {"message": "This endpoint performed extensive blocking file I/O!"}

# ----------------------------------------
# Root Endpoint
# ----------------------------------------

@app.get("/", description="Root endpoint welcoming users to the FastAPI async demo with Azure OpenTelemetry.")
async def root():
    return {"message": "Welcome to the FastAPI async demo with Azure OpenTelemetry!"}

# ----------------------------------------
# Entry Point
# ----------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
