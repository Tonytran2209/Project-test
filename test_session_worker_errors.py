import asyncio
import importlib.util
from pathlib import Path
import sys
import unittest
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch


def load_worker():
    modules = {}
    for name, attributes in {
        "supabase": {"AsyncClient": object, "acreate_client": AsyncMock()},
        "app.linkedin_session_checker": {"check_outreach_account_session": MagicMock()},
        "app.outreach_account_pool": {"OutreachAccountPool": object},
        "app.outreach_session_status": {"SESSION_TABLE": "outreach_account_sessions"},
        "app.settings": {"load_settings": MagicMock()},
    }.items():
        module = ModuleType(name)
        module.__dict__.update(attributes)
        modules[name] = module
    spec = importlib.util.spec_from_file_location(
        "session_worker_under_test", Path(__file__).with_name("outreach_session_worker.py")
    )
    worker = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(worker)
    return worker


class SessionWorkerErrorsTest(unittest.IsolatedAsyncioTestCase):
    async def test_unknown_account_is_reported_without_crashing(self):
        worker = load_worker()
        pool = MagicMock()
        pool.get_account.side_effect = KeyError("outreach_account_06")
        with patch.object(worker, "claim_session_check", AsyncMock(return_value=True)), patch.object(
            worker, "fail_session_check", AsyncMock()
        ) as failed, patch.object(worker, "logger"):
            await worker.process_account(object(), pool, "outreach_account_06")
        failed.assert_awaited_once()
        self.assertIn("OUTREACH_ACCOUNT_IDS", str(failed.call_args.kwargs["error"]))
        worker.check_outreach_account_session.assert_not_called()

    async def test_failed_request_does_not_prevent_next_account(self):
        worker = load_worker()
        worker._work_queue = asyncio.Queue()
        for account_id in ("outreach_account_06", "outreach_account_07"):
            worker._work_queue.put_nowait(account_id)
        with patch.object(worker, "process_account", AsyncMock(side_effect=[RuntimeError("request failed"), None])) as process, patch.object(worker, "logger"):
            task = asyncio.create_task(worker.worker_loop(object(), object()))
            try:
                await asyncio.wait_for(worker._work_queue.join(), timeout=1)
                self.assertEqual(process.await_count, 2)
                self.assertEqual(process.await_args_list[-1].args[-1], "outreach_account_07")
            finally:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task


if __name__ == "__main__":
    unittest.main()
