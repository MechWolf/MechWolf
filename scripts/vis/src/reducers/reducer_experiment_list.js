import { FETCH_EXPERIMENT_LIST } from '../actions/index'

export default function (state = {}, action) {
  switch (action.type) {
  case FETCH_EXPERIMENT_LIST:
    return(action.payload.data);
  default:
    return state;
  }

}
