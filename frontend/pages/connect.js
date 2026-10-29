import {poll} from './polling.js';
export function start(runtime) {
  void runtime.loadConnectCampaigns();
  return poll(runtime.loadConnect, runtime.connectPollInterval);
}
