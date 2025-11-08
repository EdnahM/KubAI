"""Issue detection and pattern matching"""

from typing import Dict, List, Any
from datetime import datetime

from ..agents.base_agent import Issue
from ..config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class IssueDetector:
    """Detects patterns and correlations across pipeline issues"""
    
    def __init__(self, config: Config):
        self.config = config
        self.pattern_rules = self._load_pattern_rules()
    
    def _load_pattern_rules(self) -> Dict[str, Any]:
        """Load cross-pipeline issue detection rules"""
        return {
            "cascading_failures": {
                "description": "Build failures causing deployment issues",
                "pattern": ["build", "deployment"],
                "severity": "critical"
            },
            "resource_bottleneck": {
                "description": "Resource constraints affecting multiple pipelines",
                "pattern": ["cpu", "memory", "resource"],
                "severity": "high"
            },
            "data_quality_impact": {
                "description": "Data quality issues affecting model performance",
                "pattern": ["data", "model", "performance"],
                "severity": "high"
            }
        }
    
    async def detect_cross_pipeline_issues(self, issues: List[Issue]) -> List[Issue]:
        """Detect issues that span multiple pipelines"""
        logger.info("Detecting cross-pipeline issues")
        
        cross_issues = []
        
        # Check for cascading failures
        cascading = self._detect_cascading_failures(issues)
        cross_issues.extend(cascading)
        
        # Check for resource bottlenecks
        bottlenecks = self._detect_resource_bottlenecks(issues)
        cross_issues.extend(bottlenecks)
        
        # Check for systemic patterns
        systemic = self._detect_systemic_issues(issues)
        cross_issues.extend(systemic)
        
        logger.info(f"Detected {len(cross_issues)} cross-pipeline issues")
        
        return cross_issues
    
    def _detect_cascading_failures(self, issues: List[Issue]) -> List[Issue]:
        """Detect cascading failures across pipelines"""
        cross_issues = []
        
        # Look for build + deployment failures
        build_failures = [i for i in issues if "build" in i.title.lower() and i.severity in ["high", "critical"]]
        deployment_failures = [i for i in issues if "deployment" in i.title.lower()]
        
        if build_failures and deployment_failures:
            cross_issues.append(Issue(
                severity="critical",
                category="reliability",
                title="Cascading Failures Detected",
                description=f"Build failures ({len(build_failures)}) are likely causing deployment issues ({len(deployment_failures)})",
                affected_component="CI/CD Pipeline",
                impact="Build failures block deployments, creating a bottleneck in the release process",
                recommendation="Fix build issues first: address test failures, resolve dependency conflicts, improve build stability",
                confidence=0.85,
                metadata={
                    "build_failures": len(build_failures),
                    "deployment_failures": len(deployment_failures)
                }
            ))
        
        return cross_issues
    
    def _detect_resource_bottlenecks(self, issues: List[Issue]) -> List[Issue]:
        """Detect resource bottlenecks affecting multiple systems"""
        cross_issues = []
        
        # Look for multiple resource-related issues
        resource_issues = [
            i for i in issues
            if i.category == "performance" and any(
                keyword in i.title.lower()
                for keyword in ["cpu", "memory", "resource", "gpu"]
            )
        ]
        
        if len(resource_issues) >= 2:
            cross_issues.append(Issue(
                severity="high",
                category="performance",
                title="System-Wide Resource Constraints",
                description=f"Multiple pipelines experiencing resource constraints ({len(resource_issues)} issues)",
                affected_component="Infrastructure",
                impact="Resource constraints are creating bottlenecks across DevOps and MLOps pipelines",
                recommendation="Scale infrastructure, optimize resource allocation, implement resource quotas, investigate resource leaks",
                confidence=0.80,
                metadata={"resource_issue_count": len(resource_issues)}
            ))
        
        return cross_issues
    
    def _detect_systemic_issues(self, issues: List[Issue]) -> List[Issue]:
        """Detect systemic issues affecting the entire platform"""
        cross_issues = []
        
        # Count issues by category
        category_counts = {}
        for issue in issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Check for predominant issue categories
        for category, count in category_counts.items():
            if count >= 5:  # Many issues in same category
                cross_issues.append(Issue(
                    severity="high",
                    category=category,
                    title=f"Systemic {category.title()} Issues",
                    description=f"Detected {count} {category} issues across pipelines",
                    affected_component="Platform-Wide",
                    impact=f"Multiple {category} issues indicate a systemic problem requiring platform-level attention",
                    recommendation=f"Conduct root cause analysis for {category} issues, implement platform-level improvements, review {category} best practices",
                    confidence=0.75,
                    metadata={"issue_count": count, "category": category}
                ))
        
        return cross_issues
