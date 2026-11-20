import unittest

from analysis_engine import MAX_TEXT_LENGTH, analyze_text


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

    def test_detects_equipment_purchase_supplier(self):
        examples = (
            "Buy a laptop from our approved supplier before starting.",
            "Purchase your work equipment through our designated vendor.",
        )
        for advert in examples:
            with self.subTest(advert=advert):
                result = analyze_text(advert)
                self.assertIn(
                    "equipment_purchase",
                    {item.key for item in result.findings},
                )

    def test_does_not_flag_employer_provided_equipment(self):
        examples = (
            "The company provides a free laptop for this role.",
            "All work equipment is supplied by the employer.",
        )
        for advert in examples:
            with self.subTest(advert=advert):
                result = analyze_text(advert)
                self.assertNotIn(
                    "equipment_purchase",
                    {item.key for item in result.findings},
                )

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


    def test_detects_fee_after_an_initial_no_fee_statement(self):
        result = analyze_text(
            "Applicants pay no fee. Successful candidates must pay a registration fee."
        )
        self.assertIn("upfront_payment", {item.key for item in result.findings})

    def test_detects_password_request_after_a_denial(self):
        result = analyze_text(
            "We never ask for passwords. Send your password to complete registration."
        )
        self.assertIn("credentials", {item.key for item in result.findings})

    def test_does_not_flag_employer_provided_free_laptop(self):
        result = analyze_text("The company provides a free laptop.")
        self.assertNotIn("equipment_purchase", {item.key for item in result.findings})

    def test_detects_laptop_purchase_from_approved_supplier(self):
        result = analyze_text(
            "Buy your laptop from our approved supplier before training."
        )
        self.assertIn("equipment_purchase", {item.key for item in result.findings})

    def test_does_not_flag_optional_whatsapp_contact(self):
        result = analyze_text(
            "WhatsApp is available, but applicants may also contact our official office."
        )
        self.assertNotIn("suspicious_contact", {item.key for item in result.findings})



if __name__ == "__main__":
    unittest.main()
