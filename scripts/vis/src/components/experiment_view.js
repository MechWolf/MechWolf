import React, { Component } from 'react';
import { connect } from 'react-redux';
import { fetchExperiment, logReceived, dataReceived } from '../actions'
import _ from 'lodash';
import LineGraphView from './line_graph_view';
import ChartJSView from './js_chart_view';
import openSocket from 'socket.io-client';

const socket = openSocket('http://localhost:5000');

class ExperimentView extends Component {

  componentDidMount() {
    const experiment_id = this.props.match.params.id
    this.props.fetchExperiment(experiment_id);
    socket.on('log', (msg) => this.props.logReceived(msg))
    socket.on('data', (msg) => this.props.dataReceived(msg))
  }

  renderTable() {
    const {experiment} = this.props
    //Renders table rows with information about the protocol.
    const table_data = {
    protocol_id: experiment.protocol_id,
    started_on: new Date(experiment.started_on).toString(),
    devices: experiment.devices }

    return (
        _.map(table_data, (value,prop) => {
          return (
            <tr key={prop}>
              <th scope='row'>{prop}</th>
              <td>{value}</td>
            </tr>
          );
          }
        )
    );
  }

  render() {
    const {experiment} = this.props;
    if (!experiment) {
      return(<div>Loading</div>);
    }
    //Renders a table and graphs of all data in the protocol.
    return (
      <div>
        <table className='table'>
          <tbody>
            {this.renderTable()}
          </tbody>
        </table>
        <h2>Device Data</h2>
        {_.map(experiment.data, (data,key) => { return(
          <div key={key}>
            <h3>{key}</h3>
            <ChartJSView data={data.map(a => a.payload).map(a => a.data)}
                           times={data.map(a =>a.timestamp)}
                           time_zero={experiment.protocol_submit_time} />
          </div> )})}
      </div>
  );
  }

}

function mapStateToProps({experiments}, ownProps) {
  return {experiment: experiments[ownProps.match.params.id]};
}


export default connect(mapStateToProps, {dataReceived, logReceived, fetchExperiment})(ExperimentView);
