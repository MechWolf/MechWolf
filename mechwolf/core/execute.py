import asyncio
import time
import traceback
from collections import namedtuple
from contextlib import ExitStack
from copy import deepcopy
from time import asctime, localtime
from typing import TYPE_CHECKING, Dict, Iterable, List, Union

from loguru import logger

from .. import __version__
from ..components import ActiveComponent, Sensor

# handle the hard issue of circular dependencies
if TYPE_CHECKING:
    from .experiment import Experiment


Datapoint = namedtuple("Datapoint", ["data", "timestamp", "experiment_elapsed_time"])


class ProtocolCancelled(Exception):
    pass


async def main(experiment: "Experiment", dry_run: Union[bool, int], strict: bool):
    """
    The function that actually does the execution of the protocol.

    Arguments:
    - `experiment`: The experiment to execute.
    - `dry_run`: Whether to simulate the experiment or actually perform it. If an integer greater than zero, the dry run will execute at that many times speed.
    - `strict`: Whether to stop execution upon any errors.
    """

    # logger.warning("Support for pausing execution is EXPERIMENTAL!")
    logger.info(f"Using MechWolf v{__version__} ⚙️🐺")
    logger.info("Performing final launch status check...")

    tasks = []

    # Run protocol
    # Enter context managers for each component (initialize serial ports, etc.)
    # We can do this with contextlib.ExitStack on an arbitrary number of components
    try:
        with ExitStack() as stack:
            if not dry_run:
                components = []
                for component in experiment._compiled_protocol.keys():
                    components.append(stack.enter_context(component))
            else:
                components = list(experiment._compiled_protocol.keys())
            for component in components:
                # Find out when each component's monitoring should end
                procedures: Iterable = experiment._compiled_protocol[component]
                end_times: List[float] = [p["time"] for p in procedures]
                end_time: float = max(end_times)  # we only want the last end time
                logger.trace(f"Calculated end time for {component} as {end_time}s")

                for procedure in experiment._compiled_protocol[component]:
                    tasks.append(
                        wait_and_execute_procedure(
                            procedure=procedure,
                            component=component,
                            experiment=experiment,
                            dry_run=dry_run,
                            strict=strict,
                        )
                    )
                logger.trace(f"Task list generated for {component}")

                # for sensors, add the monitor task
                if isinstance(component, Sensor):
                    logger.trace(f"Creating sensor monitoring task for {component}")
                    tasks.append(_monitor(component, experiment, bool(dry_run), strict))
                logger.debug(f"{component} is GO")
            logger.debug(f"All components are GO!")

            # Add a task to monitor the stop button
            tasks.append(check_if_cancelled(experiment))
            tasks.append(pause_handler(experiment, end_time, components))
            tasks.append(end_loop(experiment))
            logger.debug("All tasks are GO")

            # Add a reminder about FF
            if type(dry_run) == int:
                logger.info(f"Simulating at {dry_run}x speed...")

            # begin the experiment
            logger.info("All checks passed. Experiment is GO! 💥🚀💥")
            experiment.is_executing = True
            experiment.start_time = time.time()

            # convert to local time for the start message
            _local_time = asctime(localtime(experiment.start_time))
            start_msg = f"{experiment} started at {_local_time}."

            logger.success(start_msg)

            try:
                done, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_EXCEPTION
                )

                # when this code block is reached, the tasks will have either all completed or
                # an exception has occurred.
                experiment.end_time = time.time()

                # when this code block is reached, the tasks will have completed or have been cancelled.
                _local_time = asctime(localtime(experiment.end_time))
                end_msg = f"{experiment} completed at {_local_time}."

                # Stop all of the sensors and exit the read loops
                logger.debug("Resetting all components")

                # reset object
                for component in list(experiment._compiled_protocol.keys()):
                    # reset object
                    logger.debug(f"Resetting {component} to base state")
                    component._update_from_params(component._base_state)

                await asyncio.sleep(1)

                # Cancel all of the remaining tasks
                logger.debug("Cancelling all remaining tasks")
                for task in pending:
                    task.cancel()

                # Raise exceptions, if any
                logger.debug("Raising exceptions, if any")
                for task in done:
                    task.result()

                # we only reach this line if things went well
                logger.success(end_msg)

            except RuntimeError as e:
                logger.error(f"Got {repr(e)}. Full traceback is logged at trace level.")
                logger.error("Protocol execution is stopping NOW!")
                logger.critical(end_msg)

            except ProtocolCancelled:
                logger.error(f"Stop button pressed.")
                logger.critical(end_msg)

            except Exception:
                logger.trace(traceback.format_exc())
                logger.error("Failed to execute protocol due to uncaught error!")
                logger.critical(end_msg)
    finally:

        # set some protocol metadata
        experiment.was_executed = True
        # after E.was_executed=True, we THEN log that we're cleaning up so it's shown
        # in the cleanup category, not with a time in EET
        logger.info("Experimentation is over. Cleaning up...")
        experiment.is_executing = False

        if experiment._bound_logger is not None:
            logger.trace("Deactivating logging to Jupyter notebook widget...")
            logger.remove(experiment._bound_logger)


