import sys
import unittest
from pathlib import Path

JOBSHIELD_APP_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "jobshield"
if str(JOBSHIELD_APP_DIR) not in sys.path:
    sys.path.insert(0, str(JOBSHIELD_APP_DIR))

from app import app  # noqa: E402, RUF100


class JobShieldRouteTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Check Job Advert", response.data)

    def test_checker_renders_a_risk_result(self):
        response = self.client.post(
            "/check",
            data={"job_text": "Pay a registration fee before your interview."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"35", response.data)
        self.assertIn(b"An upfront payment is requested", response.data)

    def test_checker_rejects_blank_input(self):
        response = self.client.post("/check", data={"job_text": "  "})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Paste a job advert", response.data)

    def test_checker_rejects_oversized_text(self):
        response = self.client.post("/check", data={"job_text": "x" * 12_001})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"12,000 characters", response.data)

    def test_user_text_is_html_escaped(self):
        payload = "Please send <script>alert(1)</script> your password."
        response = self.client.post("/check", data={"job_text": payload})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"&lt;script&gt;alert(1)&lt;/script&gt;", response.data)
        self.assertNotIn(b"<script>alert(1)</script>", response.data)

    def test_results_are_not_cached(self):
        response = self.client.post(
            "/check", data={"job_text": "A standard office administrator role."}
        )
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_security_headers_are_present(self):
        response = self.client.get("/")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])


if __name__ == "__main__":
    unittest.main()
