from .behavior_analyst import BehaviorAnalyst
from .compliance_officer import ComplianceOfficer
from .entity_resolver import EntityResolverAgent
from .evidence_collector import EvidenceCollector
from .graph_detective import GraphDetective
from .narrative_generator import NarrativeGeneratorAgent
from .planner import PlannerAgent
from .recommendation_agent import RecommendationAgent
from .reflector import ReflectorAgent
from .root_cause_agent import RootCauseAgent
from .timeline_reconstructor import TimelineReconstructorAgent
from .transaction_investigator import TransactionInvestigator

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
