import asyncio
import time
from collections import namedtuple
from contextlib import ExitStack
from datetime import datetime
from typing import Iterable, List, Union

from loguru import logger

from ..components import ActiveComponent, Sensor
from .experiment import Experiment

Datapoint = namedtuple("Datapoint", ["data", "timestamp", "experiment_elapsed_time"])


async def main(experiment: Experiment, dry_run: Union[bool, int], strict: bool):
    """
    The function that actually does the execution of the protocol.

    Args:
    - `experiment`: The experiment to execute.
    - `dry_run`: Whether to simulate the experiment or actually perform it.
        If an integer greater than zero, the dry run will execute at that many times speed.
    - `strict`: Whether to stop execution upon any errors.
    """

    tasks = []

    # Run protocol
    # Enter context managers for each component (initialize serial ports, etc.)
    # We can do this with contextlib.ExitStack on an arbitrary number of components
    try:
        with ExitStack() as stack:
            if not dry_run:
                components = [
                    stack.enter_context(component)
                    for component in experiment.compiled_protocol.keys()
                ]
            else:
                components = list(experiment.compiled_protocol.keys())
            for component in components:
                # Find out when each component's monitoring should end
                procedures: Iterable = experiment.compiled_protocol[component]
                end_times: List[float] = [p["time"] for p in procedures]
                end_time: float = max(end_times)  # we only want the last end time
                logger.debug(f"Calculated {component} end time is {end_time}s")

                for procedure in experiment.compiled_protocol[component]:
                    tasks.append(
                        wait_and_execute_procedure(
                            procedure=procedure,
                            component=component,
                            experiment=experiment,
                            dry_run=dry_run,
                            strict=strict,
                        )
                    )

                # for sensors, add the monitor task
                if isinstance(component, Sensor):
                    logger.debug(f"Creating sensor monitoring task for {component}")
                    monitor_task = monitor(component, experiment, bool(dry_run), strict)
                    end_monitoring_task = end_monitoring(component, end_time, dry_run)
                    tasks.extend((monitor_task, end_monitoring_task))

            # Add a reminder about FF
            if type(dry_run) == int:
                logger.info(f"Simulating at {dry_run}x speed...")

            # begin the experiment
            experiment.start_time = time.time()
            start_msg = f"{experiment} started at {datetime.utcfromtimestamp(experiment.start_time)} UTC"
            logger.success(start_msg)
            try:
                await asyncio.gather(*tasks)

                # when this code block is reached, the tasks will have completed
                experiment.end_time = time.time()
                end_msg = f"{experiment} completed at {datetime.utcfromtimestamp(experiment.end_time)} UTC"
                logger.success(end_msg)
            except RuntimeError:
                logger.critical("Protocol execution is stopping NOW!")
            except:  # noqa
                logger.exception("Failed to execute protocol due to uncaught error!")
    finally:
        # allow sensors to start monitoring again
        logger.debug("Stopping all sensors")
        for component in list(experiment.compiled_protocol.keys()):
            component.update_from_params(component.base_state())  # reset object
            if isinstance(component, Sensor):
                component._stop = True

        # set some protocol metadata
        experiment.protocol.is_executing = False
        experiment.protocol.was_executed = True

        if experiment._bound_logger is not None:  # type: ignore
            logger.trace("Deactivating logging to Jupyter notebook widget...")
            logger.remove(experiment._bound_logger)  # type: ignore


async def wait_and_execute_procedure(
    procedure,
    component: ActiveComponent,
    experiment: Experiment,
    dry_run: Union[bool, int],
    strict: bool,
):

    # wait for the right moment
    execution_time = procedure["time"]
    if type(dry_run) == int:
        await asyncio.sleep(execution_time / dry_run)
    else:
        await asyncio.sleep(execution_time)

    component.update_from_params(
        procedure["params"]
    )  # NOTE: this doesn't actually call the update() method

    if dry_run:
        logger.info(
            f"Simulating: {procedure['params']} on {component}"
            f" at {procedure['time']}s"
        )
    else:
        logger.info(
            f"Executing: {procedure['params']} on {component}"
            f" at {procedure['time']}s"
        )
        try:
            component.update()  # NOTE: This does!
        except Exception as e:
            logger.error(f"Failed to update {component}!")
            if strict:
                raise RuntimeError(
                    f"Failed to update {component}. Got exception of type {type(e)} with message '{str(e)}'.'"
                )

    record = {
        "timestamp": time.time(),
        "params": procedure["params"],
        "type": "executed_procedure" if not dry_run else "simulated_procedure",
        "component": component,
    }
    record["experiment_elapsed_time"] = record["timestamp"] - experiment.start_time

    experiment.executed_procedures.append(record)


async def monitor(sensor: Sensor, experiment: Experiment, dry_run: bool, strict: bool):
    logger.debug(f"Started monitoring {sensor.name}")
    sensor._stop = False
    try:
        async for result in sensor.monitor(dry_run=dry_run):
            experiment.update(
                device=sensor.name,
                datapoint=Datapoint(
                    data=result["data"],
                    timestamp=result["timestamp"],
                    experiment_elapsed_time=result["timestamp"] - experiment.start_time,
                ),
            )
    except Exception as e:
        logger.error(f"Failed to update {sensor}!")
        if strict:
            raise RuntimeError(
                f"Failed to update {sensor}. Got exception of type {type(e)} with message {str(e)}"
            )


async def end_monitoring(sensor: Sensor, end_time: float, dry_run: Union[bool, int]):
    """
    Creates a new async task that ends the monitoring for a `components.sensor.Sensor` when it is done for the protocol.

    component (`components.sensor.Sensor`): A `components.sensor.Sensor` to end monitoring for.
    end_time (float): The end time for the sensor in EET.
    """
    if type(dry_run) == int:
        await asyncio.sleep(end_time / dry_run)
    else:
        await asyncio.sleep(end_time)
    logger.debug(f"Setting {sensor}._stop to True in order to stop monitoring")
    sensor._stop = True
