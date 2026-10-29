import {poll} from './polling.js';
export function start(runtime) {
  void runtime.loadReplies();
  const stopRevision = poll(runtime.pollReplyRevision, 30000, {immediate: false});
  const stopScan = poll(runtime.pollReplyScan, 5000);
  return () => { stopRevision(); stopScan(); };
}
