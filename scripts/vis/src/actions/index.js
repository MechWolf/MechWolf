import axios from 'axios';

export const FETCH_EXPERIMENT_LIST = 'FETCH_EXPERIMENT_LIST'
export const FETCH_CURRENT_PROTOCOL = 'FETCH_PROTOCOL'
export const FETCH_CURRENT_APPARATUS = 'FETCH_APPARATUS'
export const FETCH_EXPERIMENT = 'FETCH_EXPERIMENT'
export const LOG_RECEIVED = 'LOG_RECEIVED'
export const DATA_RECEIVED = 'DATA_RECEIVED'

const BASE_URL = "http://localhost:5000"

export function fetchCurrentProtocol() {
  const url = "http://localhost:5000/experiments/8edbcab8-cd9b-11e8-8250-7cd1c3dd68bf";
  const request = axios.get(url);
  return (
  { type: FETCH_CURRENT_PROTOCOL,
    payload: request}
  );
}

export function fetchExperimentList() {
  const url = "http://localhost:5000/experiments";
  const request = axios.get(url);
  return (
    { type: FETCH_EXPERIMENT_LIST,
      payload: request }
  );
}

export function fetchExperiment(id) {
  const url = `${BASE_URL}/experiments/${id}`;
  const request = axios.get(url);

  return {
    type: FETCH_EXPERIMENT,
    payload: request
  };
}

export function logReceived(log) {
  return {
    type: LOG_RECEIVED,
    payload: log
  };
}

export function dataReceived(data) {
  return {
    type: DATA_RECEIVED,
    payload: data
  };
}
