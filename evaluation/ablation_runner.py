"""
Stub script to run the 4-model ablation matrix:
1. Policy Only
2. XGBoost-raw
3. SRI-linear
4. Hybrid
"""

def run_ablation():
    """Run the evaluation matrix."""
    models = ["Policy Only", "XGBoost-raw", "SRI-linear", "Hybrid"]
    for model in models:
        print(f"Evaluating model: {model}")
        # TODO: Implement evaluation logic

if __name__ == "__main__":
    run_ablation()
