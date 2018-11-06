import axios from 'axios';
import apparatus_request from './apparatus_request';
import protocol_request from './protocol_request';


export const FETCH_CURRENT_PROTOCOL = 'FETCH_PROTOCOL'
export const FETCH_CURRENT_APPARATUS = 'FETCH_APPARATUS'

export function fetchCurrentProtocol() {
  const url = "http://localhost:5000/experiments/8edbcab8-cd9b-11e8-8250-7cd1c3dd68bf";
  const request = axios.get(url);
  return (
  { type: FETCH_CURRENT_PROTOCOL,
    payload: request}
  );
}

export function fetchCurrentApparatus() {
  return (
  { type: FETCH_CURRENT_APPARATUS,
    payload: apparatus_request()}
  );
}
