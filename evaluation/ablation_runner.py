import os
import json
import argparse
import glob
from typing import Dict, List, Any
import numpy as np
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score

from sentinel.features import compute_policy_violation, FeatureExtractor
from sentinel.ml_detector import MLDetector
from sentinel.risk_engine import RiskEngine
from evaluation.stats import bootstrap_ci, format_ieee_table

def load_dataset(dataset_path: str) -> List[Dict[str, Any]]:
    traces = []
    if not os.path.exists(dataset_path):
        return traces
    for filepath in glob.glob(os.path.join(dataset_path, "*.json")):
        with open(filepath, 'r') as f:
            try:
                trace = json.load(f)
                traces.append(trace)
            except json.JSONDecodeError:
                pass
    return traces

def get_y_true(traces: List[Dict[str, Any]]) -> List[int]:
    return [1 if t.get('label', 'SAFE') == 'ATTACK' else 0 for t in traces]

def process_trace_tool_calls(trace: Dict[str, Any]) -> Dict[str, Any]:
    tool_calls = trace.get('tool_calls', trace.get('tool_sequence', []))
    processed_trace = {'user_prompt': trace.get('user_prompt', ''), 'tool_calls': []}
    
    for call in tool_calls:
        c = dict(call)
        trust = c.get('source_trust', 1.0)
        if isinstance(trust, str):
            c['source_trust'] = 0.1 if trust == "EXTERNAL_CONTENT" else 1.0
        if 'args' in c and 'arguments' not in c:
            c['arguments'] = c['args']
        processed_trace['tool_calls'].append(c)
    return processed_trace

def run_ablation():
    parser = argparse.ArgumentParser(description="Run 4-Model Ablation Matrix")
    parser.add_argument('--dev', action='store_true', help='Reduce bootstrap iterations for fast debugging')
    args = parser.parse_args()

    n_resamples = 100 if args.dev else 1000

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data', 'attacks')
    models_dir = os.path.join(base_dir, 'data', 'models')

    datasets = {
        'Set A': load_dataset(os.path.join(data_dir, 'set_a')),
        'Set B': load_dataset(os.path.join(data_dir, 'set_b_redteam')),
        'Evasion': load_dataset(os.path.join(data_dir, 'evasion_set'))
    }

    feature_extractor = FeatureExtractor()
    ml_detector = MLDetector()
    xgb_path = os.path.join(models_dir, 'xgboost_detector.json')
    if os.path.exists(xgb_path):
        ml_detector.load_model(xgb_path)

    risk_engine = RiskEngine(weights_path=os.path.join(models_dir, 'frozen_weights.json'))

    models = ["Policy Only", "XGBoost-raw", "SRI-linear", "SentinelMCP Hybrid"]
    results = []
    
    table_dict = {
        "Model": [],
        "Set B F1": [],
        "F1 Lower CI": [],
        "F1 Upper CI": [],
        "Evasion Recall": []
    }

    for model in models:
        print(f"Evaluating model: {model}")
        model_results = {'Model': model, 'Datasets': {}}
        table_dict["Model"].append(model)
        
        set_b_f1 = 0.0
        set_b_f1_lower = 0.0
        set_b_f1_upper = 0.0
        evasion_recall = 0.0
        
        for ds_name, traces in datasets.items():
            if not traces:
                continue
                
            y_true = get_y_true(traces)
            y_pred_probs = []
            
            for trace in traces:
                processed = process_trace_tool_calls(trace)
                
                if model == "Policy Only":
                    score = compute_policy_violation(processed['tool_calls'])
                
                elif model == "XGBoost-raw":
                    score = 0.0
                    for call in processed['tool_calls']:
                        score = max(score, ml_detector.predict_risk(call))
                        
                elif model == "SRI-linear":
                    features = feature_extractor.extract(processed)
                    cd = features.context_drift
                    pv = features.policy_violation
                    tr = features.transition_risk
                    st = features.source_trust
                    
                    weights = risk_engine.weight_learner.get_weights()
                    if isinstance(weights, dict):
                        weights = list(weights.values())
                    w1, w2, w3, w4, _ = weights
                    w_sum = w1 + w2 + w3 + w4
                    if w_sum > 0:
                        w1, w2, w3, w4 = w1/w_sum, w2/w_sum, w3/w_sum, w4/w_sum
                    else:
                        w1, w2, w3, w4 = 0.25, 0.25, 0.25, 0.25
                    score = float(w1*cd + w2*pv + w3*tr + w4*st)
                    
                elif model == "SentinelMCP Hybrid":
                    res = risk_engine.evaluate_session(trace)
                    score = res['sri_score'] / 100.0
                    
                y_pred_probs.append(score)
                
            # Compute metrics
            y_pred_binary = [1 if p > 0.5 else 0 for p in y_pred_probs]
            
            try:
                auc = roc_auc_score(y_true, y_pred_probs) if len(set(y_true)) > 1 else np.nan
            except Exception:
                auc = np.nan
                
            precision = precision_score(y_true, y_pred_binary, zero_division=0)
            recall = recall_score(y_true, y_pred_binary, zero_division=0)
            f1 = f1_score(y_true, y_pred_binary, zero_division=0)
            
            # Bootstrapping for CI (use bootstrap_ci from stats.py)
            point_est, ci_low, ci_high = bootstrap_ci(
                y_true, y_pred_binary, metric_fn=f1_score, n_resamples=n_resamples
            )
            
            ds_metrics = {
                'Precision': float(precision),
                'Recall': float(recall),
                'F1': float(f1),
                'AUC': float(auc) if not np.isnan(auc) else None,
                'F1_CI': [float(ci_low) if not np.isnan(ci_low) else None, 
                          float(ci_high) if not np.isnan(ci_high) else None]
            }
            model_results['Datasets'][ds_name] = ds_metrics
            
            if ds_name == "Set B":
                set_b_f1 = f1
                set_b_f1_lower = ci_low
                set_b_f1_upper = ci_high
            elif ds_name == "Evasion":
                evasion_recall = recall
                
        table_dict["Set B F1"].append(set_b_f1)
        table_dict["F1 Lower CI"].append(set_b_f1_lower)
        table_dict["F1 Upper CI"].append(set_b_f1_upper)
        table_dict["Evasion Recall"].append(evasion_recall)
            
        results.append(model_results)

    # Print matrix
    print(json.dumps(results, indent=2))

    # Save outputs
    eval_dir = os.path.join(base_dir, 'evaluation')
    with open(os.path.join(eval_dir, 'evaluation_results.json'), 'w') as f:
        json.dump(results, f, indent=4)
        
    # Generate and save LaTeX
    tex_content = format_ieee_table(table_dict)
    with open(os.path.join(eval_dir, 'ieee_table.tex'), 'w') as f:
        f.write(tex_content)
        
    print("Evaluation completed. Results saved to evaluation_results.json and ieee_table.tex.")

if __name__ == "__main__":
    run_ablation()
