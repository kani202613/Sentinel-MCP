"""
Functions for bootstrapping confidence intervals and formatting IEEE tables.
"""
import numpy as np
from scipy import stats

def bootstrap_confidence_interval(data, confidence_level=0.95, n_resamples=1000):
    """
    Computes a bootstrap confidence interval for the mean of the data.
    
    Args:
        data (array-like): 1D array of data points.
        confidence_level (float): Confidence level for the interval.
        n_resamples (int): Number of bootstrap resamples.
        
    Returns:
        tuple: (lower_bound, upper_bound)
    """
    data = np.asarray(data)
    if len(data) == 0:
        return (np.nan, np.nan)
        
    res = stats.bootstrap(
        (data,),
        np.mean,
        confidence_level=confidence_level,
        n_resamples=n_resamples,
        method='BCa'
    )
    return res.confidence_interval.low, res.confidence_interval.high


def format_ieee_table(results):
    """
    Formats the evaluation results into an IEEE-styled table (LaTeX format).
    
    Args:
        results (list of dict): Evaluation results per model.
        
    Returns:
        str: LaTeX formatted table string.
    """
    # TODO: Implement IEEE table generation based on actual results format
    table = "\\begin{table}[htbp]\n"
    table += "\\caption{Evaluation Results}\n"
    table += "\\begin{center}\n"
    table += "\\begin{tabular}{|c|c|c|c|}\n"
    table += "\\hline\n"
    table += "\\textbf{Model} & \\textbf{Precision} & \\textbf{Recall} & \\textbf{F1-Score} \\\\\n"
    table += "\\hline\n"
    # Example rows
    table += "\\hline\n"
    table += "\\end{tabular}\n"
    table += "\\label{tab:results}\n"
    table += "\\end{center}\n"
    table += "\\end{table}"
    return table
