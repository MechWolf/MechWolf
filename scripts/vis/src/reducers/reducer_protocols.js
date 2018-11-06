import { FETCH_CURRENT_PROTOCOL } from '../actions/index'

export default function (state = {}, action) {
  switch (action.type) {
  case FETCH_CURRENT_PROTOCOL:
    return(action.payload.data);
  default:
    return state;
  }

}
