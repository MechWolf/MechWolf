import asyncio
import logging
import time
from collections import namedtuple
from contextlib import ExitStack
from uuid import uuid1

from bokeh.io import output_notebook, push_notebook, show
from bokeh.plotting import figure

from .mechwolf import term

server = "http://localhost:5000"

Datapoint = namedtuple('Datapoint', ['datapoint', 'timestamp'])

class Experiment(object):
    '''
        Experiments contain all data from execution of a protocol.
    '''

    def __init__(self,
                 experiment_id,
                 protocol,
                 apparatus,
                 start_time,
                 data,
                 executed_procedures):
        self.experiment_id = experiment_id
        self.protocol = protocol
        self.apparatus = apparatus
        self.start_time = start_time
        self.data = data
        self.executed_procedures = executed_procedures

        self._charts = {}
        self._transformed_data = {}

    def _transform_data(self, device):
        data = self.data[device]
        return {'datapoints': [datapoint.datapoint for datapoint in data],
                'timestamps': [datapoint.timestamp - self.start_time for datapoint in data]}

    def visualize(self):
        output_notebook()

        for device in self.data:
            self._transformed_data[device] = self._transform_data(device)
            p = figure(title=f'{device} data', plot_height=300, plot_width=600)
            r = p.line(source=self._transformed_data[device], x='timestamps', y='datapoints', color='#2222aa', line_width=3)
            target = show(p, notebook_handle=True)
            #Register chart for continuous updating
            self._charts[device] = (target, r)

    def update_chart(self, device, datapoint):
        #If a chart has been registered to the device, update it.
        if device not in self.data:
            self.data[device] = []
        self.data[device].append(datapoint)
        if device in self._transformed_data:
            target, r = self._charts[device]
            self._transformed_data[device]['datapoints'].append(datapoint.datapoint)
            self._transformed_data[device]['timestamps'].append(datapoint.timestamp - self.start_time)
            r.data_source.data['datapoints'] = self._transformed_data[device]['datapoints']
            r.data_source.data['timestamps'] = self._transformed_data[device]['timestamps']
            push_notebook(handle=target)

    def procedure_did_execute(self, procedure_record):
        self.executed_procedures.append(procedure_record)

class DeviceNotFound(Exception):
    '''Raised if a device specified in the protocol is not in the apparatus.'''
    pass

def jupyter_execute(protocol, **kwargs):
    '''
        Executes the specified protocol in a jupyter notebook.

        Args:
            protocol: A protocol of the form mechwolf.Protocol

        Returns:
            mechwolf.Experiment object containing information about the running
            protocol.

        Raises:
            DeviceNotFound: if a device in the protocol is not in the apparatus.
    '''
    #reinitialize objects
    for component in protocol.compile().keys():
        component.done = False
    #Extract the protocol from the Protocol object (or protocol json)
    apparatus = protocol.apparatus
    experiment_id = f'{time.strftime("%Y_%m_%d")}_{uuid1()}'
    print(term.green_bold(f'Experiment {experiment_id} in progress'))
    start_time = time.time()
    experiment = Experiment(experiment_id,
                            protocol,
                            apparatus,
                            start_time,
                            data={},
                            executed_procedures=[])

    asyncio.ensure_future(main(protocol, apparatus, start_time, experiment_id, experiment))
    return experiment

def execute(protocol, delay=5, **kwargs):
    '''
        Executes the specified protocol.
        Starts after the specified delay.

        Args:
            protocol: A protocol of the form mechwolf.Protocol
            apparatus: An apparatus of the form mechwolf.Apparatus
            delay (sec): Number of seconds to delay execution of the protocol.

        Returns:
            mechwolf.Experiment object containing information about the running
            protocol.

        Raises:
            DeviceNotFound: if a device in the protocol is not in the apparatus.
    '''

    #Extract the protocol from the Protocol object (or protocol json)
    apparatus = protocol.apparatus
    experiment_id = f'{time.strftime("%Y_%m_%d")}_{uuid1()}'
    start_time = time.time() + delay
    print(f'Experiment {experiment_id} in progress')

    try:
        logs = asyncio.run(main(protocol, apparatus, start_time, experiment_id))
    finally:
        for component in protocol.compile().keys():
            component.done = False

    executed_procedures = []
    data = {}
    for log in logs:
        if log['type'] == 'executed_procedure':
            executed_procedures.append(log)
        if log['type'] == 'data':
            component_name = log['component_name']
            data[component_name] = log['data']

    return Experiment(experiment_id,
                      protocol,
                      apparatus,
                      start_time,
                      data,
                      executed_procedures)

async def main(protocol, apparatus, start_time, experiment_id, experiment):

    if protocol.__class__.__name__ == 'Protocol':
        p = protocol.compile()
    else:
        raise TypeError('protocol not of type mechwolf.Protocol')
        #TODO allow JSON protocol parsing

    if apparatus.__class__.__name__ != 'Apparatus':
        raise TypeError('apparatus not of type mechwolf.Apparatus')
        #Todo allow parsing of apparatus json

    #Check that all devices in the protocol were passed to the executor.
    for component in p.keys():
        if component not in apparatus.components:
            raise DeviceNotFound(f'Component {component} not in apparatus.')

    tasks = []

    # Run protocol
    # Enter context managers for each component (initialize serial ports, etc.)
    # We can do this with contextlib.ExitStack on an arbitrary number of components

    tasks += [log_start(protocol, start_time, experiment_id, experiment)]
    with ExitStack() as stack:
        components = [stack.enter_context(component) for component in p.keys()]
        for component in components:
            # Find out when each component's monitoring should end
            times = [procedure['time'] for procedure in p[component]]
            end_time = max(times).magnitude
            tasks += [create_procedure(procedure, component, experiment_id, experiment, end_time)
                      for procedure in p[component]]
            tasks += [monitor(component, end_time, experiment_id, experiment)]

        completed_tasks = await asyncio.gather(*tasks)
        return completed_tasks

async def create_procedure(procedure, component, experiment_id, experiment, end_time):

    execution_time = procedure["time"].to("seconds").magnitude
    await asyncio.sleep(execution_time)
    logging.info(term.green(f"Executing: {procedure} on {component} at {time.time()}"))
    component.update_from_params(procedure["params"])
    procedure_record = component.update()
    procedure_record['type'] = 'executed_procedure'
    procedure_record['executed_time'] = procedure_record['timestamp'] - experiment.start_time
    if end_time == execution_time:
        component.done = True

    experiment.procedure_did_execute(procedure_record)
    return procedure_record

async def monitor(component, end_time, experiment_id, experiment):
    device_id = component.name
    async for result in component.monitor():
        if result is None:
            return
        datapoint = Datapoint(datapoint=result['datapoint'], timestamp=result['timestamp'])
        experiment.update_chart(device_id, datapoint)
    return {'component_name': component.name, 'data': experiment.data[device_id], 'type': 'data'}

async def log_start(protocol, start_time, experiment_id, experiment):
    return {"experiment_id": experiment_id,
            "experiment_start_time": start_time,
            "type": "experiment_start"}
