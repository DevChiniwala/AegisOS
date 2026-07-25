import os

def fix_file(filepath, replacements):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r') as f:
        content = f.read()
    
    for old, new in replacements:
        content = content.replace(old, new)
        
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Fixed {filepath}")

fixes = [
    (
        "services/agents/langgraph_orchestrator.py",
        [
            ("from langgraph.graph import END, StateGraph", "pass  # from langgraph.graph import END, StateGraph")
        ]
    ),
    (
        "services/feature_engine/extractors/geo_features.py",
        [
            ("if c: countries_24h.add(c)", "if c:\n                        countries_24h.add(c)"),
            ("if city: cities_24h.add(city)", "if city:\n                        cities_24h.add(city)"),
            ("if tx_country: countries_24h.add(tx_country)", "if tx_country:\n            countries_24h.add(tx_country)")
        ]
    ),
    (
        "services/graph_engine/algorithms/centrality.py",
        [
            ("if entity_id not in graph: return 0.0", "if entity_id not in graph:\n            return 0.0")
        ]
    ),
    (
        "services/graph_engine/engine.py",
        [
            ("if n: shared_nodes.append(n)", "if n:\n                shared_nodes.append(n)")
        ]
    ),
    (
        "services/graph_engine/streaming_tgn.py",
        [
            ("import numpy as np", "pass  # import numpy as np")
        ]
    ),
    (
        "services/knowledge/entity_resolution.py",
        [
            ("return [l for l in self._links if l.source_id == entity_id or l.target_id == entity_id]", "return [link for link in self._links if link.source_id == entity_id or link.target_id == entity_id]"),
            ("return [l for l in self._links if l.confidence >= min_confidence]", "return [link for link in self._links if link.confidence >= min_confidence]")
        ]
    ),
    (
        "services/memory/knowledge_graph.py",
        [
            ("if not target: return []", "if not target:\n            return []")
        ]
    ),
    (
        "services/risk_engine/adversarial.py",
        [
            ("import numpy as np", "pass  # import numpy as np")
        ]
    )
]

for filepath, replacements in fixes:
    fix_file(filepath, replacements)
