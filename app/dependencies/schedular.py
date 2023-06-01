import logging
from rocketry import Rocketry

app = Rocketry(execution="async", config={"task_execution": "async"})

# Create some tasks


@app.task("every 10 seconds")
async def do_things():
    logging.info("Here I am")

