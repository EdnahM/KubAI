"""Report generation for pipeline analysis"""

from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path
import json

from ..config import Config
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ReportGenerator:
    """Generate reports for pipeline analysis and optimization"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def generate_analysis_report(
        self,
        results: Dict[str, Any],
        output_dir: str = "reports"
    ) -> str:
        """Generate comprehensive analysis report"""
        logger.info("Generating analysis report")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate markdown report
        report_file = output_path / f"pipeline_analysis_{timestamp}.md"
        markdown_content = self._generate_markdown_report(results)
        
        with open(report_file, "w") as f:
            f.write(markdown_content)
        
        # Also save JSON version
        json_file = output_path / f"pipeline_analysis_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Report generated: {report_file}")
        
        return str(report_file)
    
    def generate_optimization_report(
        self,
        results: Dict[str, Any],
        output_dir: str = "reports"
    ) -> str:
        """Generate optimization suggestions report"""
        logger.info("Generating optimization report")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate markdown report
        report_file = output_path / f"optimization_plan_{timestamp}.md"
        markdown_content = self._generate_optimization_markdown(results)
        
        with open(report_file, "w") as f:
            f.write(markdown_content)
        
        logger.info(f"Optimization report generated: {report_file}")
        
        return str(report_file)
    
    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate markdown formatted analysis report"""
        lines = []
        
        # Header
        lines.append("# Pipeline Analysis Report")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Analysis Type:** {results.get('pipeline_type', 'Unknown')}")
        lines.append("\n---\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n")
        
        total_issues = 0
        critical_count = 0
        high_count = 0
        
        if results.get("devops"):
            devops_summary = results["devops"]["summary"]
            total_issues += devops_summary["total"]
            critical_count += devops_summary.get("by_severity", {}).get("critical", 0)
            high_count += devops_summary.get("by_severity", {}).get("high", 0)
        
        if results.get("mlops"):
            mlops_summary = results["mlops"]["summary"]
            total_issues += mlops_summary["total"]
            critical_count += mlops_summary.get("by_severity", {}).get("critical", 0)
            high_count += mlops_summary.get("by_severity", {}).get("high", 0)
        
        lines.append(f"- **Total Issues:** {total_issues}")
        lines.append(f"- **Critical Issues:** {critical_count}")
        lines.append(f"- **High Severity Issues:** {high_count}")
        lines.append("")
        
        # DevOps Analysis
        if results.get("devops"):
            lines.append("## DevOps Pipeline Analysis\n")
            lines.extend(self._format_issues_section(results["devops"]["issues"], "DevOps"))
        
        # MLOps Analysis
        if results.get("mlops"):
            lines.append("\n## MLOps Pipeline Analysis\n")
            lines.extend(self._format_issues_section(results["mlops"]["issues"], "MLOps"))
        
        # Cross-Pipeline Issues
        if results.get("cross_pipeline_issues"):
            lines.append("\n## Cross-Pipeline Issues\n")
            lines.append("These issues affect multiple systems and require coordinated resolution:\n")
            lines.extend(self._format_issues_section(results["cross_pipeline_issues"], "Cross-Pipeline"))
        
        # Recommendations Summary
        lines.append("\n## Priority Recommendations\n")
        lines.append(self._generate_priority_recommendations(results))
        
        return "\n".join(lines)
    
    def _format_issues_section(self, issues: List[Dict], section_name: str) -> List[str]:
        """Format issues section for markdown report"""
        lines = []
        
        if not issues:
            lines.append(f"✅ No issues detected in {section_name} pipelines.\n")
            return lines
        
        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue.get("severity", "unknown")
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)
        
        # Output by severity
        for severity in ["critical", "high", "medium", "low"]:
            if severity not in by_severity:
                continue
            
            severity_issues = by_severity[severity]
            icon = self._get_severity_icon(severity)
            
            lines.append(f"### {icon} {severity.upper()} Severity ({len(severity_issues)} issues)\n")
            
            for i, issue in enumerate(severity_issues, 1):
                lines.append(f"#### {i}. {issue.get('title')}\n")
                lines.append(f"**Category:** {issue.get('category')}")
                lines.append(f"**Affected Component:** {issue.get('affected_component')}")
                lines.append(f"**Confidence:** {issue.get('confidence', 0):.0%}\n")
                lines.append(f"**Description:**")
                lines.append(f"{issue.get('description')}\n")
                lines.append(f"**Impact:**")
                lines.append(f"{issue.get('impact')}\n")
                lines.append(f"**Recommendation:**")
                lines.append(f"{issue.get('recommendation')}\n")
                lines.append("---\n")
        
        return lines
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢"
        }
        return icons.get(severity, "⚪")
    
    def _generate_priority_recommendations(self, results: Dict[str, Any]) -> str:
        """Generate priority recommendations summary"""
        lines = []
        
        # Collect all critical and high issues
        priority_issues = []
        
        if results.get("devops"):
            for issue in results["devops"]["issues"]:
                if issue.get("severity") in ["critical", "high"]:
                    priority_issues.append(issue)
        
        if results.get("mlops"):
            for issue in results["mlops"]["issues"]:
                if issue.get("severity") in ["critical", "high"]:
                    priority_issues.append(issue)
        
        if not priority_issues:
            return "✅ No high-priority issues requiring immediate attention.\n"
        
        # Sort by severity and confidence
        severity_order = {"critical": 0, "high": 1}
        priority_issues.sort(
            key=lambda x: (severity_order.get(x.get("severity"), 99), -x.get("confidence", 0))
        )
        
        lines.append("### Top Priority Actions:\n")
        
        for i, issue in enumerate(priority_issues[:5], 1):  # Top 5
            lines.append(f"{i}. **{issue.get('title')}** ({issue.get('severity')} severity)")
            lines.append(f"   - {issue.get('recommendation')}\n")
        
        return "\n".join(lines)
    
    def _generate_optimization_markdown(self, results: Dict[str, Any]) -> str:
        """Generate markdown formatted optimization report"""
        lines = []
        
        # Header
        lines.append("# Pipeline Optimization Plan")
        lines.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n---\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n")
        
        devops_opt_count = len(results.get("optimizations", {}).get("devops", []))
        mlops_opt_count = len(results.get("optimizations", {}).get("mlops", []))
        
        lines.append(f"This optimization plan provides {devops_opt_count + mlops_opt_count} actionable recommendations to improve your pipeline performance, reliability, and efficiency.\n")
        lines.append(f"- **DevOps Optimizations:** {devops_opt_count}")
        lines.append(f"- **MLOps Optimizations:** {mlops_opt_count}\n")
        
        # DevOps Optimizations
        if results.get("optimizations", {}).get("devops"):
            lines.append("## DevOps Pipeline Optimizations\n")
            lines.extend(self._format_optimizations(results["optimizations"]["devops"]))
        
        # MLOps Optimizations
        if results.get("optimizations", {}).get("mlops"):
            lines.append("\n## MLOps Pipeline Optimizations\n")
            lines.extend(self._format_optimizations(results["optimizations"]["mlops"]))
        
        # Implementation Roadmap
        lines.append("\n## Implementation Roadmap\n")
        lines.append(self._generate_implementation_roadmap(results))
        
        return "\n".join(lines)
    
    def _format_optimizations(self, optimizations: List[Dict]) -> List[str]:
        """Format optimizations section"""
        lines = []
        
        for i, opt in enumerate(optimizations, 1):
            priority_icon = "🔥" if opt.get("priority", 5) <= 2 else "⭐"
            
            lines.append(f"### {priority_icon} {i}. {opt.get('title')}\n")
            lines.append(f"**Type:** {opt.get('type')}")
            lines.append(f"**Priority:** {opt.get('priority')}/5")
            lines.append(f"**Implementation Effort:** {opt.get('implementation_effort')}\n")
            lines.append(f"**Description:**")
            lines.append(f"{opt.get('description')}\n")
            lines.append(f"**Estimated Impact:**")
            lines.append(f"{opt.get('estimated_impact')}\n")
            lines.append(f"**Implementation Steps:**")
            
            for step_num, step in enumerate(opt.get('steps', []), 1):
                lines.append(f"{step_num}. {step}")
            
            lines.append("")
            
            # Metrics Impact
            if opt.get('metrics_impact'):
                lines.append("**Expected Metrics Improvement:**")
                for metric, impact in opt['metrics_impact'].items():
                    impact_str = f"+{impact*100:.0f}%" if impact > 0 else f"{impact*100:.0f}%"
                    lines.append(f"- {metric.replace('_', ' ').title()}: {impact_str}")
                lines.append("")
            
            lines.append("---\n")
        
        return lines
    
    def _generate_implementation_roadmap(self, results: Dict[str, Any]) -> str:
        """Generate implementation roadmap"""
        lines = []
        
        # Collect all optimizations
        all_opts = []
        
        if results.get("optimizations", {}).get("devops"):
            all_opts.extend([
                {**opt, "pipeline": "DevOps"}
                for opt in results["optimizations"]["devops"]
            ])
        
        if results.get("optimizations", {}).get("mlops"):
            all_opts.extend([
                {**opt, "pipeline": "MLOps"}
                for opt in results["optimizations"]["mlops"]
            ])
        
        # Sort by priority
        all_opts.sort(key=lambda x: x.get("priority", 5))
        
        # Phase 1: High priority, low/medium effort
        phase1 = [
            opt for opt in all_opts
            if opt.get("priority", 5) <= 2 and opt.get("implementation_effort") in ["low", "medium"]
        ]
        
        # Phase 2: High priority, high effort OR medium priority, low/medium effort
        phase2 = [
            opt for opt in all_opts
            if (opt.get("priority", 5) <= 2 and opt.get("implementation_effort") == "high") or
               (opt.get("priority", 5) == 3 and opt.get("implementation_effort") in ["low", "medium"])
        ]
        
        # Phase 3: Everything else
        phase3 = [opt for opt in all_opts if opt not in phase1 and opt not in phase2]
        
        if phase1:
            lines.append("### Phase 1: Quick Wins (Immediate - 2 weeks)\n")
            for opt in phase1:
                lines.append(f"- **{opt.get('title')}** ({opt.get('pipeline')})")
            lines.append("")
        
        if phase2:
            lines.append("### Phase 2: High-Impact Improvements (2-6 weeks)\n")
            for opt in phase2:
                lines.append(f"- **{opt.get('title')}** ({opt.get('pipeline')})")
            lines.append("")
        
        if phase3:
            lines.append("### Phase 3: Long-Term Enhancements (6+ weeks)\n")
            for opt in phase3:
                lines.append(f"- **{opt.get('title')}** ({opt.get('pipeline')})")
            lines.append("")
        
        return "\n".join(lines)
