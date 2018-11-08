import React, { Component } from 'react';
import { connect } from 'react-redux';
import { fetchExperimentList } from '../actions';
import _ from 'lodash';

class ExperimentListView extends Component {
  componentDidMount() {
    this.props.fetchExperimentList();
  }

  render() {
      return (
        <div>
          <h1>Experiments</h1>
          <ul className='list-group'>
            {_.map(this.props.experiment_list, experiment => {
              return (
                <button className="list-group-item"
                        key={experiment}
                        onClick={() => {this.props.history.push(`/vis/experiments/${experiment}`)}}>
                  {experiment}
                </button>
              );
            })}
          </ul>
        </div>
      );
  }

}

function mapStateToProps(state) {
  return {experiment_list: state.experiment_list};
}

export default connect(mapStateToProps, { fetchExperimentList })(ExperimentListView);
