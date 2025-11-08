"""Base AI Agent for pipeline analysis and optimization"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Issue:
    """Represents a detected issue in a pipeline"""
    severity: str  # critical, high, medium, low
    category: str  # performance, reliability, security, cost, quality
    title: str
    description: str
    affected_component: str
    impact: str
    recommendation: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary"""
        return {
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "affected_component": self.affected_component,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "confidence": self.confidence,
            "metadata": self.metadata or {}
        }


@dataclass
class Optimization:
    """Represents an optimization suggestion"""
    type: str  # time, cost, reliability, performance
    title: str
    description: str
    estimated_impact: str
    implementation_effort: str  # low, medium, high
    priority: int  # 1-5, 1 being highest
    steps: List[str]
    metrics_impact: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert optimization to dictionary"""
        return {
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "estimated_impact": self.estimated_impact,
            "implementation_effort": self.implementation_effort,
            "priority": self.priority,
            "steps": self.steps,
            "metrics_impact": self.metrics_impact
        }


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> List[Issue]:
        """Analyze pipeline data and identify issues"""
        pass
    
    @abstractmethod
    async def optimize(self, data: Dict[str, Any], issues: List[Issue]) -> List[Optimization]:
        """Generate optimization suggestions based on analysis"""
        pass
    
    def _calculate_confidence(self, evidence: Dict[str, Any]) -> float:
        """Calculate confidence score based on evidence"""
        # Simple confidence calculation based on evidence strength
        weights = {
            "pattern_match": 0.3,
            "statistical_significance": 0.4,
            "historical_data": 0.3
        }
        
        score = 0.0
        for key, weight in weights.items():
            if key in evidence:
                score += evidence[key] * weight
        
        return min(max(score, 0.0), 1.0)
    
    def _prioritize_issues(self, issues: List[Issue]) -> List[Issue]:
        """Prioritize issues based on severity and confidence"""
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        return sorted(
            issues,
            key=lambda x: (severity_order.get(x.severity, 0), x.confidence),
            reverse=True
        )
    
    def _generate_summary(self, issues: List[Issue]) -> Dict[str, Any]:
        """Generate summary statistics for issues"""
        if not issues:
            return {"total": 0, "by_severity": {}, "by_category": {}}
        
        by_severity = {}
        by_category = {}
        
        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
            by_category[issue.category] = by_category.get(issue.category, 0) + 1
        
        return {
            "total": len(issues),
            "by_severity": by_severity,
            "by_category": by_category
        }
