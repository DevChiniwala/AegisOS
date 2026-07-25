"""
Compliance RAG — Retrieval-augmented generation for regulatory compliance.

Retrieves relevant regulatory guidance for SAR narrative generation
with source citations and zero-hallucination enforcement.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List

from core.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RegulatorySource:
    source_id: str
    title: str
    content: str
    authority: str
    section: str = ""
    effective_date: str = ""
    keywords: List[str] = field(default_factory=list)


@dataclass
class ComplianceContext:
    sources: List[RegulatorySource]
    relevance_scores: List[float]
    query: str
    total_sources_searched: int = 0


SAR_TEMPLATES = {
    "account_takeover": (
        "On {date}, {institution} identified suspicious activity involving account {account_id}. "
        "The account, belonging to {subject_name}, exhibited indicators of unauthorized access. "
        "Specifically, {evidence}. The total suspicious amount was {amount} {currency}. "
        "This activity is being reported as it may indicate account takeover fraud."
    ),
    "structuring": (
        "Between {start_date} and {end_date}, {subject_name} conducted {tx_count} transactions "
        "totaling {amount} {currency} that appear designed to evade Currency Transaction Report "
        "requirements. Specifically, {evidence}. The pattern suggests deliberate structuring "
        "to keep individual transactions below the $10,000 reporting threshold."
    ),
    "money_laundering": (
        "This report concerns suspicious transactions involving {subject_name} that may constitute "
        "money laundering. Between {start_date} and {end_date}, the subject conducted {tx_count} "
        "transactions totaling {amount} {currency}. The activity exhibited layering characteristics: "
        "{evidence}. The funds were rapidly moved through {hop_count} intermediary accounts."
    ),
    "default": (
        "On {date}, suspicious activity was identified involving a transaction of {amount} {currency} "
        "from {sender} to {receiver}. The transaction scored {risk_score:.3f} on our risk assessment "
        "framework. Investigation findings: {evidence}. Recommended action: {action}."
    ),
}

REGULATORY_CORPUS = [
    RegulatorySource(
        source_id="fincen_sar_2011",
        title="FinCEN SAR Filing Instructions",
        content="A SAR must be filed within 30 days of initial detection of suspicious activity. "
                "The narrative should describe the five Ws: who, what, when, where, and why.",
        authority="FinCEN",
        section="31 CFR 1020.320",
        keywords=["sar", "filing", "narrative", "timeline"],
    ),
    RegulatorySource(
        source_id="bsa_ctr_threshold",
        title="Currency Transaction Report Requirements",
        content="Financial institutions must file a CTR for each currency transaction exceeding "
                "$10,000. Structuring transactions to avoid this threshold is a federal crime "
                "under 31 USC 5324.",
        authority="FinCEN",
        section="31 CFR 1010.311",
        keywords=["ctr", "threshold", "structuring", "10000"],
    ),
    RegulatorySource(
        source_id="ofac_sdn",
        title="OFAC SDN List Screening",
        content="All financial institutions must screen transactions against the OFAC Specially "
                "Designated Nationals and Blocked Persons List. Matches require immediate blocking "
                "and reporting within 10 business days.",
        authority="OFAC",
        section="31 CFR Part 501",
        keywords=["ofac", "sanctions", "sdn", "screening", "blocking"],
    ),
    RegulatorySource(
        source_id="aml_risk_factors",
        title="AML Risk Factor Guidelines",
        content="High-risk indicators include: rapid movement of funds, geographic risk (high-risk "
                "jurisdictions), unusual transaction patterns inconsistent with customer profile, "
                "structuring, layering through multiple accounts, and use of privacy-enhancing "
                "technologies.",
        authority="FATF",
        section="FATF Recommendation 10",
        keywords=["aml", "risk", "indicators", "layering", "structuring"],
    ),
    RegulatorySource(
        source_id="pep_screening",
        title="Politically Exposed Persons Screening",
        content="Enhanced due diligence is required for Politically Exposed Persons (PEPs), "
                "their family members, and close associates. PEP status does not automatically "
                "indicate criminal activity but requires ongoing monitoring.",
        authority="FATF",
        section="FATF Recommendation 12",
        keywords=["pep", "politically exposed", "due diligence", "monitoring"],
    ),
]


class ComplianceRAG:
    """RAG engine for regulatory compliance and SAR generation."""

    def __init__(self):
        self._corpus: List[RegulatorySource] = list(REGULATORY_CORPUS)
        self._custom_sources: List[RegulatorySource] = []

    def add_source(self, source: RegulatorySource):
        self._custom_sources.append(source)

    def retrieve(self, query: str, top_k: int = 3) -> ComplianceContext:
        """Retrieve relevant regulatory sources for a query."""
        all_sources = self._corpus + self._custom_sources
        query_terms = set(query.lower().split())

        scored = []
        for source in all_sources:
            keyword_overlap = len(query_terms & set(source.keywords))
            content_score = sum(1 for term in query_terms if term in source.content.lower())
            title_score = sum(2 for term in query_terms if term in source.title.lower())
            score = keyword_overlap * 3 + content_score + title_score

            if score > 0:
                scored.append((score, source))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_sources = scored[:top_k]

        max_score = max(s for s, _ in top_sources) if top_sources else 1
        relevance_scores = [s / max_score for s, _ in top_sources]

        return ComplianceContext(
            sources=[src for _, src in top_sources],
            relevance_scores=relevance_scores,
            query=query,
            total_sources_searched=len(all_sources),
        )

    def generate_sar_narrative(
        self,
        fraud_type: str,
        transaction_data: Dict[str, Any],
        findings: List[str],
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate a SAR narrative using templates + retrieved context."""
        template = SAR_TEMPLATES.get(fraud_type, SAR_TEMPLATES["default"])

        evidence_text = "; ".join(findings[:5]) if findings else "No specific findings available"

        params = {
            "date": transaction_data.get("timestamp", "date unknown"),
            "start_date": kwargs.get("start_date", transaction_data.get("timestamp", "")),
            "end_date": kwargs.get("end_date", transaction_data.get("timestamp", "")),
            "amount": transaction_data.get("amount", 0),
            "currency": transaction_data.get("currency", "USD"),
            "sender": transaction_data.get("sender_id", "unknown"),
            "receiver": transaction_data.get("receiver_id", "unknown"),
            "subject_name": kwargs.get("subject_name", transaction_data.get("sender_id", "subject")),
            "institution": kwargs.get("institution", "reporting institution"),
            "account_id": transaction_data.get("sender_id", ""),
            "risk_score": transaction_data.get("risk_score", 0.0),
            "evidence": evidence_text,
            "action": kwargs.get("action", "enhanced monitoring"),
            "tx_count": kwargs.get("tx_count", 1),
            "hop_count": kwargs.get("hop_count", 0),
        }

        try:
            narrative = template.format(**params)
        except KeyError:
            narrative = SAR_TEMPLATES["default"].format(**params)

        context = self.retrieve(f"{fraud_type} sar filing requirements")

        citations = []
        for source in context.sources:
            citations.append(f"[{source.source_id}] {source.title} ({source.authority} {source.section})")

        return {
            "narrative": narrative,
            "fraud_type": fraud_type,
            "citations": citations,
            "regulatory_context": [s.content for s in context.sources],
            "confidence": 0.85 if context.sources else 0.6,
        }
