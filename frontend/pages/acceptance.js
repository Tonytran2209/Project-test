import {poll} from './polling.js';
export function start(runtime) {
  return poll(runtime.loadAcceptance, 10000);
}
