import { FETCH_EXPERIMENT, LOG_RECEIVED, DATA_RECEIVED } from '../actions/index'
import _ from 'lodash'

export default function (state = {}, action) {
  var protocol_id = '';
  var device_id = '';
  switch (action.type) {
  case FETCH_EXPERIMENT:
      return { ...state, [action.payload.data.protocol_id]:
                            {protocol_id: action.payload.data.protocol_id,
                             data: _.groupBy(action.payload.data.data, data => data.device_id),
                             started_on: action.payload.data.protocol_submit_time,
                             devices: (_.keys(action.payload.data.protocol)).join(),
                             protocol: action.payload.data.protocol,
                             steps: action.payload.logs || [],
                             protocol_submit_time: action.payload.data.protocol_submit_time}};
      // Groups protocol data by device id. {device_id: [data...]...}
      // Axios returns the request in payload.data... our request returns
      // the data under the dict key 'data', hence the two datas...
  case LOG_RECEIVED:
      protocol_id = action.payload.protocol_id
      return {...state, [protocol_id]:
                {...state[protocol_id], steps:
                    [...state[protocol_id].steps, action.payload]
                }
             };

  case DATA_RECEIVED:
      protocol_id = action.payload.protocol_id
      device_id = action.payload.device_id
      console.log(state[protocol_id].data)
      var data = {}
      //Trying to add data into an undefined array will cause an error
      //Need to initialize the array before the creation of the first datapoint.
      //If there is data for the device,
      if (!state[protocol_id].data[device_id]) {
        data = {...state[protocol_id].data, [device_id]: [action.payload]}
      }
      else {
        data = {...state[protocol_id].data, [device_id]:
          [...state[protocol_id].data[device_id], action.payload]}
      }
      console.log(data)
      return {...state, [protocol_id]:
                {...state[protocol_id], data}
              };
  default:
    return state;
  }

}
