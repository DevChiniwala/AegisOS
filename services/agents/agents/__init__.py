from .transaction_investigator import TransactionInvestigator
from .graph_detective import GraphDetective
from .behavior_analyst import BehaviorAnalyst
from .compliance_officer import ComplianceOfficer
from .evidence_collector import EvidenceCollector
from .planner import PlannerAgent
from .entity_resolver import EntityResolverAgent
from .timeline_reconstructor import TimelineReconstructorAgent
from .narrative_generator import NarrativeGeneratorAgent
from .root_cause_agent import RootCauseAgent
from .recommendation_agent import RecommendationAgent
from .reflector import ReflectorAgent

ALL_AGENTS = [
    TransactionInvestigator,
    GraphDetective,
    BehaviorAnalyst,
    ComplianceOfficer,
    EvidenceCollector,
    PlannerAgent,
    EntityResolverAgent,
    TimelineReconstructorAgent,
    NarrativeGeneratorAgent,
    RootCauseAgent,
    RecommendationAgent,
    ReflectorAgent,
]
