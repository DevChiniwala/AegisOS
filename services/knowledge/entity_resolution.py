"""
Entity Resolution Engine — Links identities across multiple dimensions.

Resolves entities using:
- Fuzzy name matching (Levenshtein, Jaro-Winkler)
- Device/IP/email linking
- Confidence-scored entity merge suggestions
- Graph-based entity clustering
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

from core.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EntityLink:
    source_id: str
    target_id: str
    link_type: str
    confidence: float
    evidence: List[str] = field(default_factory=list)


@dataclass
class ResolvedEntity:
    canonical_id: str
    aliases: List[str] = field(default_factory=list)
    linked_accounts: List[str] = field(default_factory=list)
    linked_devices: List[str] = field(default_factory=list)
    linked_ips: List[str] = field(default_factory=list)
    linked_emails: List[str] = field(default_factory=list)
    confidence: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)


class EntityResolutionEngine:
    """Resolves and links entities across identity dimensions."""

    def __init__(self, threshold: float = 0.7):
        self._threshold = threshold
        self._entities: Dict[str, ResolvedEntity] = {}
        self._links: List[EntityLink] = []

    def resolve(self, entity_id: str, attributes: Dict[str, Any]) -> ResolvedEntity:
        """Resolve an entity against known entities."""
        if entity_id in self._entities:
            return self._entities[entity_id]

        candidates = self._find_candidates(entity_id, attributes)

        if candidates:
            best_match, confidence = candidates[0]
            if confidence >= self._threshold:
                existing = self._entities[best_match]
                existing.aliases.append(entity_id)
                self._links.append(EntityLink(
                    source_id=entity_id,
                    target_id=best_match,
                    link_type="identity_match",
                    confidence=confidence,
                    evidence=[f"Matched via attributes (confidence={confidence:.3f})"],
                ))
                return existing

        resolved = ResolvedEntity(
            canonical_id=entity_id,
            confidence=1.0,
            properties=attributes,
        )

        if "device_id" in attributes:
            resolved.linked_devices.append(attributes["device_id"])
        if "ip_address" in attributes:
            resolved.linked_ips.append(attributes["ip_address"])
        if "email" in attributes:
            resolved.linked_emails.append(attributes["email"])

        self._entities[entity_id] = resolved
        return resolved

    def find_links(self, entity_id: str) -> List[EntityLink]:
        """Find all links for an entity."""
        return [link for link in self._links if link.source_id == entity_id or link.target_id == entity_id]

    def link_by_device(self, device_id: str) -> List[str]:
        """Find all entities sharing a device."""
        return [
            eid for eid, entity in self._entities.items()
            if device_id in entity.linked_devices
        ]

    def link_by_ip(self, ip_address: str) -> List[str]:
        """Find all entities sharing an IP address."""
        return [
            eid for eid, entity in self._entities.items()
            if ip_address in entity.linked_ips
        ]

    def link_by_email_domain(self, email: str) -> List[str]:
        """Find all entities sharing an email domain."""
        domain = email.split("@")[-1] if "@" in email else ""
        if not domain:
            return []
        return [
            eid for eid, entity in self._entities.items()
            if any(e.endswith(f"@{domain}") for e in entity.linked_emails)
        ]

    def suggest_merges(self, min_confidence: float = 0.8) -> List[EntityLink]:
        """Get high-confidence merge suggestions."""
        return [link for link in self._links if link.confidence >= min_confidence]

    def _find_candidates(self, entity_id: str, attributes: Dict[str, Any]) -> List[Tuple[str, float]]:
        """Find candidate matches from existing entities."""
        candidates = []

        for existing_id, existing in self._entities.items():
            score = self._compute_similarity(attributes, existing.properties)
            if score > 0.3:
                candidates.append((existing_id, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:5]

    def _compute_similarity(self, attrs_a: Dict[str, Any], attrs_b: Dict[str, Any]) -> float:
        """Compute overall similarity between two entity attribute sets."""
        scores = []

        name_a = attrs_a.get("name", "")
        name_b = attrs_b.get("name", "")
        if name_a and name_b:
            scores.append(("name", self._jaro_winkler(name_a.lower(), name_b.lower()), 2.0))

        email_a = attrs_a.get("email", "")
        email_b = attrs_b.get("email", "")
        if email_a and email_b:
            scores.append(("email", 1.0 if email_a == email_b else 0.0, 3.0))

        device_a = attrs_a.get("device_id", "")
        device_b = attrs_b.get("device_id", "")
        if device_a and device_b:
            scores.append(("device", 1.0 if device_a == device_b else 0.0, 2.5))

        ip_a = attrs_a.get("ip_address", "")
        ip_b = attrs_b.get("ip_address", "")
        if ip_a and ip_b:
            scores.append(("ip", 1.0 if ip_a == ip_b else 0.0, 1.5))

        if not scores:
            return 0.0

        total_weight = sum(w for _, _, w in scores)
        weighted_sum = sum(s * w for _, s, w in scores)
        return weighted_sum / total_weight

    @staticmethod
    def _jaro_winkler(s1: str, s2: str) -> float:
        """Jaro-Winkler string similarity."""
        if s1 == s2:
            return 1.0
        if not s1 or not s2:
            return 0.0

        max_dist = max(len(s1), len(s2)) // 2 - 1
        if max_dist < 0:
            max_dist = 0

        s1_matches = [False] * len(s1)
        s2_matches = [False] * len(s2)
        matches = 0
        transpositions = 0

        for i in range(len(s1)):
            start = max(0, i - max_dist)
            end = min(i + max_dist + 1, len(s2))
            for j in range(start, end):
                if s2_matches[j] or s1[i] != s2[j]:
                    continue
                s1_matches[i] = True
                s2_matches[j] = True
                matches += 1
                break

        if matches == 0:
            return 0.0

        k = 0
        for i in range(len(s1)):
            if not s1_matches[i]:
                continue
            while not s2_matches[k]:
                k += 1
            if s1[i] != s2[k]:
                transpositions += 1
            k += 1

        jaro = (matches / len(s1) + matches / len(s2) + (matches - transpositions / 2) / matches) / 3

        prefix_len = 0
        for i in range(min(4, len(s1), len(s2))):
            if s1[i] == s2[i]:
                prefix_len += 1
            else:
                break

        return jaro + prefix_len * 0.1 * (1 - jaro)
