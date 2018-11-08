import { combineReducers } from 'redux';
import ProtocolReducer from './reducer_protocols';
import ApparatusReducer from './reducer_apparatus';
import ExperimentReducer from './reducer_experiment';
import ExperimentListReducer from './reducer_experiment_list';

const rootReducer = combineReducers({
    experiments: ExperimentReducer,
    experiment_list: ExperimentListReducer
});

export default rootReducer;
