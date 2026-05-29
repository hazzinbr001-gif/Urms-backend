import logging
from typing import Dict, Any, List
from dataclasses import dataclass, field
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class ScoreCategory:
    name: str
    score: int
    max_score: int = 100
    feedback: str = ""

@dataclass
class ProposalScore:
    total_score: int
    categories: List[ScoreCategory] = field(default_factory=list)
    recommendation: str = "PENDING"
    confidence_score: Decimal = Decimal('0.00')

@dataclass
class ProposalCritique:
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    overall_summary: str = ""

class AIEngineService:
    """
    Service layer for AI-driven proposal analysis.
    Currently implements mock behaviors for development and testing.
    """

    @classmethod
    def score_proposal(cls, proposal_id: int) -> ProposalScore:
        """
        Mock implementation of proposal scoring.
        In a production environment, this would interface with an ML model or external AI API.

        Args:
            proposal_id (int): The ID of the proposal to score.

        Returns:
            ProposalScore: A structured object containing the scoring details.
        """
        logger.info(f"Initiating mock AI scoring for proposal ID: {proposal_id}")

        # Mocking a response
        categories = [
            ScoreCategory(name="Innovation", score=85, feedback="Strong novel approach."),
            ScoreCategory(name="Feasibility", score=70, feedback="Timeline is slightly aggressive."),
            ScoreCategory(name="Methodology", score=90, feedback="Rigorous and well-defined.")
        ]

        result = ProposalScore(
            total_score=82,
            categories=categories,
            recommendation="APPROVE_WITH_MINOR_REVISIONS",
            confidence_score=Decimal('0.92')
        )

        logger.debug(f"Mock scoring complete for proposal ID: {proposal_id}. Score: {result.total_score}")
        return result

    @classmethod
    def critique_proposal(cls, proposal_id: int) -> ProposalCritique:
        """
        Mock implementation of proposal critiquing.
        Generates qualitative feedback on the proposal structure and content.

        Args:
            proposal_id (int): The ID of the proposal to critique.

        Returns:
            ProposalCritique: A structured object containing the critique details.
        """
        logger.info(f"Initiating mock AI critique for proposal ID: {proposal_id}")

        # Mocking a response
        result = ProposalCritique(
            strengths=[
                "Clear problem statement.",
                "Comprehensive literature review."
            ],
            weaknesses=[
                "Budget justification lacks detail in equipment section."
            ],
            improvement_suggestions=[
                "Provide a more detailed breakdown of the equipment costs.",
                "Consider expanding the risk mitigation strategy."
            ],
            overall_summary="The proposal is fundamentally sound but requires some financial clarifications before final approval."
        )

        logger.debug(f"Mock critique complete for proposal ID: {proposal_id}.")
        return result
