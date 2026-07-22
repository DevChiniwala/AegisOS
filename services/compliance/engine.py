"""
Compliance Engine.
"""
from dataclasses import dataclass
from typing import List
from core.schemas.transaction import TransactionCreate
from core.schemas.entity import UserProfile
from core.schemas.investigation import InvestigationCase, CaseStatus, CasePriority

@dataclass
class ComplianceResult:
    is_compliant: bool
    flags: List[str]

@dataclass
class SanctionsResult:
    is_sanctioned: bool
    match_score: float
    details: str

@dataclass
class PEPResult:
    is_pep: bool
    role: str

class ComplianceEngine:
    def check_aml(self, transaction: TransactionCreate, user: UserProfile) -> ComplianceResult:
        flags = []
        if transaction.amount > 10000:
            flags.append("CTR_THRESHOLD_EXCEEDED")
        # Check aggregation logic
        if not flags:
            return ComplianceResult(is_compliant=True, flags=[])
        return ComplianceResult(is_compliant=False, flags=flags)

    def screen_sanctions(self, entity_name: str, entity_country: str) -> SanctionsResult:
        # Mock screening
        bad_entities = {"Evil Corp", "Sanctioned Entity LLC"}
        if entity_name in bad_entities:
            return SanctionsResult(is_sanctioned=True, match_score=1.0, details="Exact match on OFAC list")
        return SanctionsResult(is_sanctioned=False, match_score=0.0, details="No match")

    def check_pep(self, entity_name: str) -> PEPResult:
        peps = {"Politician A", "Minister B"}
        if entity_name in peps:
            return PEPResult(is_pep=True, role="Government Official")
        return PEPResult(is_pep=False, role="")

    def should_file_sar(self, case: InvestigationCase) -> bool:
        return case.priority == CasePriority.HIGH and case.status == CaseStatus.CLOSED and case.verdict == "FRAUD"

    def generate_sar_report(self, case: InvestigationCase) -> str:
        return f"Suspicious Activity Report for Case {case.case_id}\nPriority: {case.priority}\nDetails: Found suspicious behavior."

    def get_regulatory_requirements(self, transaction: TransactionCreate) -> List[str]:
        reqs = ["KYC", "AML"]
        if getattr(transaction, "currency", "USD") == "EUR":
            reqs.append("GDPR")
            reqs.append("PSD2")
        return reqs
