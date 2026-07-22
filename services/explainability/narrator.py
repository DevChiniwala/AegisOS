from core.schemas.risk import RiskExplanation
from typing import Any

class ExplanationNarrator:
    def narrate(self, risk_explanation: RiskExplanation, transaction: Any) -> str:
        score = risk_explanation.risk_score
        top_feats = risk_explanation.top_features
        
        narrative = f"The transaction has been assigned a risk score of {score:.2f}. "
        
        if score > 0.8:
            narrative += "This is considered HIGH RISK. "
        elif score > 0.5:
            narrative += "This is considered MODERATE RISK. "
        else:
            narrative += "This is considered LOW RISK. "
            
        if top_feats:
            narrative += "The key driving factors are: \n"
            for feat in top_feats[:3]:
                impact = "increased" if feat.contribution == "positive" else "decreased"
                narrative += f"- {feat.feature}: {impact} the risk score.\n"
                
        if risk_explanation.counterfactual and 'explanation_text' in risk_explanation.counterfactual:
            narrative += f"\nCounterfactual analysis: {risk_explanation.counterfactual['explanation_text']}"
            
        return narrative
