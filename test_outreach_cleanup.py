"""Read-only regression checks for removing the retired scanner/research tool."""
import ast
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent


class OutreachCleanupTest(unittest.TestCase):
    def test_only_current_dashboard_panels_remain(self):
        html = (ROOT / "frontend/index.html").read_text()
        self.assertEqual(set(re.findall(r'<section id="tab-([^"]+)"', html)),
                         {"outreach", "replies", "campaigns"})
        for asset in re.findall(r'(?:src|href)="\./([^"?]+)', html):
            self.assertTrue((ROOT / "frontend" / asset).is_file(), asset)

    def test_api_keeps_outreach_and_health_not_retired_routes(self):
        tree = ast.parse((ROOT / "backend/main.py").read_text())
        routes = set()
        for node in tree.body:
            for decorator in getattr(node, "decorator_list", []):
                if isinstance(decorator, ast.Call) and decorator.args:
                    arg = decorator.args[0]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        routes.add(arg.value)
        self.assertIn("/health", routes)
        for route in ["connect/jobs", "accepted-pool", "messages/batches",
                      "replies", "sessions/check", "campaigns/performance"]:
            self.assertIn("/api/outreach/" + route, routes)
        self.assertTrue(all(r in {"/", "/health"} or r.startswith("/api/outreach/")
                            for r in routes))

    def test_no_duplicate_source_tree_but_reply_services_survive(self):
        self.assertEqual(list((ROOT / "git-meta/app").glob("*.py")), [])
        self.assertEqual(list((ROOT / "git-meta/frontend").glob("*.js")), [])
        for name in ["reply_check_schedule_service.sh", "reply_send_workers_service.sh"]:
            source = (ROOT / "git-meta" / name).read_text()
            self.assertIn('$(dirname "$0")/..', source)
            self.assertIn("outreach_reply_", source)

    def test_retired_frontend_and_dependencies_are_gone(self):
        js = (ROOT / "frontend/app.js").read_text()
        self.assertNotRegex(js, r"youtube|Youtube|linkedin_sources|linkedin_profile_snapshots|sendWorkerCommand")
        requirements = (ROOT / "requirements.txt").read_text()
        self.assertNotRegex(requirements, r"google-api-python-client|google-auth|requests>=")
        self.assertFalse((ROOT / "app/lark_client.py").exists())


if __name__ == "__main__":
    unittest.main()
