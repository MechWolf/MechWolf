import asyncio
import time
from collections import namedtuple
from contextlib import ExitStack
from datetime import datetime

from loguru import logger

from .components import Sensor

Datapoint = namedtuple("Datapoint", ["datapoint", "timestamp"])


async def main(experiment, dry_run):

    tasks = []

    logger.info(f"Compiling protocol with dry_run = {dry_run}")
    compiled_protocol = experiment.protocol.compile(dry_run=dry_run)

    # Run protocol
    # Enter context managers for each component (initialize serial ports, etc.)
    # We can do this with contextlib.ExitStack on an arbitrary number of components

    with ExitStack() as stack:
        components = [
            stack.enter_context(component) for component in compiled_protocol.keys()
        ]
        for component in components:
            # Find out when each component's monitoring should end
            end_time = max(
                [procedure["time"] for procedure in compiled_protocol[component]]
            ).magnitude

            logger.debug(f"Calculated {component} end time is {end_time}")

            for procedure in compiled_protocol[component]:
                tasks.append(
                    create_procedure(
                        procedure=procedure,
                        component=component,
                        experiment=experiment,
                        end_time=end_time,
                        dry_run=dry_run,
                    )
                )

            # for sensors, add the monitor task
            if isinstance(component, Sensor):
                logger.debug(f"Creating sensor monitoring task for {component}")
                tasks.append(
                    monitor(component=component, experiment=experiment, dry_run=dry_run)
                )

        experiment.start_time = time.time()

        start_msg = (
            f"{experiment} started at {datetime.fromtimestamp(experiment.start_time)}"
            f" ({experiment.start_time} Unix time)"
        )
        logger.success(start_msg)
        await asyncio.gather(*tasks)

        # when this code block is reached, the tasks will have completed
        experiment.end_time = time.time()
        end_msg = (
            f"{experiment} completed at {datetime.fromtimestamp(experiment.end_time)}"
            f" ({experiment.end_time} Unix time)"
        )
        logger.success(end_msg)


async def create_procedure(procedure, component, experiment, end_time, dry_run):

    # wait for the right moment
    execution_time = procedure["time"].to("seconds").magnitude
    await asyncio.sleep(execution_time)

    component.update_from_params(
        procedure["params"]
    )  # NOTE: this doesn't actually call the update() method

    if dry_run:
        logger.info(
            f"Simulating execution: {procedure} on {component} at {time.time()}"
        )
        procedure_record = {}
    else:
        logger.info(f"Executing: {procedure} on {component} at {time.time()}")
        procedure_record = component.update()  # NOTE: This does!

    try:
        timestamp = procedure_record["timestamp"]
    except KeyError:
        logger.trace(
            f"No timestamp passed for {component}. Defaulting to current time."
        )
        timestamp = time.time()

    procedure_record["params"] = procedure["params"]
    procedure_record["type"] = (
        "executed_procedure" if not dry_run else "simulated_procedure"
    )
    procedure_record["experiment_elapsed_time"] = timestamp - experiment.start_time
    if end_time == execution_time:
        component.done = True

    experiment.executed_procedures.append(procedure_record)


async def monitor(component, experiment, dry_run):
    async for result in component.monitor(dry_run=dry_run):
        experiment.update(
            component.name,
            Datapoint(datapoint=result["datapoint"], timestamp=result["timestamp"]),
        )
