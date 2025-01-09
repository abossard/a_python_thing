import logging  # Added import for logging
from contextlib import asynccontextmanager
import aiohttp
import asyncio
import time
import random
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from dotenv import load_dotenv

load_dotenv()

configure_azure_monitor(
   enable_live_metrics=True,
)

from fastapi import FastAPI  # noqa: E402
from aiocache import cached  # noqa: E402


logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

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
@tracer.start_as_current_span(name="fetch_data")
async def fetch_data(url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()  # Change to JSON for better demonstration

@app.get("/fetch-multiple", description="Fetch data from multiple external APIs concurrently.")
@tracer.start_as_current_span(name="get_multiple_external_data")
async def get_multiple_external_data():
    urls = urls_to_fetch
    tasks = [fetch_data(url) for url in urls]
    data = await asyncio.gather(*tasks)
    return {"data": data}

@app.get("/fetch-multiple-with-errors", description="Fetch data from multiple external APIs concurrently with error handling.")
@tracer.start_as_current_span(name="get_multiple_external_data_with_errors")
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
@tracer.start_as_current_span(name="sample_task")
async def sample_task(task_id):
    await asyncio.sleep(random.uniform(0.5, 2))  # Variable sleep time
    return f"Task {task_id} completed"

# Background task with increased complexity
@tracer.start_as_current_span(name="background_task")
async def background_task():
    await asyncio.sleep(10)
    print("Background task completed after 10 seconds")

@app.get("/background-task", description="Trigger a background task that runs for 10 seconds.")
@tracer.start_as_current_span(name="trigger_background_task")
async def trigger_background_task():
    asyncio.create_task(background_task())
    return {"message": "Background task started with extended duration"}

# Visual concurrent tasks with increased number and duration
@tracer.start_as_current_span(name="visual_task")
async def visual_task(task_id):
    duration = random.uniform(2, 5)  # Increased duration
    print(f"Task {task_id:02} |{'-' * task_id} Start")
    await asyncio.sleep(duration)
    print(f"Task {task_id:02} |{'-' * task_id} Done ({duration:.2f}s)")

@app.get("/concurrent-tasks", description="Execute 100 visual concurrent tasks with increased load.")
@tracer.start_as_current_span(name="run_visual_concurrent_tasks")
async def run_visual_concurrent_tasks():
    tasks = [visual_task(i) for i in range(100)]
    await asyncio.gather(*tasks)
    return {"message": "Visual concurrent tasks completed with increased load"}

# Visual limited concurrency with fewer semaphore permits
@tracer.start_as_current_span(name="visual_limited_task")
async def visual_limited_task(task_id, semaphore):
    async with semaphore:
        duration = random.uniform(2, 5)
        print(f"Task {task_id:02} |{'=' * task_id} Start (Semaphore)")
        await asyncio.sleep(duration)
        print(f"Task {task_id:02} |{'=' * task_id} Done ({duration:.2f}s)")

@app.get("/limited-concurrency", description="Run 100 tasks with limited concurrency using a semaphore.")
@tracer.start_as_current_span(name="run_visual_limited_concurrency")
async def run_visual_limited_concurrency():
    semaphore = asyncio.Semaphore(10)  # Increased limit to 10
    tasks = [visual_limited_task(i, semaphore) for i in range(100)]
    await asyncio.gather(*tasks)
    return {"message": "Visual limited concurrency tasks completed with increased tasks"}

# Visual queue concurrency with more workers and tasks
@tracer.start_as_current_span(name="visual_worker")
async def visual_worker(name, queue):
    while not queue.empty():
        task_id = await queue.get()
        duration = random.uniform(2, 5)
        with tracer.start_as_current_span(name=f"visual-task-{task_id}"):
            print(f"{name} |{'#' * task_id} Task {task_id:02} Start")
            await asyncio.sleep(duration)
            print(f"{name} |{'#' * task_id} Task {task_id:02} Done ({duration:.2f}s)")
            queue.task_done()

@app.get("/queue-concurrency", description="Process 100 tasks using a queue with 10 worker coroutines.")
@tracer.start_as_current_span(name="run_visual_queue_concurrency")
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
@tracer.start_as_current_span(name="get_cached_data")
async def get_cached_data():
    await asyncio.sleep(3)
    return {"data": "This is cached data with shorter TTL"}

@app.get("/cached-data", description="Retrieve cached data with a TTL of 30 seconds, accessed multiple times.")
@tracer.start_as_current_span(name="read_cached_data")
async def read_cached_data():
    data = await get_cached_data()
    # Access cached data multiple times
    return {"data1": data, "data2": data, "data3": data}

# ----------------------------------------
# Handling Blocking I/O
# ----------------------------------------

# Handling blocking I/O with longer duration
@tracer.start_as_current_span(name="blocking_io")
def blocking_io():
    time.sleep(10)
    return "Blocking I/O operation completed after 10 seconds"

@app.get("/blocking-io", description="Handle a blocking I/O operation by running it in a separate thread.")
@tracer.start_as_current_span(name="handle_blocking_io")
async def handle_blocking_io():
    result = await asyncio.to_thread(blocking_io)
    return {"result": result}

# ----------------------------------------
# Bad Blocking Examples
# ----------------------------------------

# Bad Blocking Examples intensified
@app.get("/bad-blocking-sleep", description="Endpoint demonstrating a blocking sleep of 10 seconds.")
@tracer.start_as_current_span(name="bad_blocking_sleep")
async def bad_blocking_sleep():
    time.sleep(10)  # Increased blocking sleep
    return {"message": "This endpoint used a longer blocking sleep!"}

@app.get("/bad-blocking-while", description="Endpoint demonstrating a CPU-bound blocking loop.")
@tracer.start_as_current_span(name="bad_blocking_while")
async def bad_blocking_while():
    i = 0
    while i < 5e8:  # Increased CPU-bound blocking loop
        i += 1
    return {"message": "This endpoint used a longer blocking while loop!"}

@app.get("/bad-blocking-file-io", description="Endpoint performing extensive blocking file I/O operations.")
@tracer.start_as_current_span(name="bad_blocking_file_io")
async def bad_blocking_file_io():
    with open("very_large_file.txt", "w") as f:
        for i in range(50000000):
            f.write(f"Line {i}\n")  # Increased number of lines
    return {"message": "This endpoint performed extensive blocking file I/O!"}

# ----------------------------------------
# Root Endpoint
# ----------------------------------------

@app.get("/", description="Root endpoint welcoming users to the FastAPI async demo with Azure OpenTelemetry.")
@tracer.start_as_current_span(name="root")
async def root():
    return {"message": "Welcome to the FastAPI async demo with Azure OpenTelemetry!"}

# ----------------------------------------
# Entry Point
# ----------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
