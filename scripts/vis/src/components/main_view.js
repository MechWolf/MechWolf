import React, { Component } from 'react';

import ProtocolView from './protocol_view';
import NetworkView from './network_view';

export default class MainView extends Component {
  render() {
    return (
      <div>
        <ProtocolView />
      </div>
    );
  }
}
