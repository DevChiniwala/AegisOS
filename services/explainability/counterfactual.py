import numpy as np
from typing import Dict, Any
from scipy.optimize import minimize

class CounterfactualExplainer:
    def generate_counterfactual(self, model: Any, features: Dict[str, float], target_outcome: str = 'legitimate') -> Dict[str, Any]:
        """
        Finds minimal feature changes to flip the prediction.
        Uses gradient-free optimization (scipy minimize).
        """
        if not model:
            return {"changed_features": {}, "explanation": "No model provided"}
            
        feature_names = list(features.keys())
        initial_x = np.array(list(features.values()))
        
        # Define prediction wrapper
        def predict_prob(x):
            try:
                # Scikit-learn style
                return model.predict_proba([x])[0][1] # Probability of fraud
            except AttributeError:
                # Assuming callable model that returns scalar
                return model([x])[0]

        original_score = predict_prob(initial_x)
        
        if target_outcome == 'legitimate' and original_score < 0.5:
            return {"message": "Already legitimate"}
            
        # Objective function: distance + penalty if prob doesn't cross threshold
        def objective(x):
            distance = np.linalg.norm(x - initial_x)
            prob = predict_prob(x)
            penalty = 1000 * max(0, prob - 0.5) if target_outcome == 'legitimate' else 1000 * max(0, 0.5 - prob)
            return distance + penalty

        # Bounds: prevent extreme values
        bounds = [(val * 0.5, val * 1.5) if val > 0 else (-1, 1) for val in initial_x]
        
        res = minimize(objective, initial_x, method='L-BFGS-B', bounds=bounds)
        
        changed_features = {}
        for i, name in enumerate(feature_names):
            if abs(res.x[i] - initial_x[i]) > 1e-4:
                changed_features[name] = res.x[i]
                
        counterfactual_score = predict_prob(res.x)
        
        return {
            "changed_features": changed_features,
            "original_score": original_score,
            "counterfactual_score": counterfactual_score,
            "explanation_text": f"Prediction flips if {', '.join([f'{k} changes to {v:.2f}' for k, v in changed_features.items()])}"
        }
