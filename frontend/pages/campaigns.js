import {poll} from './polling.js';
export function start(runtime) {
  return poll(runtime.loadCampaigns, 30000);
}
