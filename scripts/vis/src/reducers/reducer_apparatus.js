import { FETCH_CURRENT_APPARATUS } from '../actions/index'

export default function (state = null, action) {
  switch (action.type) {
  case FETCH_CURRENT_APPARATUS:
    return(action.payload);
  default:
    return state;
  }

}
