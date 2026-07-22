from typing import Dict, List, Any, Optional
from core.schemas.investigation import InvestigationCase
import uuid

class CaseStore:
    def __init__(self):
        self.cases: Dict[str, InvestigationCase] = {}

    def create_case(self, case: InvestigationCase) -> str:
        case_id = case.case_id or str(uuid.uuid4())
        case.case_id = case_id
        self.cases[case_id] = case
        return case_id

    def update_case(self, case_id: str, updates: Dict[str, Any]) -> None:
        if case_id in self.cases:
            case = self.cases[case_id]
            for k, v in updates.items():
                if hasattr(case, k):
                    setattr(case, k, v)

    def get_case(self, case_id: str) -> Optional[InvestigationCase]:
        return self.cases.get(case_id)

    def search_cases(self, filters: Dict[str, Any]) -> List[InvestigationCase]:
        results = []
        for case in self.cases.values():
            match = True
            for k, v in filters.items():
                if getattr(case, k, None) != v:
                    match = False
                    break
            if match:
                results.append(case)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        stats = {"total_cases": len(self.cases), "by_status": {}}
        for case in self.cases.values():
            status = str(case.status)
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        return stats
