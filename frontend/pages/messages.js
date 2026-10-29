import {poll} from './polling.js';
export function start(runtime) {
  return poll(runtime.loadMessages, 15000);
}
