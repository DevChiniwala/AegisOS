"""
Financial Domain Ontology — Formal entity model for AegisOS.

Defines the core entity types, relationship types, and lifecycle states
for the fraud intelligence knowledge graph.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class EntityType(str, Enum):
    PERSON = "person"
    ACCOUNT = "account"
    COMPANY = "company"
    TRANSACTION = "transaction"
    DEVICE = "device"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    PHONE = "phone"
    ALERT = "alert"
    INVESTIGATION = "investigation"


class RelationshipType(str, Enum):
    OWNS = "owns"
    SENDS_TO = "sends_to"
    RECEIVES_FROM = "receives_from"
    USES_DEVICE = "uses_device"
    LOGGED_FROM_IP = "logged_from_ip"
    HAS_EMAIL = "has_email"
    HAS_PHONE = "has_phone"
    EMPLOYED_BY = "employed_by"
    RELATED_TO = "related_to"
    SHARES_DEVICE = "shares_device"
    SHARES_IP = "shares_ip"
    CO_TRANSACTED = "co_transacted"
    INVESTIGATED_FOR = "investigated_for"
    TRIGGERED = "triggered"
    PART_OF_RING = "part_of_ring"


class EntityLifecycle(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    CLOSED = "closed"
    UNDER_REVIEW = "under_review"
    FLAGGED = "flagged"


class RiskTier(str, Enum):
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class OntologyEntity:
    entity_id: str
    entity_type: EntityType
    lifecycle: EntityLifecycle = EntityLifecycle.ACTIVE
    risk_tier: RiskTier = RiskTier.LOW
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class OntologyRelationship:
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: Optional[datetime] = None


RELATIONSHIP_CONSTRAINTS = {
    RelationshipType.OWNS: {
        "source_types": [EntityType.PERSON, EntityType.COMPANY],
        "target_types": [EntityType.ACCOUNT],
        "cardinality": "one_to_many",
    },
    RelationshipType.SENDS_TO: {
        "source_types": [EntityType.ACCOUNT],
        "target_types": [EntityType.ACCOUNT],
        "cardinality": "many_to_many",
    },
    RelationshipType.USES_DEVICE: {
        "source_types": [EntityType.PERSON],
        "target_types": [EntityType.DEVICE],
        "cardinality": "many_to_many",
    },
    RelationshipType.LOGGED_FROM_IP: {
        "source_types": [EntityType.PERSON, EntityType.DEVICE],
        "target_types": [EntityType.IP_ADDRESS],
        "cardinality": "many_to_many",
    },
    RelationshipType.HAS_EMAIL: {
        "source_types": [EntityType.PERSON, EntityType.COMPANY],
        "target_types": [EntityType.EMAIL],
        "cardinality": "one_to_many",
    },
    RelationshipType.EMPLOYED_BY: {
        "source_types": [EntityType.PERSON],
        "target_types": [EntityType.COMPANY],
        "cardinality": "many_to_one",
    },
    RelationshipType.SHARES_DEVICE: {
        "source_types": [EntityType.PERSON],
        "target_types": [EntityType.PERSON],
        "cardinality": "many_to_many",
    },
    RelationshipType.PART_OF_RING: {
        "source_types": [EntityType.PERSON, EntityType.ACCOUNT],
        "target_types": [EntityType.PERSON, EntityType.ACCOUNT],
        "cardinality": "many_to_many",
    },
}


def validate_relationship(source: OntologyEntity, target: OntologyEntity, rel_type: RelationshipType) -> bool:
    """Validate that a relationship type is valid between two entity types."""
    constraints = RELATIONSHIP_CONSTRAINTS.get(rel_type)
    if not constraints:
        return True

    source_valid = source.entity_type in constraints["source_types"]
    target_valid = target.entity_type in constraints["target_types"]
    return source_valid and target_valid
