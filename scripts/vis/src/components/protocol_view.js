import React, { Component } from 'react';
import { connect } from 'react-redux';
import { fetchCurrentProtocol } from '../actions'
import _ from 'lodash';
import LineGraphView from './line_graph_view'
import NetworkView from './network_view'

class ProtocolView extends Component {

  componentDidMount() {
    this.props.fetchCurrentProtocol();
  }

  renderTable() {
    //Renders table rows with information about the protocol.
    const table_data = {
    protocol_id: this.props.current_protocol.protocol_id,
    started_on: Date(this.props.current_protocol.protocol_submit_time),
    devices: (_.keys(this.props.current_protocol.protocol)).join() }

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
    //Renders a table and graphs of all data in the protocol.

    return (
      <div>
        <table className='table'>
          <tbody>
            {this.renderTable()}
          </tbody>
        </table>
        <h2>Device Data</h2>
        {_.map(this.props.current_data, (data,key) => { return(
          <div key={key}>
            <h3>{key}</h3>
            <LineGraphView data={data} time_zero={this.props.current_protocol.protocol_submit_time} />
          </div> )})}
      </div>
  );
  }

}

function mapStateToProps(state) {
  return {current_protocol: state.current_protocol,
          current_data: state.current_data};
}

export default connect(mapStateToProps, { fetchCurrentProtocol })(ProtocolView);
