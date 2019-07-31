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

WAIT_DURATION = 0.5


class ProtocolCancelled(Exception):
    pass


async def main(experiment: Experiment, dry_run: Union[bool, int], strict: bool):
    """
    The function that actually does the execution of the protocol.

    Arguments:
    - `experiment`: The experiment to execute.
    - `dry_run`: Whether to simulate the experiment or actually perform it. If an integer greater than zero, the dry run will execute at that many times speed.
    - `strict`: Whether to stop execution upon any errors.
    """

    logger.warning("Support for pausing execution is EXPERIMENTAL!")

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

                # Add a task to monitor the stop button
                tasks.append(check_if_cancelled(experiment, end_time))

                # for sensors, add the monitor task
                if isinstance(component, Sensor):
                    logger.debug(f"Creating sensor monitoring task for {component}")
                    monitor_task = monitor(component, experiment, bool(dry_run), strict)
                    end_monitoring_task = end_monitoring(
                        component, end_time, dry_run, experiment
                    )
                    tasks.extend((monitor_task, end_monitoring_task))

            # Add a reminder about FF
            if type(dry_run) == int:
                logger.info(f"Simulating at {dry_run}x speed...")

            # begin the experiment
            experiment.start_time = time.time()
            start_msg = f"{experiment} started at {datetime.utcfromtimestamp(experiment.start_time)} UTC"
            logger.success(start_msg)
            try:
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_EXCEPTION
                )

                # when this code block is reached, the tasks will have either all completed or
                # an exception has occurred.
                experiment.end_time = time.time()

                # when this code block is reached, the tasks will have completed or have been cancelled.
                end_msg = f"{experiment} completed at {datetime.utcfromtimestamp(experiment.end_time)} UTC"

                # Cancel all of the remaining tasks
                logger.trace("Cancelling all remaining tasks")
                for task in pending:
                    task.cancel()

                # Raise exceptions, if any
                logger.trace("Raising exceptions, if any")
                for task in done:
                    task.result()

                # we only reach this line if things went well
                logger.success(end_msg)

            except RuntimeError as e:
                logger.error(f"Got {repr(e)}")
                logger.error("Protocol execution is stopping NOW!")
                logger.critical(end_msg)

            except ProtocolCancelled:
                logger.error(f"Stop button pressed.")
                logger.critical(end_msg)

            except:  # noqa
                logger.exception("Failed to execute protocol due to uncaught error!")
                logger.critical(end_msg)
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
        execution_time /= dry_run

    time_awaited = 0.0
    while time_awaited < execution_time - WAIT_DURATION:
        if not experiment.paused:
            time_awaited += WAIT_DURATION
        await asyncio.sleep(WAIT_DURATION)
    logger.trace(
        f"{component} is waiting a final {execution_time - time_awaited} seconds"
    )
    await asyncio.sleep(execution_time - time_awaited)

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
            await component.update()  # NOTE: This does!
        except Exception as e:
            logger.log(
                "ERROR" if strict else "WARNING", f"Failed to update {component}!"
            )
            if strict:
                raise RuntimeError(str(e))

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
        logger.log("ERROR" if strict else "WARNING", f"Failed to read {sensor}!")
        if strict:
            raise RuntimeError(str(e))


async def end_monitoring(
    sensor: Sensor, end_time: float, dry_run: Union[bool, int], experiment: Experiment
) -> None:
    """
    Creates a new async task that ends the monitoring for a `components.sensor.Sensor` when it is done for the protocol.

    - `sensor`: The sensor to end monitoring for.
    - `end_time`: The end time for the sensor in EET.
    - `dry_run`: Whether a dry run is in progress.
    - `experiment`: The experiment that's in progress.

    """
    if type(dry_run) == int:
        end_time /= dry_run
    time_awaited = 0.0

    # spend most of the time checking to see if the protocol is paused
    while time_awaited < end_time - WAIT_DURATION:
        if not experiment.paused:
            time_awaited += WAIT_DURATION
        await asyncio.sleep(WAIT_DURATION)
    await asyncio.sleep(end_time - time_awaited)

    logger.debug(f"Setting {sensor}._stop to True in order to stop monitoring")
    sensor._stop = True


async def check_if_cancelled(experiment: Experiment, end_time: float) -> None:
    time_awaited = 0.0
    while time_awaited < end_time:
        await asyncio.sleep(WAIT_DURATION)
        time_awaited += WAIT_DURATION
        if experiment.cancelled is True:
            raise ProtocolCancelled("protocol cancelled")
