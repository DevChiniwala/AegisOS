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
        "models/ensemble/catboost_model.py",
        [
            ("if self.model is None: return 0.5", "if self.model is None:\n            return 0.5"),
            ("if self.model is None: return [0.5]*len(features)", "if self.model is None:\n            return [0.5]*len(features)")
        ]
    ),
    (
        "models/ensemble/lightgbm_model.py",
        [
            ("if self.model is None: return 0.5", "if self.model is None:\n            return 0.5"),
            ("if self.model is None: return [0.5]*len(features)", "if self.model is None:\n            return [0.5]*len(features)")
        ]
    ),
    (
        "models/ensemble/xgboost_model.py",
        [
            ("if self.model is None: return 0.5", "if self.model is None:\n            return 0.5"),
            ("if self.model is None: return [0.5]*len(features)", "if self.model is None:\n            return [0.5]*len(features)")
        ]
    )
]

for filepath, replacements in fixes:
    fix_file(filepath, replacements)
