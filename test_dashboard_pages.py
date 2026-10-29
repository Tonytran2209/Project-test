"""Route wiring tests without starting workers or loading service dependencies."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


class DashboardPagesTests(unittest.TestCase):
    def setUp(self):
        path = Path('backend/dashboard_pages.py')
        tree = ast.parse(path.read_text())
        tree.body = [node for node in tree.body if not isinstance(node, ast.ImportFrom)
                     or not node.module.startswith('fastapi')]
        self.routes = {}
        router = SimpleNamespace(add_api_route=lambda path, endpoint, **kw: self.routes.update({path:endpoint}))
        self.ns = {'__file__':str(path.resolve()), 'APIRouter':lambda:router,
                   'FileResponse':lambda path:Path(path),
                   'RedirectResponse':lambda url, status_code:SimpleNamespace(url=url,status_code=status_code)}
        exec(compile(tree, str(path), 'exec'), self.ns)

    def test_all_pages_open_same_shared_shell_on_direct_links_and_reload(self):
        for page in ('connect','acceptance','messages','replies','campaigns'):
            for suffix in ('','/'):
                result = self.routes[f'/dashboard/{page}{suffix}']()
                self.assertEqual(result, Path('frontend/index.html').resolve())
                self.assertTrue(result.is_file())

    def test_assets_are_not_shadowed_and_home_redirects(self):
        self.assertNotIn('/dashboard/{page}', self.routes)
        self.assertNotIn('/dashboard/app.js', self.routes)
        self.assertEqual(self.routes['/dashboard/']().url, '/dashboard/connect')
        source = Path('backend/main.py').read_text()
        self.assertLess(source.index('app.include_router(dashboard_pages_router)'), source.index('app.mount('))

    def test_assets_resolve_from_shared_base_and_router_precedes_runtime(self):
        html = Path('frontend/index.html').read_text()
        self.assertIn('<base href="/dashboard/"', html)
        self.assertLess(html.index('src="./workspace-router.js'), html.index('src="./app.js'))


if __name__ == '__main__':
    unittest.main()
