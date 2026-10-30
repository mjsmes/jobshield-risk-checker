import sys
import unittest
from pathlib import Path

JOBSHIELD_APP_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "jobshield"
if str(JOBSHIELD_APP_DIR) not in sys.path:
    sys.path.insert(0, str(JOBSHIELD_APP_DIR))

from analysis_engine import MAX_TEXT_LENGTH, analyze_text  # noqa: E402, RUF100


class AnalyzeTextTests(unittest.TestCase):
    def test_detects_upfront_registration_fee(self):
        result = analyze_text("Pay a registration fee before your interview.")
        self.assertIn("upfront_payment", {item.key for item in result.findings})

    def test_does_not_flag_a_clear_no_fee_statement(self):
        result = analyze_text("There is no application fee to apply for this role.")
        self.assertNotIn("upfront_payment", {item.key for item in result.findings})

    def test_detects_guaranteed_high_earnings(self):
        result = analyze_text("Guaranteed high income with no experience required.")
        self.assertIn("guaranteed_earnings", {item.key for item in result.findings})

    def test_detects_high_pay_promised_per_week(self):
        result = analyze_text("Earn KSh 80,000 every week from home.")
        self.assertIn("guaranteed_earnings", {item.key for item in result.findings})

    def test_detects_immediate_pressure(self):
        result = analyze_text("Act now to reserve your position.")
        self.assertIn("urgency", {item.key for item in result.findings})

    def test_detects_pressure_with_a_deadline(self):
        result = analyze_text("Reply within 2 hours or lose the opportunity.")
        self.assertIn("urgency", {item.key for item in result.findings})

    def test_detects_request_for_password_and_otp(self):
        result = analyze_text("Send your password and OTP to the recruiter.")
        self.assertIn("credentials", {item.key for item in result.findings})

    def test_does_not_flag_advice_against_sharing_credentials(self):
        result = analyze_text("Never share your password or one-time code.")
        self.assertNotIn("credentials", {item.key for item in result.findings})

    def test_detects_whatsapp_only_contact(self):
        result = analyze_text("Contact us only on WhatsApp to proceed.")
        self.assertIn("suspicious_contact", {item.key for item in result.findings})

    def test_detects_personal_email_address(self):
        result = analyze_text("Send your CV to hiring.team@gmail.com")
        self.assertIn("suspicious_contact", {item.key for item in result.findings})

    def test_returns_exact_matched_evidence(self):
        phrase = "Pay a training fee"
        result = analyze_text(f"To continue, {phrase} before starting.")
        finding = next(item for item in result.findings if item.key == "upfront_payment")
        self.assertEqual(finding.evidence, phrase)

    def test_no_matching_signals_returns_zero_and_low_category(self):
        result = analyze_text(
            "The full-time role includes a written contract and a monthly salary."
        )
        self.assertEqual(result.score, 0)
        self.assertEqual(result.category, "Low")
        self.assertEqual(result.findings, ())

    def test_score_is_bounded_at_one_hundred(self):
        result = analyze_text(
            "Pay a registration fee. Guaranteed high income. Act now. "
            "Send your PIN. Contact us only on WhatsApp."
        )
        self.assertEqual(result.score, 100)
        self.assertLessEqual(result.score, 100)

    def test_multiple_signals_raise_the_category(self):
        result = analyze_text("Pay a training fee and send your OTP.")
        self.assertGreaterEqual(result.score, 45)
        self.assertIn(result.category, {"High", "Very high"})

    def test_rejects_blank_text(self):
        with self.assertRaises(ValueError):
            analyze_text(" \n\t ")

    def test_rejects_non_string_input(self):
        with self.assertRaises(TypeError):
            analyze_text(None)

    def test_rejects_text_over_the_size_limit(self):
        with self.assertRaises(ValueError):
            analyze_text("a" * (MAX_TEXT_LENGTH + 1))


if __name__ == "__main__":
    unittest.main()
