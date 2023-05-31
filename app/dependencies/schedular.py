import logging
from rocketry import Rocketry

app = Rocketry(execution="async", config={"task_execution": "async"})

# Create some tasks


@app.task("every 5 seconds")
async def do_things():
    logging.info("Here I am")


if __name__ == "__main__":
    app.run()
