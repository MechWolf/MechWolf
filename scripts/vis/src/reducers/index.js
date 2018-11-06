import { combineReducers } from 'redux';
import ProtocolReducer from './reducer_protocols';
import ApparatusReducer from './reducer_apparatus';
import DataReducer from './reducer_data';

const rootReducer = combineReducers({
    current_protocol: ProtocolReducer,
    current_apparatus: ApparatusReducer,
    current_data: DataReducer
});

export default rootReducer;
