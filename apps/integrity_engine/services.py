import logging
from typing import List, Optional
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum

logger = logging.getLogger(__name__)

class IntegrityStatus(str, Enum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"
    ERROR = "ERROR"

@dataclass
class MatchSource:
    url_or_document: str
    match_percentage: Decimal
    matched_text_snippet: str

@dataclass
class PlagiarismReport:
    overall_similarity_score: Decimal
    status: IntegrityStatus
    matched_sources: List[MatchSource] = field(default_factory=list)
    scan_id: str = "mock-scan-id"
    details: str = ""

@dataclass
class AIContentReport:
    ai_probability_score: Decimal
    status: IntegrityStatus
    flagged_sections: List[str] = field(default_factory=list)
    details: str = ""

class IntegrityService:
    """
    Service layer for enforcing academic and proposal integrity.
    Currently implements mock behaviors for plagiarism and AI content detection.
    """

    @classmethod
    def check_plagiarism(cls, proposal_id: int, content_text: Optional[str] = None) -> PlagiarismReport:
        """
        Mock implementation of plagiarism checking.
        In a production environment, this would interface with a service like Turnitin or Copyscape.

        Args:
            proposal_id (int): The ID of the proposal.
            content_text (Optional[str]): Optional raw text to scan.

        Returns:
            PlagiarismReport: A structured report containing similarity metrics.
        """
        logger.info(f"Initiating mock plagiarism check for proposal ID: {proposal_id}")

        # Mocking a response
        sources = [
            MatchSource(
                url_or_document="https://example.com/research-paper-1",
                match_percentage=Decimal('5.2'),
                matched_text_snippet="...the fundamental approach to distributed ledger technology..."
            ),
             MatchSource(
                url_or_document="Internal Database - Proposal #4421",
                match_percentage=Decimal('2.1'),
                matched_text_snippet="...in conclusion, the results demonstrate a significant..."
            )
        ]

        overall_score = Decimal('7.3')

        # Simple threshold logic for mock status
        if overall_score < Decimal('15.0'):
            status = IntegrityStatus.PASS
        elif overall_score < Decimal('30.0'):
            status = IntegrityStatus.WARNING
        else:
            status = IntegrityStatus.FAIL

        result = PlagiarismReport(
            overall_similarity_score=overall_score,
            status=status,
            matched_sources=sources,
            details="Acceptable level of similarity detected. Mostly common phrasing."
        )

        logger.debug(f"Mock plagiarism check complete for proposal ID: {proposal_id}. Score: {result.overall_similarity_score}%")
        return result

    @classmethod
    def detect_ai_content(cls, proposal_id: int, content_text: Optional[str] = None) -> AIContentReport:
        """
        Mock implementation of AI-generated content detection.

        Args:
            proposal_id (int): The ID of the proposal.
            content_text (Optional[str]): Optional raw text to scan.

        Returns:
            AIContentReport: A structured report indicating the probability of AI generation.
        """
        logger.info(f"Initiating mock AI content detection for proposal ID: {proposal_id}")

        # Mocking a response
        probability_score = Decimal('12.5')

        # Simple threshold logic for mock status
        if probability_score < Decimal('20.0'):
            status = IntegrityStatus.PASS
        elif probability_score < Decimal('40.0'):
            status = IntegrityStatus.WARNING
        else:
            status = IntegrityStatus.FAIL

        result = AIContentReport(
            ai_probability_score=probability_score,
            status=status,
            flagged_sections=[
                "Introduction paragraph 2 shows minor indicators of generative AI patterns."
            ] if status != IntegrityStatus.PASS else [],
            details="Low probability of AI generation detected."
        )

        logger.debug(f"Mock AI content detection complete for proposal ID: {proposal_id}. Probability: {result.ai_probability_score}%")
        return result
