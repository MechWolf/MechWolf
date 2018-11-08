import React, { Component } from 'react';

import ExperimentView from './experiment_view';
import ExperimentListView from './experiment_list_view';

export default class MainView extends Component {
  render() {
    return (
      <div>
        <ExperimentListView />
        <ExperimentView />
      </div>
    );
  }
}
