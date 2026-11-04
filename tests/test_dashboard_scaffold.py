import asyncio
import subprocess
import unittest
from pathlib import Path

from httpx import ASGITransport, AsyncClient

from agentic_os.api import FEATURES, app

ROOT = Path(__file__).resolve().parents[1]


class DashboardScaffoldTests(unittest.TestCase):
    def request(self, method, path):
        async def send():
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                return await client.request(method, path)

        return asyncio.run(send())

    def test_dashboard_is_served(self):
        response = self.request("GET", "/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("GOD AI OS", response.text)
        self.assertIn('src="./app.js"', response.text)
        self.assertEqual(self.request("GET", "/styles.css").status_code, 200)
        self.assertEqual(self.request("GET", "/pages/goals.js").status_code, 200)

    def test_health_and_existing_prototype_api(self):
        health = self.request("GET", "/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json()["status"], "ok")

        dashboard = self.request("GET", "/api/dashboard")
        self.assertEqual(dashboard.status_code, 200)
        self.assertEqual(dashboard.json()["agents"][0]["agent_id"], "father")

        prototype = self.request("GET", "/prototype/")
        self.assertEqual(prototype.status_code, 200)
        self.assertIn("Agentic OS", prototype.text)

    def test_all_feature_routes_are_explicitly_scaffolded(self):
        response = self.request("GET", "/api/features")
        self.assertEqual(response.status_code, 200)
        features = response.json()["features"]
        self.assertEqual(len(features), 22)
        self.assertEqual(features[0]["status"], "prototype")
        self.assertTrue(
            all(item["status"] == "not_implemented" for item in features[1:])
        )

        for feature_id in FEATURES:
            page = self.request("GET", f"/api/features/{feature_id}")
            self.assertEqual(page.status_code, 200, feature_id)
        unknown = self.request("GET", "/api/features/not-a-feature")
        self.assertEqual(unknown.status_code, 404)

    def test_every_feature_has_a_page_module(self):
        page_modules = {
            path.stem for path in (ROOT / "dashboard" / "pages").glob("*.js")
        }
        self.assertEqual(page_modules, set(FEATURES))

    def test_backup_scripts_fail_explicitly_without_changing_data(self):
        for script, action in (("backup.sh", "Backup"), ("restore.sh", "Restore")):
            result = subprocess.run(
                ["sh", str(ROOT / script)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(f"{action} is not implemented", result.stderr)


if __name__ == "__main__":
    unittest.main()
