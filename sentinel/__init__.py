"""
Sentinel Core Engine.

This package provides the core components for ToolTrace, an IEEE-targeted security framework.
It includes the interceptor for capturing tool traces, feature extractors, machine learning
detectors, weight learning models, and the main risk engine.
"""

from .interceptor import ToolTraceInterceptor
from .risk_engine import RiskEngine

__all__ = ["ToolTraceInterceptor", "RiskEngine"]
