from django.test import TestCase
from .services import IntegrityService, IntegrityStatus
from decimal import Decimal

class IntegrityServiceTest(TestCase):
    def test_check_plagiarism(self):
        report = IntegrityService.check_plagiarism(1)
        self.assertIsNotNone(report)
        self.assertEqual(report.status, IntegrityStatus.PASS)
        self.assertEqual(report.overall_similarity_score, Decimal('7.3'))
        self.assertEqual(len(report.matched_sources), 2)

    def test_detect_ai_content(self):
        report = IntegrityService.detect_ai_content(1)
        self.assertIsNotNone(report)
        self.assertEqual(report.status, IntegrityStatus.PASS)
        self.assertEqual(report.ai_probability_score, Decimal('12.5'))