async def wait_and_execute_procedure(
    procedure,
    component: ActiveComponent,
    experiment: "Experiment",
    dry_run: Union[bool, int],
    strict: bool,
):
    params = procedure["params"]

    # wait for the right moment
    execution_time = procedure["time"]
    if type(dry_run) == int:
        execution_time /= dry_run
    await wait(execution_time, experiment, f"Set {component} to {params}")

    # NOTE: this doesn't actually call the _update() method
    component._update_from_params(params)
    logger.trace(f"{component} object state updated to reflect new params.")

    if dry_run:
        logger.info(f"Simulating: {params} on {component} at {procedure['time']}s")
    else:
        logger.info(f"Executing: {params} on {component} at {procedure['time']}s")
        try:
            await component._update()  # NOTE: This does!
        except Exception as e:
            level = "ERROR" if strict else "WARNING"
            logger.log(level, f"Failed to update {component}!")
            logger.trace(traceback.format_exc())
            if strict:
                raise RuntimeError(str(e))

    record = {
        "timestamp": time.time(),
        "params": params,
        "type": "executed_procedure" if not dry_run else "simulated_procedure",
        "component": component,
    }
    record["experiment_elapsed_time"] = record["timestamp"] - experiment.start_time

    experiment.executed_procedures.append(record)


async def _monitor(
    sensor: Sensor, experiment: "Experiment", dry_run: bool, strict: bool
):
    logger.debug(f"Started monitoring {sensor.name}")
    try:
        async for result in sensor._monitor(dry_run=dry_run, experiment=experiment):
            await experiment._update(
                device=sensor.name,
                datapoint=Datapoint(
                    data=result["data"],
                    timestamp=result["timestamp"],
                    experiment_elapsed_time=result["timestamp"] - experiment.start_time,
                ),
            )
        logger.debug(f"Stopped monitoring {sensor}")
    except Exception as e:
        logger.log("ERROR" if strict else "WARNING", f"Failed to read {sensor}!")
        logger.trace(traceback.format_exc())
        if strict:
            raise RuntimeError(str(e))


async def end_loop(experiment: "Experiment"):
    await wait(experiment.protocol._inferred_duration, experiment, "End loop")
    experiment._end_loop = True


async def check_if_cancelled(experiment: "Experiment") -> None:
    while not experiment._end_loop:
        if experiment.cancelled:
            raise ProtocolCancelled("protocol cancelled")
        await asyncio.sleep(0)


async def pause_handler(
    experiment: "Experiment", end_time: float, components: List[ActiveComponent]
) -> None:
    was_paused = False
    states: Dict[ActiveComponent, dict] = {}
    # this is either the planned duration of the experiment or cancellation
    while not experiment._end_loop:

        # we need to pause
        if experiment.paused and not was_paused:
            was_paused = True
            for component in components:
                logger.debug(f"Pausing {component}.")
                states[component] = deepcopy(component.__dict__)
                component._update_from_params(component._base_state)
                await component._update()
            logger.debug("All components set to base states.")
            logger.trace(f"Saved states are {states}.")

        # we are paused but the button was hit, so we need to resume
        elif not experiment.paused and was_paused:
            logger.trace(f"Previous states: {states}")
            for component in components:
                for k, v in states[component].items():
                    setattr(component, k, v)
                await component._update()
                logger.debug(f"Reset {component} to {states[component]}.")
            was_paused = False
            states = {}
            logger.debug("All components reset to state before pause.")

        await asyncio.sleep(0)


async def wait(duration: float, experiment: "Experiment", name: str):
    """A pause-aware version of asyncio.sleep"""
    await asyncio.sleep(duration)
    logger.trace(f"<{name}> Just woke up from {duration}s nap")

    while True:
        # if, at the end of sleeping, the experiment is paused, wait for it to resume
        while experiment.paused:
            await asyncio.sleep(0)
        assert not experiment.paused

        # figure out how long we've been paused for
        eet_offset = experiment._total_paused_duration
        # and where in the experimental plan we are
        assert isinstance(experiment.start_time, float)  # make the type checker happy
        eet = time.time() - experiment.start_time - eet_offset

        # do the logging thing
        logger.trace(f"EET is {eet}")
        logger.trace(f"<{name}> was supposed to execute after {duration}s")

        if (duration - eet) > 0:
            logger.trace(f"Waiting {duration - eet} more seconds")
            await asyncio.sleep(duration - eet)
        else:
            logger.trace(f"It's go time for <{name}>!")
            break
