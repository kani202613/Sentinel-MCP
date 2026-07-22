import os
import json
import argparse
import numpy as np
from pathlib import Path
from sklearn.metrics import accuracy_score, f1_score

from sentinel.features import FeatureExtractor
from sentinel.ml_detector import MLDetector
from sentinel.weight_learner import WeightLearner

def map_source_trust(trust_str):
    if trust_str == "EXTERNAL_CONTENT":
        return 0.1
    return 1.0

def load_and_preprocess(data_dir):
    extractor = FeatureExtractor()
    sessions = []
    
    for filename in os.listdir(data_dir):
        if not filename.endswith('.json'):
            continue
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        tool_sequence = data.get('tool_sequence', [])
        processed_calls = []
        for call in tool_sequence:
            c = dict(call)
            trust = c.get('source_trust', 1.0)
            if isinstance(trust, str):
                c['source_trust'] = map_source_trust(trust)
            if 'args' in c and 'arguments' not in c:
                c['arguments'] = c['args']
            processed_calls.append(c)
            
        is_attack = data.get('label', '') == 'ATTACK'
        label_val = 1 if is_attack else 0
        
        session_trace = {
            'user_prompt': data.get('user_prompt', ''),
            'tool_calls': processed_calls
        }
        
        sessions.append({
            'trace': session_trace,
            'label': label_val,
            'heuristic_features': extractor.extract(session_trace)
        })
        
    return sessions

def main():
    parser = argparse.ArgumentParser(description="Train ToolTrace models on Set A")
    parser.add_argument("--data-dir", type=str, default="data/attacks/set_a", help="Directory containing training data")
    parser.add_argument("--models-dir", type=str, default="data/models", help="Directory to save models")
    args = parser.parse_args()
    
    print(f"Loading data from {args.data_dir}...")
    sessions = load_and_preprocess(args.data_dir)
    
    if not sessions:
        print("No training data found.")
        return
        
    print(f"Loaded {len(sessions)} sessions.")
    
    ml_detector = MLDetector()
    
    # Train MLDetector
    print("Training MLDetector...")
    ml_X = []
    ml_y = []
    
    for sess in sessions:
        label = sess['label']
        for call in sess['trace']['tool_calls']:
            feats = ml_detector.extract_structural_features(call)
            ml_X.append(feats)
            ml_y.append(label)
            
    ml_detector.train(np.array(ml_X), np.array(ml_y))
    
    # Extract ML features for WeightLearner
    print("Training WeightLearner...")
    wl_X = []
    wl_y = []
    
    for sess in sessions:
        label = sess['label']
        h_feats = sess['heuristic_features']
        
        # Max ML risk for the session
        ml_risk = 0.0
        for call in sess['trace']['tool_calls']:
            risk = ml_detector.predict_risk(call)
            if risk > ml_risk:
                ml_risk = risk
                
        # [CD, PV, TR, ST, ML]
        combined_feats = [
            h_feats.context_drift,
            h_feats.policy_violation,
            h_feats.transition_risk,
            h_feats.source_trust,
            ml_risk
        ]
        wl_X.append(combined_feats)
        wl_y.append(label)
        
    X_wl = np.array(wl_X)
    y_wl = np.array(wl_y)
    
    weight_learner = WeightLearner()
    weight_learner.train(X_wl, y_wl)
    
    # Evaluate WeightLearner
    y_pred = []
    for x in X_wl:
        pred_prob = weight_learner.predict_combined_risk(x)
        y_pred.append(1 if pred_prob >= 0.5 else 0)
        
    acc = accuracy_score(y_wl, y_pred)
    f1 = f1_score(y_wl, y_pred)
    
    weights = weight_learner.get_weights()
    print(f"Learned weights (CD, PV, TR, ST, ML): {weights}")
    print(f"Training Accuracy: {acc:.4f}")
    print(f"Training F1 Score: {f1:.4f}")
    
    # Save models
    os.makedirs(args.models_dir, exist_ok=True)
    
    xgb_path = os.path.join(args.models_dir, 'xgboost_detector.json')
    ml_detector.save_model(xgb_path)
    print(f"Saved MLDetector to {xgb_path}")
        
    weights_path = os.path.join(args.models_dir, 'frozen_weights.json')
    with open(weights_path, 'w') as f:
        json.dump({
            'weights': weights,
            'intercept': float(weight_learner.intercept)
        }, f, indent=4)
    print(f"Saved Weights to {weights_path}")

if __name__ == "__main__":
    main()
