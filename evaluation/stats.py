import numpy as np
from typing import Callable, Tuple, Dict, Any
from sklearn.metrics import f1_score

def bootstrap_ci(
    y_true: np.ndarray | list,
    y_pred: np.ndarray | list,
    metric_fn: Callable = f1_score,
    n_resamples: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> Tuple[float, float, float]:
    """
    Computes point estimate and 95% Confidence Interval [lower, upper] via bootstrap resampling.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    rng = np.random.default_rng(seed)
    
    point_est = metric_fn(y_true, y_pred)
    
    n_samples = len(y_true)
    bootstrapped_scores = []
    
    for _ in range(n_resamples):
        indices = rng.choice(n_samples, size=n_samples, replace=True)
        # We try to calculate metric; if it fails (e.g. only one class in y_true), handle gracefully if possible
        try:
            score = metric_fn(y_true[indices], y_pred[indices])
            bootstrapped_scores.append(score)
        except Exception:
            pass
            
    if not bootstrapped_scores:
        return point_est, float('nan'), float('nan')
        
    lower = np.percentile(bootstrapped_scores, 100 * (alpha / 2))
    upper = np.percentile(bootstrapped_scores, 100 * (1 - alpha / 2))
    
    return float(point_est), float(lower), float(upper)


def mcnemar_test(
    y_true: np.ndarray | list,
    y_pred_baseline: np.ndarray | list,
    y_pred_model: np.ndarray | list
) -> dict:
    """
    Computes McNemar test statistic and p-value comparing two models.
    """
    y_true = np.array(y_true)
    y_pred_baseline = np.array(y_pred_baseline)
    y_pred_model = np.array(y_pred_model)
    
    # Calculate contingency table
    correct_baseline = (y_true == y_pred_baseline)
    correct_model = (y_true == y_pred_model)
    
    # b: model correct, baseline wrong
    b = np.sum(correct_model & ~correct_baseline)
    # c: baseline correct, model wrong
    c = np.sum(~correct_model & correct_baseline)
    
    # Calculate McNemar test
    # If b + c < 25, exact binomial test is recommended
    if b + c < 25:
        # Binomial test
        try:
            from scipy.stats import binomtest
            p_value = binomtest(b, b + c, 0.5).pvalue
        except ImportError:
            try:
                from scipy.stats import binom_test
                p_value = binom_test(b, b + c, 0.5)
            except ImportError:
                # Fallback to simple calculation if scipy is unavailable
                p_value = 1.0 # Requires scipy
        stat = min(b, c)
    else:
        # Asymptotic (chi-squared) with Edwards continuity correction
        stat = ((abs(b - c) - 1)**2) / (b + c)
        try:
            from scipy.stats import chi2
            p_value = chi2.sf(stat, 1)
        except ImportError:
            p_value = 1.0 # Requires scipy
            
    return {
        "statistic": float(stat),
        "p_value": float(p_value),
        "b": int(b),
        "c": int(c)
    }


def format_ieee_table(results_dict: dict) -> str:
    """
    Converts ablation results into a clean IEEE-formatted LaTeX table string and markdown string.
    """
    latex_table = "\\begin{table}[htbp]\n"
    latex_table += "\\caption{Ablation Results}\n"
    latex_table += "\\begin{center}\n"
    latex_table += "\\begin{tabular}{|c|c|c|c|}\n"
    latex_table += "\\hline\n"
    latex_table += "\\textbf{Model} & \\textbf{Set B F1 (95\\% CI)} & \\textbf{Evasion Recall} \\\\\n"
    latex_table += "\\hline\n"
    
    md_table = "| Model | Set B F1 (95% CI) | Evasion Recall |\n"
    md_table += "|---|---|---|\n"
    
    models = results_dict.get("Model", [])
    
    # Allow for potential keys for F1 and CI
    f1_key = "Set B F1" if "Set B F1" in results_dict else "F1"
    lower_key = "F1 Lower CI" if "F1 Lower CI" in results_dict else "Lower CI"
    upper_key = "F1 Upper CI" if "F1 Upper CI" in results_dict else "Upper CI"
    recall_key = "Evasion Recall" if "Evasion Recall" in results_dict else "Recall"
    
    for i, model in enumerate(models):
        f1 = results_dict[f1_key][i]
        lower = results_dict[lower_key][i]
        upper = results_dict[upper_key][i]
        recall = results_dict[recall_key][i]
        
        latex_table += f"{model} & {f1:.3f} [{lower:.3f}, {upper:.3f}] & {recall:.3f} \\\\\n"
        latex_table += "\\hline\n"
        
        md_table += f"| {model} | {f1:.3f} [{lower:.3f}, {upper:.3f}] | {recall:.3f} |\n"
        
    latex_table += "\\end{tabular}\n"
    latex_table += "\\end{center}\n"
    latex_table += "\\end{table}\n"
    
    return f"LaTeX Table:\n```latex\n{latex_table}```\n\nMarkdown Table:\n{md_table}"


def check_success_criteria(results_matrix: dict) -> dict:
    """
    Evaluates whether the success criteria in README/Plan are met:
      - Set B F1 >= 0.80
      - 95% CI lower bound > Policy-Only baseline
      - Evasion set margin > SRI-linear by non-trivial margin (+10% Recall)
    """
    models = results_matrix.get("Model", [])
    
    try:
        ours_idx = models.index("Ours")
        policy_idx = models.index("Policy-Only")
        sri_idx = models.index("SRI-linear")
    except ValueError:
        return {"error": "Missing models in results_matrix. Required: 'Ours', 'Policy-Only', 'SRI-linear'"}
        
    f1_key = "Set B F1" if "Set B F1" in results_matrix else "F1"
    lower_key = "F1 Lower CI" if "F1 Lower CI" in results_matrix else "Lower CI"
    recall_key = "Evasion Recall" if "Evasion Recall" in results_matrix else "Recall"
    
    ours_f1 = results_matrix[f1_key][ours_idx]
    ours_lower_ci = results_matrix[lower_key][ours_idx]
    policy_f1 = results_matrix[f1_key][policy_idx]
    
    ours_evasion = results_matrix[recall_key][ours_idx]
    sri_evasion = results_matrix[recall_key][sri_idx]
    
    criteria = {
        "set_b_f1_ge_80": bool(ours_f1 >= 0.80),
        "ci_lower_gt_policy_baseline": bool(ours_lower_ci > policy_f1),
        "evasion_margin_gt_sri_10_percent": bool(ours_evasion >= (sri_evasion + 0.10))
    }
    
    criteria["overall_success"] = all(criteria.values())
    
    return criteria
