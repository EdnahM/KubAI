"""AI Agent specialized in DevOps pipeline analysis"""

from typing import Dict, List, Any
import re
from datetime import datetime, timedelta

from .base_agent import BaseAgent, Issue, Optimization
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class DevOpsAgent(BaseAgent):
    """Agent for analyzing DevOps pipelines (CI/CD, deployment, infrastructure)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.issue_patterns = self._load_issue_patterns()
    
    def _load_issue_patterns(self) -> Dict[str, Any]:
        """Load known issue patterns for DevOps pipelines"""
        return {
            "flaky_tests": {
                "pattern": r"(test.*failed|flaky|intermittent)",
                "severity": "high",
                "category": "reliability"
            },
            "slow_builds": {
                "threshold": 600,  # 10 minutes
                "severity": "medium",
                "category": "performance"
            },
            "deployment_failures": {
                "pattern": r"(deployment.*failed|rollback)",
                "severity": "critical",
                "category": "reliability"
            },
            "security_vulnerabilities": {
                "pattern": r"(vulnerability|CVE-|security.*issue)",
                "severity": "critical",
                "category": "security"
            },
            "resource_exhaustion": {
                "pattern": r"(out of memory|disk.*full|cpu.*limit)",
                "severity": "high",
                "category": "performance"
            },
            "pod_failures": {
                "pattern": r"(CrashLoopBackOff|ImagePullBackOff|ErrImagePull)",
                "severity": "critical",
                "category": "reliability"
            },
            "node_issues": {
                "pattern": r"(NodeNotReady|DiskPressure|MemoryPressure)",
                "severity": "high",
                "category": "reliability"
            }
        }
    
    async def analyze(self, data: Dict[str, Any]) -> List[Issue]:
        """Analyze DevOps pipeline data"""
        logger.info("DevOpsAgent analyzing pipeline data")
        issues = []
        
        # Analyze build performance
        build_issues = await self._analyze_build_performance(data.get("builds", []))
        issues.extend(build_issues)
        
        # Analyze test reliability
        test_issues = await self._analyze_test_reliability(data.get("tests", []))
        issues.extend(test_issues)
        
        # Analyze deployment patterns
        deployment_issues = await self._analyze_deployments(data.get("deployments", []))
        issues.extend(deployment_issues)
        
        # Analyze resource usage
        resource_issues = await self._analyze_resource_usage(data.get("resources", {}))
        issues.extend(resource_issues)
        
        # Check for security issues
        security_issues = await self._analyze_security(data.get("security_scans", []))
        issues.extend(security_issues)
        
        # Analyze Kubernetes clusters (if data available)
        k8s_issues = await self._analyze_kubernetes(data.get("kubernetes", {}))
        issues.extend(k8s_issues)
        
        return self._prioritize_issues(issues)
    
    async def _analyze_build_performance(self, builds: List[Dict]) -> List[Issue]:
        """Analyze build performance metrics"""
        issues = []
        
        if not builds:
            return issues
        
        # Calculate average build time
        durations = [b.get("duration", 0) for b in builds if b.get("status") == "success"]
        if durations:
            avg_duration = sum(durations) / len(durations)
            
            # Check for slow builds
            if avg_duration > self.issue_patterns["slow_builds"]["threshold"]:
                issues.append(Issue(
                    severity="medium",
                    category="performance",
                    title="Slow Build Times",
                    description=f"Average build time is {avg_duration:.0f} seconds, exceeding recommended threshold",
                    affected_component="CI/CD Pipeline",
                    impact=f"Delayed feedback cycles, reduced developer productivity. Average delay: {(avg_duration - 300):.0f}s per build",
                    recommendation="Consider: 1) Enable build caching, 2) Parallelize test execution, 3) Use faster build agents, 4) Optimize dependency resolution",
                    confidence=0.9,
                    metadata={"avg_duration": avg_duration, "sample_size": len(durations)}
                ))
        
        # Analyze build failure rate
        total_builds = len(builds)
        failed_builds = len([b for b in builds if b.get("status") == "failed"])
        failure_rate = failed_builds / total_builds if total_builds > 0 else 0
        
        if failure_rate > 0.15:  # More than 15% failure rate
            issues.append(Issue(
                severity="high",
                category="reliability",
                title="High Build Failure Rate",
                description=f"Build failure rate is {failure_rate:.1%}, indicating instability",
                affected_component="Build Process",
                impact=f"{failed_builds} out of {total_builds} builds failed. This blocks deployments and wastes resources",
                recommendation="Investigate common failure patterns, improve test stability, add pre-commit hooks, review recent code changes",
                confidence=0.95,
                metadata={"failure_rate": failure_rate, "failed_count": failed_builds, "total_count": total_builds}
            ))
        
        return issues
    
    async def _analyze_test_reliability(self, tests: List[Dict]) -> List[Issue]:
        """Analyze test execution and reliability"""
        issues = []
        
        # Track flaky tests (tests that fail intermittently)
        test_results = {}
        for test in tests:
            test_name = test.get("name")
            if test_name:
                if test_name not in test_results:
                    test_results[test_name] = {"passed": 0, "failed": 0}
                
                if test.get("status") == "passed":
                    test_results[test_name]["passed"] += 1
                else:
                    test_results[test_name]["failed"] += 1
        
        # Identify flaky tests
        flaky_tests = []
        for test_name, results in test_results.items():
            total = results["passed"] + results["failed"]
            if total > 1 and results["failed"] > 0 and results["passed"] > 0:
                failure_rate = results["failed"] / total
                if 0.1 < failure_rate < 0.9:  # Intermittent failures
                    flaky_tests.append((test_name, failure_rate))
        
        if flaky_tests:
            issues.append(Issue(
                severity="high",
                category="reliability",
                title="Flaky Tests Detected",
                description=f"Found {len(flaky_tests)} flaky tests with intermittent failures",
                affected_component="Test Suite",
                impact="Flaky tests reduce confidence in test results, waste time investigating false failures, and may mask real issues",
                recommendation=f"Investigate and fix flaky tests: {', '.join([t[0] for t in flaky_tests[:3]])}{'...' if len(flaky_tests) > 3 else ''}. Common causes: timing issues, shared state, external dependencies",
                confidence=0.85,
                metadata={"flaky_tests": [{"name": t[0], "failure_rate": t[1]} for t in flaky_tests]}
            ))
        
        return issues
    
    async def _analyze_deployments(self, deployments: List[Dict]) -> List[Issue]:
        """Analyze deployment patterns and success rates"""
        issues = []
        
        if not deployments:
            return issues
        
        # Analyze deployment frequency and success
        recent_deployments = [
            d for d in deployments
            if d.get("timestamp")  # Filter valid deployments
        ]
        
        failed_deployments = [d for d in recent_deployments if d.get("status") == "failed"]
        
        if failed_deployments:
            failure_rate = len(failed_deployments) / len(recent_deployments)
            
            if failure_rate > 0.1:  # More than 10% deployment failures
                issues.append(Issue(
                    severity="critical",
                    category="reliability",
                    title="High Deployment Failure Rate",
                    description=f"Deployment failure rate is {failure_rate:.1%}",
                    affected_component="Deployment Pipeline",
                    impact="Failed deployments cause service disruptions, rollbacks, and delayed feature releases",
                    recommendation="Review deployment process, implement better pre-deployment testing, add automated rollback mechanisms, improve deployment scripts",
                    confidence=0.92,
                    metadata={
                        "failure_rate": failure_rate,
                        "failed_count": len(failed_deployments),
                        "total_count": len(recent_deployments)
                    }
                ))
        
        return issues
    
    async def _analyze_resource_usage(self, resources: Dict[str, Any]) -> List[Issue]:
        """Analyze resource utilization patterns"""
        issues = []
        
        # Check CPU usage
        cpu_usage = resources.get("cpu_usage", [])
        if cpu_usage:
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            max_cpu = max(cpu_usage)
            
            if max_cpu > 90:
                issues.append(Issue(
                    severity="high",
                    category="performance",
                    title="High CPU Usage",
                    description=f"CPU usage reached {max_cpu:.1f}% (average: {avg_cpu:.1f}%)",
                    affected_component="Build Infrastructure",
                    impact="High CPU usage causes build slowdowns, potential timeouts, and resource contention",
                    recommendation="Scale build agents, optimize build processes, distribute workload, investigate CPU-intensive operations",
                    confidence=0.88,
                    metadata={"max_cpu": max_cpu, "avg_cpu": avg_cpu}
                ))
        
        # Check memory usage
        memory_usage = resources.get("memory_usage", [])
        if memory_usage:
            avg_memory = sum(memory_usage) / len(memory_usage)
            max_memory = max(memory_usage)
            
            if max_memory > 85:
                issues.append(Issue(
                    severity="high",
                    category="performance",
                    title="High Memory Usage",
                    description=f"Memory usage reached {max_memory:.1f}% (average: {avg_memory:.1f}%)",
                    affected_component="Build Infrastructure",
                    impact="High memory usage can cause OOM errors, build failures, and system instability",
                    recommendation="Increase memory allocation, optimize memory-intensive processes, investigate memory leaks, add memory monitoring",
                    confidence=0.87,
                    metadata={"max_memory": max_memory, "avg_memory": avg_memory}
                ))
        
        return issues
    
    async def _analyze_security(self, security_scans: List[Dict]) -> List[Issue]:
        """Analyze security scan results"""
        issues = []
        
        for scan in security_scans:
            vulnerabilities = scan.get("vulnerabilities", [])
            
            # Group by severity
            critical_vulns = [v for v in vulnerabilities if v.get("severity") == "critical"]
            high_vulns = [v for v in vulnerabilities if v.get("severity") == "high"]
            
            if critical_vulns:
                issues.append(Issue(
                    severity="critical",
                    category="security",
                    title="Critical Security Vulnerabilities Detected",
                    description=f"Found {len(critical_vulns)} critical security vulnerabilities",
                    affected_component="Dependencies/Code",
                    impact="Critical vulnerabilities pose immediate security risks and must be addressed urgently",
                    recommendation=f"Update vulnerable dependencies immediately. CVEs: {', '.join([v.get('cve', 'Unknown') for v in critical_vulns[:3]])}",
                    confidence=0.98,
                    metadata={"critical_count": len(critical_vulns), "vulnerabilities": critical_vulns}
                ))
            
            if high_vulns and len(high_vulns) > 5:
                issues.append(Issue(
                    severity="high",
                    category="security",
                    title="Multiple High-Severity Vulnerabilities",
                    description=f"Found {len(high_vulns)} high-severity security vulnerabilities",
                    affected_component="Dependencies/Code",
                    impact="High-severity vulnerabilities require prompt attention to prevent potential security breaches",
                    recommendation="Review and update vulnerable dependencies, implement security scanning in CI/CD",
                    confidence=0.95,
                    metadata={"high_count": len(high_vulns)}
                ))
        
        return issues
    
    async def _analyze_kubernetes(self, k8s_data: Dict[str, Any]) -> List[Issue]:
        """Analyze Kubernetes cluster health and configuration"""
        issues = []
        
        if not k8s_data:
            return issues
        
        # Analyze pod health
        pods = k8s_data.get("pods", [])
        if pods:
            failed_pods = [p for p in pods if p.get("status") in ["CrashLoopBackOff", "Error", "Failed"]]
            pending_pods = [p for p in pods if p.get("status") == "Pending"]
            
            if failed_pods:
                issues.append(Issue(
                    severity="critical",
                    category="reliability",
                    title="Kubernetes Pod Failures",
                    description=f"{len(failed_pods)} pods are in failed state",
                    affected_component="Kubernetes Cluster",
                    impact=f"Failed pods indicate application crashes, configuration errors, or resource issues. Services may be degraded or unavailable",
                    recommendation=f"Investigate pod logs with 'kubectl logs <pod-name>'. Common causes: image pull errors, OOM kills, liveness probe failures, misconfigured environment variables",
                    confidence=0.95,
                    metadata={
                        "failed_pods": [p.get("name") for p in failed_pods[:5]],
                        "failed_count": len(failed_pods)
                    }
                ))
            
            if len(pending_pods) > 3:
                issues.append(Issue(
                    severity="high",
                    category="reliability",
                    title="Multiple Pods Stuck in Pending State",
                    description=f"{len(pending_pods)} pods cannot be scheduled",
                    affected_component="Kubernetes Scheduler",
                    impact="Pending pods indicate resource constraints or scheduling issues, preventing services from scaling or deploying",
                    recommendation="Check node resources with 'kubectl describe nodes'. Verify resource requests/limits, node selectors, taints/tolerations, and cluster autoscaling configuration",
                    confidence=0.90,
                    metadata={"pending_count": len(pending_pods)}
                ))
        
        # Analyze node health
        nodes = k8s_data.get("nodes", [])
        if nodes:
            unhealthy_nodes = [n for n in nodes if n.get("status") != "Ready"]
            
            if unhealthy_nodes:
                issues.append(Issue(
                    severity="critical",
                    category="reliability",
                    title="Unhealthy Kubernetes Nodes",
                    description=f"{len(unhealthy_nodes)} nodes are not in Ready state",
                    affected_component="Kubernetes Nodes",
                    impact="Unhealthy nodes reduce cluster capacity and may cause pod evictions or scheduling failures",
                    recommendation="Investigate node conditions with 'kubectl describe node <node-name>'. Check for disk pressure, memory pressure, network issues, or kubelet problems",
                    confidence=0.96,
                    metadata={
                        "unhealthy_nodes": [n.get("name") for n in unhealthy_nodes],
                        "unhealthy_count": len(unhealthy_nodes),
                        "total_nodes": len(nodes)
                    }
                ))
        
        # Analyze deployments
        deployments = k8s_data.get("deployments", [])
        if deployments:
            underscaled = []
            failed_deployments = []
            
            for deploy in deployments:
                desired = deploy.get("desired_replicas", 0)
                available = deploy.get("available_replicas", 0)
                
                if desired > 0 and available < desired:
                    if available == 0:
                        failed_deployments.append(deploy.get("name"))
                    else:
                        underscaled.append(deploy.get("name"))
            
            if failed_deployments:
                issues.append(Issue(
                    severity="critical",
                    category="reliability",
                    title="Kubernetes Deployments with Zero Availability",
                    description=f"{len(failed_deployments)} deployments have no available replicas",
                    affected_component="Kubernetes Deployments",
                    impact="Services are completely unavailable, causing outages and service disruptions",
                    recommendation=f"Check deployment status: 'kubectl describe deployment {failed_deployments[0] if failed_deployments else '<name>'}'. Review pod events, resource limits, and image availability",
                    confidence=0.98,
                    metadata={"failed_deployments": failed_deployments}
                ))
            
            if underscaled:
                issues.append(Issue(
                    severity="high",
                    category="reliability",
                    title="Under-Scaled Kubernetes Deployments",
                    description=f"{len(underscaled)} deployments running below desired replica count",
                    affected_component="Kubernetes Deployments",
                    impact="Reduced capacity and redundancy, potential performance degradation and single points of failure",
                    recommendation="Investigate why replicas aren't starting. Check resource availability, HPA configuration, and pod scheduling constraints",
                    confidence=0.88,
                    metadata={"underscaled_deployments": underscaled}
                ))
        
        # Analyze resource quotas and limits
        resource_usage = k8s_data.get("resource_usage", {})
        if resource_usage:
            cpu_usage_pct = resource_usage.get("cpu_usage_percent", 0)
            memory_usage_pct = resource_usage.get("memory_usage_percent", 0)
            
            if cpu_usage_pct > 85:
                issues.append(Issue(
                    severity="high",
                    category="performance",
                    title="High Kubernetes Cluster CPU Usage",
                    description=f"Cluster CPU usage at {cpu_usage_pct:.1f}%",
                    affected_component="Kubernetes Cluster Resources",
                    impact="High CPU usage may cause throttling, slow response times, and pod scheduling failures",
                    recommendation="Scale cluster nodes, optimize pod resource requests/limits, identify CPU-intensive workloads, consider horizontal pod autoscaling",
                    confidence=0.92,
                    metadata={"cpu_usage_percent": cpu_usage_pct}
                ))
            
            if memory_usage_pct > 85:
                issues.append(Issue(
                    severity="high",
                    category="performance",
                    title="High Kubernetes Cluster Memory Usage",
                    description=f"Cluster memory usage at {memory_usage_pct:.1f}%",
                    affected_component="Kubernetes Cluster Resources",
                    impact="High memory usage may trigger OOM kills, pod evictions, and prevent new pods from scheduling",
                    recommendation="Scale cluster nodes, review memory requests/limits, investigate memory leaks, enable cluster autoscaling",
                    confidence=0.92,
                    metadata={"memory_usage_percent": memory_usage_pct}
                ))
        
        # Analyze persistent volume claims
        pvcs = k8s_data.get("pvcs", [])
        if pvcs:
            pending_pvcs = [p for p in pvcs if p.get("status") == "Pending"]
            
            if pending_pvcs:
                issues.append(Issue(
                    severity="high",
                    category="reliability",
                    title="Pending Persistent Volume Claims",
                    description=f"{len(pending_pvcs)} PVCs unable to bind to volumes",
                    affected_component="Kubernetes Storage",
                    impact="Applications requiring persistent storage cannot start, blocking deployments and causing data access issues",
                    recommendation="Check storage class availability, verify volume provisioner is working, ensure sufficient storage capacity in cluster",
                    confidence=0.87,
                    metadata={"pending_pvcs": [p.get("name") for p in pending_pvcs]}
                ))
        
        # Analyze service mesh (if available)
        service_mesh = k8s_data.get("service_mesh", {})
        if service_mesh:
            error_rate = service_mesh.get("error_rate", 0)
            
            if error_rate > 0.05:  # More than 5% error rate
                issues.append(Issue(
                    severity="high",
                    category="reliability",
                    title="High Service Mesh Error Rate",
                    description=f"Service mesh reporting {error_rate:.1%} error rate",
                    affected_component="Service Mesh",
                    impact="High error rates indicate service communication failures, impacting application reliability",
                    recommendation="Review service mesh metrics, check for misconfigured routes, verify mTLS settings, investigate failing services",
                    confidence=0.85,
                    metadata={"error_rate": error_rate}
                ))
        
        return issues
    
    async def optimize(self, data: Dict[str, Any], issues: List[Issue]) -> List[Optimization]:
        """Generate optimization suggestions for DevOps pipelines"""
        logger.info("DevOpsAgent generating optimization suggestions")
        optimizations = []
        
        # Build optimization
        builds = data.get("builds", [])
        if builds:
            avg_duration = sum(b.get("duration", 0) for b in builds) / len(builds)
            
            if avg_duration > 300:  # More than 5 minutes
                optimizations.append(Optimization(
                    type="time",
                    title="Implement Build Caching",
                    description="Reduce build times by caching dependencies and build artifacts",
                    estimated_impact=f"Potential 30-50% reduction in build time (estimated saving: {avg_duration * 0.4:.0f}s per build)",
                    implementation_effort="medium",
                    priority=1,
                    steps=[
                        "Enable dependency caching in CI/CD system",
                        "Implement Docker layer caching for containerized builds",
                        "Cache compiled artifacts between builds",
                        "Use distributed caching for multi-stage builds"
                    ],
                    metrics_impact={"build_time_reduction": 0.4, "resource_usage_reduction": 0.2}
                ))
        
        # Test optimization
        test_issues = [i for i in issues if i.category == "reliability" and "test" in i.title.lower()]
        if test_issues:
            optimizations.append(Optimization(
                type="reliability",
                title="Improve Test Suite Reliability",
                description="Fix flaky tests and improve test infrastructure",
                estimated_impact="Increase confidence in test results, reduce false positives by 80%",
                implementation_effort="high",
                priority=2,
                steps=[
                    "Identify and isolate flaky tests",
                    "Add proper test isolation and cleanup",
                    "Implement retry logic for genuinely flaky external dependencies",
                    "Use test containers for consistent test environments",
                    "Add better error reporting and logging"
                ],
                metrics_impact={"test_reliability": 0.8, "false_positive_rate": -0.8}
            ))
        
        # Deployment optimization
        deployment_issues = [i for i in issues if "deployment" in i.title.lower()]
        if deployment_issues:
            optimizations.append(Optimization(
                type="reliability",
                title="Implement Blue-Green Deployments",
                description="Reduce deployment risks with zero-downtime deployment strategy",
                estimated_impact="Near-zero downtime deployments, instant rollback capability",
                implementation_effort="high",
                priority=1,
                steps=[
                    "Set up parallel production environments (blue/green)",
                    "Implement health checks and automated validation",
                    "Configure load balancer for traffic switching",
                    "Add automated rollback triggers",
                    "Implement comprehensive deployment monitoring"
                ],
                metrics_impact={"deployment_success_rate": 0.3, "rollback_time": -0.9}
            ))
        
        # Resource optimization
        resource_issues = [i for i in issues if i.category == "performance"]
        if resource_issues:
            optimizations.append(Optimization(
                type="cost",
                title="Optimize Resource Allocation",
                description="Right-size build agents and optimize resource usage",
                estimated_impact="20-40% reduction in infrastructure costs",
                implementation_effort="medium",
                priority=2,
                steps=[
                    "Analyze actual resource usage patterns",
                    "Implement autoscaling for build agents",
                    "Use spot instances for non-critical builds",
                    "Optimize container resource limits",
                    "Schedule resource-intensive jobs during off-peak hours"
                ],
                metrics_impact={"cost_reduction": 0.3, "resource_efficiency": 0.35}
            ))
        
        # Kubernetes optimizations
        k8s_issues = [i for i in issues if "kubernetes" in i.affected_component.lower()]
        if k8s_issues:
            optimizations.append(Optimization(
                type="reliability",
                title="Implement Kubernetes Best Practices",
                description="Apply production-ready Kubernetes configurations and observability",
                estimated_impact="50% reduction in pod failures, improved cluster stability",
                implementation_effort="medium",
                priority=2,
                steps=[
                    "Configure proper resource requests and limits for all pods",
                    "Implement liveness and readiness probes",
                    "Set up Horizontal Pod Autoscaler (HPA) for dynamic scaling",
                    "Configure Pod Disruption Budgets (PDB) for high availability",
                    "Implement network policies for security",
                    "Set up cluster monitoring with Prometheus/Grafana",
                    "Configure log aggregation (ELK/Loki)",
                    "Implement pod security policies/standards"
                ],
                metrics_impact={"pod_failure_rate": -0.5, "availability": 0.3, "recovery_time": -0.6}
            ))
            
            optimizations.append(Optimization(
                type="cost",
                title="Optimize Kubernetes Resource Utilization",
                description="Right-size pods and implement efficient autoscaling strategies",
                estimated_impact="30-40% reduction in infrastructure costs",
                implementation_effort="medium",
                priority=2,
                steps=[
                    "Analyze actual resource usage vs requests using metrics server",
                    "Right-size pod resource requests and limits based on actual usage",
                    "Implement Vertical Pod Autoscaler (VPA) for automatic sizing",
                    "Use cluster autoscaler for node-level scaling",
                    "Implement pod priority classes for critical workloads",
                    "Use spot/preemptible nodes for non-critical workloads",
                    "Schedule batch jobs during off-peak hours",
                    "Implement resource quotas per namespace"
                ],
                metrics_impact={"cost_reduction": 0.35, "resource_waste": -0.45}
            ))
            
            optimizations.append(Optimization(
                type="performance",
                title="Improve Kubernetes Deployment Speed and Reliability",
                description="Optimize container images and deployment strategies",
                estimated_impact="50% faster deployments, zero-downtime updates",
                implementation_effort="medium",
                priority=3,
                steps=[
                    "Optimize container images (multi-stage builds, minimize layers)",
                    "Implement image caching strategies",
                    "Use rolling updates with proper readiness checks",
                    "Configure appropriate terminationGracePeriodSeconds",
                    "Implement blue-green or canary deployment strategies",
                    "Use init containers for setup tasks",
                    "Optimize image pull policy (IfNotPresent)",
                    "Set up local container registry cache"
                ],
                metrics_impact={"deployment_time": -0.5, "deployment_success_rate": 0.25}
            ))
        
        return sorted(optimizations, key=lambda x: x.priority)
