"""Main orchestrator for coordinating pipeline analysis"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from .config import Config
from .agents import DevOpsAgent, MLOpsAgent, Issue, Optimization
from .collectors import CollectorFactory
from .monitors.issue_detector import IssueDetector
from .reports.report_generator import ReportGenerator
from .utils.logger import setup_logger

logger = setup_logger(__name__)


class PipelineOrchestrator:
    """Main orchestrator for pipeline analysis and optimization"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize agents
        self.devops_agent = DevOpsAgent(config.agent.__dict__)
        self.mlops_agent = MLOpsAgent(config.agent.__dict__)
        
        # Initialize components
        self.issue_detector = IssueDetector(config)
        self.report_generator = ReportGenerator(config)
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task = None
        
        logger.info("PipelineOrchestrator initialized")
    
    async def analyze_pipelines(
        self,
        pipeline_type: str = "both",
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Perform one-time pipeline analysis"""
        logger.info(f"Starting pipeline analysis: {pipeline_type}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "pipeline_type": pipeline_type,
            "devops": None,
            "mlops": None
        }
        
        # Collect and analyze DevOps pipelines
        if pipeline_type in ["devops", "both"]:
            devops_data = await self._collect_devops_data(source)
            devops_issues = await self.devops_agent.analyze(devops_data)
            
            results["devops"] = {
                "data": devops_data,
                "issues": [issue.to_dict() for issue in devops_issues],
                "summary": self.devops_agent._generate_summary(devops_issues)
            }
            
            logger.info(f"DevOps analysis complete: {len(devops_issues)} issues found")
        
        # Collect and analyze MLOps pipelines
        if pipeline_type in ["mlops", "both"]:
            mlops_data = await self._collect_mlops_data(source)
            mlops_issues = await self.mlops_agent.analyze(mlops_data)
            
            results["mlops"] = {
                "data": mlops_data,
                "issues": [issue.to_dict() for issue in mlops_issues],
                "summary": self.mlops_agent._generate_summary(mlops_issues)
            }
            
            logger.info(f"MLOps analysis complete: {len(mlops_issues)} issues found")
        
        # Run cross-pipeline issue detection
        all_issues = []
        if results["devops"]:
            all_issues.extend(devops_issues)
        if results["mlops"]:
            all_issues.extend(mlops_issues)
        
        cross_issues = await self.issue_detector.detect_cross_pipeline_issues(all_issues)
        results["cross_pipeline_issues"] = [issue.to_dict() for issue in cross_issues]
        
        return results
    
    async def analyze_and_optimize(
        self,
        pipeline_type: str = "both",
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze pipelines and generate optimization suggestions"""
        logger.info(f"Starting analysis and optimization: {pipeline_type}")
        
        # First, perform analysis
        analysis_results = await self.analyze_pipelines(pipeline_type, source)
        
        optimizations = {
            "devops": None,
            "mlops": None
        }
        
        # Generate DevOps optimizations
        if analysis_results["devops"]:
            devops_data = analysis_results["devops"]["data"]
            devops_issues = [
                Issue(**issue) if isinstance(issue, dict) else issue
                for issue in analysis_results["devops"]["issues"]
            ]
            
            devops_opts = await self.devops_agent.optimize(devops_data, devops_issues)
            optimizations["devops"] = [opt.to_dict() for opt in devops_opts]
            
            logger.info(f"Generated {len(devops_opts)} DevOps optimizations")
        
        # Generate MLOps optimizations
        if analysis_results["mlops"]:
            mlops_data = analysis_results["mlops"]["data"]
            mlops_issues = [
                Issue(**issue) if isinstance(issue, dict) else issue
                for issue in analysis_results["mlops"]["issues"]
            ]
            
            mlops_opts = await self.mlops_agent.optimize(mlops_data, mlops_issues)
            optimizations["mlops"] = [opt.to_dict() for opt in mlops_opts]
            
            logger.info(f"Generated {len(mlops_opts)} MLOps optimizations")
        
        analysis_results["optimizations"] = optimizations
        
        return analysis_results
    
    async def start_monitoring(
        self,
        pipeline_type: str = "both",
        source: Optional[str] = None
    ):
        """Start continuous monitoring mode"""
        logger.info("Starting continuous monitoring mode")
        self.monitoring_active = True
        
        interval = self.config.monitoring.interval
        
        while self.monitoring_active:
            try:
                # Perform analysis
                results = await self.analyze_pipelines(pipeline_type, source)
                
                # Check for critical issues
                await self._check_and_alert(results)
                
                # Wait for next interval
                logger.info(f"Waiting {interval} seconds until next check...")
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error during monitoring: {e}", exc_info=True)
                await asyncio.sleep(interval)
    
    async def _check_and_alert(self, results: Dict[str, Any]):
        """Check results for critical issues and send alerts"""
        critical_issues = []
        
        # Collect critical issues from both pipelines
        if results.get("devops"):
            devops_issues = results["devops"]["issues"]
            critical_issues.extend([
                i for i in devops_issues
                if i.get("severity") in ["critical", "high"]
            ])
        
        if results.get("mlops"):
            mlops_issues = results["mlops"]["issues"]
            critical_issues.extend([
                i for i in mlops_issues
                if i.get("severity") in ["critical", "high"]
            ])
        
        if critical_issues and self.config.monitoring.enable_notifications:
            logger.warning(f"Found {len(critical_issues)} critical/high severity issues")
            # In a real implementation, this would send notifications
            # via email, Slack, PagerDuty, etc.
            await self._send_notifications(critical_issues)
    
    async def _send_notifications(self, issues: List[Dict[str, Any]]):
        """Send notifications about critical issues"""
        logger.info(f"Sending notifications for {len(issues)} critical issues")
        
        for channel in self.config.monitoring.notification_channels:
            logger.info(f"  - Notification sent via {channel}")
            # Implementation would integrate with actual notification services
    
    async def _collect_devops_data(self, source: Optional[str]) -> Dict[str, Any]:
        """Collect DevOps pipeline data from configured sources"""
        # Determine collector type from source
        collector_type = self._determine_collector_type(source)
        collector = CollectorFactory.create_collector(collector_type, self.config.__dict__)
        
        data = await collector.collect(source or "default", lookback_days=7)
        
        # Add security scan data if available
        if "security_scans" not in data:
            data["security_scans"] = await self._collect_security_scans()
        
        return data
    
    async def _collect_mlops_data(self, source: Optional[str]) -> Dict[str, Any]:
        """Collect MLOps pipeline data from configured sources"""
        # Collect from multiple sources
        mlflow_collector = CollectorFactory.create_collector("mlflow", self.config.__dict__)
        k8s_collector = CollectorFactory.create_collector("kubernetes", self.config.__dict__)
        dq_collector = CollectorFactory.create_collector("data_quality", self.config.__dict__)
        
        mlflow_data = await mlflow_collector.collect(source or "default")
        k8s_data = await k8s_collector.collect(source or "default")
        dq_data = await dq_collector.collect(source or "default")
        
        # Merge data from different sources
        merged_data = {
            **mlflow_data,
            "inference_metrics": k8s_data.get("inference_metrics", {}),
            "data_metrics": dq_data.get("data_metrics", {})
        }
        
        return merged_data
    
    async def _collect_security_scans(self) -> List[Dict[str, Any]]:
        """Collect security scan results"""
        # Simulate security scan data
        import random
        
        vulnerabilities = []
        if random.random() > 0.7:  # 30% chance of having vulnerabilities
            num_vulns = random.randint(1, 3)
            for i in range(num_vulns):
                vulnerabilities.append({
                    "cve": f"CVE-2024-{random.randint(1000, 9999)}",
                    "severity": random.choice(["critical", "high", "medium"]),
                    "package": random.choice(["requests", "numpy", "django", "flask"])
                })
        
        return [{
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": vulnerabilities
        }]
    
    def _determine_collector_type(self, source: Optional[str]) -> str:
        """Determine collector type from source string"""
        if not source:
            return "jenkins"
        
        source_lower = source.lower()
        
        if "jenkins" in source_lower:
            return "jenkins"
        elif "github" in source_lower:
            return "github"
        elif "gitlab" in source_lower:
            return "gitlab"
        else:
            return "jenkins"  # default
    
    def generate_report(
        self,
        results: Dict[str, Any],
        output_dir: str = "reports"
    ) -> str:
        """Generate analysis report"""
        return self.report_generator.generate_analysis_report(results, output_dir)
    
    def generate_optimization_report(
        self,
        results: Dict[str, Any],
        output_dir: str = "reports"
    ) -> str:
        """Generate optimization report"""
        return self.report_generator.generate_optimization_report(results, output_dir)
    
    async def shutdown(self):
        """Shutdown orchestrator and cleanup"""
        logger.info("Shutting down orchestrator")
        self.monitoring_active = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
