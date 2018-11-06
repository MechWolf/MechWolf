import { FETCH_CURRENT_PROTOCOL } from '../actions/index'
import _ from 'lodash'

export default function (state = {}, action) {
  switch (action.type) {
  case FETCH_CURRENT_PROTOCOL:
    return(
      // Groups protocol data by device id. {device_id: [data...]...}
      // Axios returns the request in payload.data... our request returns
      // the data under the dict key 'data', hence the two datas...
      _.groupBy(action.payload.data.data, data => data.device_id));
  default:
    return state;
  }

}
