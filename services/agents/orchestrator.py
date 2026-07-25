import asyncio
import uuid
from typing import Union

from core.schemas.investigation import CasePriority, CaseStatus, InvestigationCase, TimelineEvent
from core.schemas.risk import RiskExplanation
from core.schemas.transaction import TransactionCreate
from services.risk_engine.engine import ScoringResult

from .agents.behavior_analyst import BehaviorAnalyst
from .agents.compliance_officer import ComplianceOfficer
from .agents.decision_agent import DecisionAgent
from .agents.evidence_collector import EvidenceCollector
from .agents.graph_detective import GraphDetective
from .agents.report_generator import ReportGenerator
from .agents.risk_assessor import RiskAssessor
from .agents.supervisor import SupervisorAgent
from .agents.transaction_investigator import TransactionInvestigator
from .base import InvestigationContext


class InvestigationOrchestrator:
    def __init__(self):
        self.agents = {
            'tx_investigator': TransactionInvestigator(),
            'behavior_analyst': BehaviorAnalyst(),
            'graph_detective': GraphDetective(),
            'evidence_collector': EvidenceCollector(),
            'risk_assessor': RiskAssessor(),
            'compliance_officer': ComplianceOfficer(),
            'decision_agent': DecisionAgent(),
            'supervisor': SupervisorAgent(),
            'report_generator': ReportGenerator()
        }

    async def run_investigation(self, transaction: TransactionCreate, risk_result: Union[ScoringResult, RiskExplanation]) -> InvestigationCase:
        score = risk_result.score if isinstance(risk_result, ScoringResult) else getattr(risk_result, 'risk_score', 0.0)
        case = InvestigationCase(
            case_id=f"CASE-{uuid.uuid4().hex[:8].upper()}",
            transaction_id=transaction.transaction_id or "",
            status=CaseStatus.OPEN,
            priority=CasePriority.HIGH if score > 0.8 else CasePriority.MEDIUM
        )

        context = InvestigationContext(
            case=case,
            transaction=transaction,
            features={},
            risk_score=score
        )
        
        case.timeline.append(TimelineEvent(event_type="ALERT", description="Investigation started"))

        # Step 1: Parallel initial investigation
        case.timeline.append(TimelineEvent(event_type="TRIAGE", description="Running initial analysis"))
        triage_tasks = [
            self.agents['tx_investigator'].investigate(context),
            self.agents['behavior_analyst'].investigate(context)
        ]
        triage_findings = await asyncio.gather(*triage_tasks)
        context.previous_findings.extend(triage_findings)
        case.findings.extend(triage_findings)

        # Step 2: Graph Detective
        case.timeline.append(TimelineEvent(event_type="INVESTIGATE", description="Running graph analysis"))
        graph_finding = await self.agents['graph_detective'].investigate(context)
        context.previous_findings.append(graph_finding)
        case.findings.append(graph_finding)

        # Step 3: Evidence Collection
        case.timeline.append(TimelineEvent(event_type="EVIDENCE", description="Collecting evidence"))
        evidence_finding = await self.agents['evidence_collector'].investigate(context)
        context.previous_findings.append(evidence_finding)
        
        # Step 4: Risk Assessment
        risk_finding = await self.agents['risk_assessor'].investigate(context)
        context.previous_findings.append(risk_finding)
        
        # Step 5: Compliance
        compliance_finding = await self.agents['compliance_officer'].investigate(context)
        context.previous_findings.append(compliance_finding)

        # Step 6: Decision
        case.timeline.append(TimelineEvent(event_type="DECIDE", description="Making automated decision"))
        decision_finding = await self.agents['decision_agent'].investigate(context)
        context.previous_findings.append(decision_finding)

        # Step 7: Supervisor Quality Check
        await self.agents['supervisor'].investigate(context)
        
        # Step 8: Report Generation
        case.timeline.append(TimelineEvent(event_type="REPORT", description="Generating investigation report"))
        report_finding = await self.agents['report_generator'].investigate(context)
        case.summary = report_finding.description
        
        case.status = CaseStatus.CLOSED
        case.timeline.append(TimelineEvent(event_type="CLOSED", description="Investigation completed"))
        
        return case
