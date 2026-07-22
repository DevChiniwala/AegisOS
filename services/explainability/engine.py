from core.schemas.risk import RiskExplanation
from .shap_explainer import SHAPExplainer
from .counterfactual import CounterfactualExplainer
from .narrator import ExplanationNarrator
from .similar_cases import SimilarCaseFinder

class ExplainabilityEngine:
    def __init__(self):
        self.shap_explainer = SHAPExplainer()
        self.cf_explainer = CounterfactualExplainer()
        self.narrator = ExplanationNarrator()
        self.similar_finder = SimilarCaseFinder()

    async def explain(self, transaction, features, risk_score: float, models: dict, graph_engine=None, behavioral_engine=None, memory_engine=None) -> RiskExplanation:
        
        # 1. Get SHAP values
        shap_vals = self.shap_explainer.explain_prediction(models.get('primary'), features)
        top_feats = self.shap_explainer.top_features(shap_vals)
        
        # 2. Get Counterfactual
        cf = self.cf_explainer.generate_counterfactual(models.get('primary'), features)
        
        # 3. Find Similar Cases
        similar_cases = self.similar_finder.find_similar(features)
        
        # 4. Generate Narrative
        explanation = RiskExplanation(
            risk_score=risk_score,
            top_features=top_feats,
            counterfactual=cf,
            similar_cases=similar_cases,
            narrative=""
        )
        explanation.narrative = self.narrator.narrate(explanation, transaction)
        
        return explanation
