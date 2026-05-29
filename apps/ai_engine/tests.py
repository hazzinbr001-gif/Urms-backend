from django.test import TestCase
from .services import AIEngineService

class AIEngineServiceTest(TestCase):
    def test_score_proposal(self):
        score = AIEngineService.score_proposal(1)
        self.assertIsNotNone(score)
        self.assertEqual(score.total_score, 82)
        self.assertEqual(len(score.categories), 3)

    def test_critique_proposal(self):
        critique = AIEngineService.critique_proposal(1)
        self.assertIsNotNone(critique)
        self.assertGreater(len(critique.strengths), 0)
        self.assertGreater(len(critique.weaknesses), 0)
