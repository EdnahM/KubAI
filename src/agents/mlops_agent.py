"""AI Agent specialized in MLOps pipeline analysis"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import statistics

from .base_agent import BaseAgent, Issue, Optimization
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class MLOpsAgent(BaseAgent):
    """Agent for analyzing MLOps pipelines (model training, deployment, monitoring)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.metric_thresholds = self._load_metric_thresholds()
    
    def _load_metric_thresholds(self) -> Dict[str, Any]:
        """Load metric thresholds for ML pipeline analysis"""
        return {
            "model_performance": {
                "accuracy_drop": 0.05,  # 5% drop is concerning
                "f1_score_threshold": 0.7,
                "precision_threshold": 0.7,
                "recall_threshold": 0.7
            },
            "training": {
                "max_duration": 3600 * 4,  # 4 hours
                "gpu_utilization_min": 0.6,  # 60% minimum
                "convergence_check": True
            },
            "data": {
                "drift_threshold": 0.1,  # 10% drift
                "quality_threshold": 0.95,  # 95% data quality
                "missing_values_threshold": 0.05  # 5% missing
            },
            "inference": {
                "latency_p95": 100,  # 100ms for p95
                "throughput_min": 100,  # requests per second
                "error_rate_max": 0.01  # 1% error rate
            }
        }
    
    async def analyze(self, data: Dict[str, Any]) -> List[Issue]:
        """Analyze MLOps pipeline data"""
        logger.info("MLOpsAgent analyzing ML pipeline data")
        issues = []
        
        # Analyze model performance
        performance_issues = await self._analyze_model_performance(data.get("model_metrics", []))
        issues.extend(performance_issues)
        
        # Analyze training efficiency
        training_issues = await self._analyze_training(data.get("training_runs", []))
        issues.extend(training_issues)
        
        # Analyze data quality and drift
        data_issues = await self._analyze_data_quality(data.get("data_metrics", {}))
        issues.extend(data_issues)
        
        # Analyze model serving/inference
        inference_issues = await self._analyze_inference(data.get("inference_metrics", {}))
        issues.extend(inference_issues)
        
        # Analyze experiment tracking
        experiment_issues = await self._analyze_experiments(data.get("experiments", []))
        issues.extend(experiment_issues)
        
        return self._prioritize_issues(issues)
    
    async def _analyze_model_performance(self, model_metrics: List[Dict]) -> List[Issue]:
        """Analyze model performance metrics over time"""
        issues = []
        
        if not model_metrics or len(model_metrics) < 2:
            return issues
        
        # Sort by timestamp to analyze trends
        sorted_metrics = sorted(model_metrics, key=lambda x: x.get("timestamp", ""))
        
        # Check for performance degradation
        if len(sorted_metrics) >= 2:
            recent_metrics = sorted_metrics[-5:]  # Last 5 evaluations
            older_metrics = sorted_metrics[-10:-5] if len(sorted_metrics) >= 10 else sorted_metrics[:-5]
            
            if older_metrics and recent_metrics:
                # Compare accuracy
                recent_accuracy = statistics.mean([m.get("accuracy", 0) for m in recent_metrics])
                older_accuracy = statistics.mean([m.get("accuracy", 0) for m in older_metrics])
                
                accuracy_drop = older_accuracy - recent_accuracy
                
                if accuracy_drop > self.metric_thresholds["model_performance"]["accuracy_drop"]:
                    issues.append(Issue(
                        severity="high",
                        category="quality",
                        title="Model Performance Degradation Detected",
                        description=f"Model accuracy dropped by {accuracy_drop:.1%} from {older_accuracy:.2%} to {recent_accuracy:.2%}",
                        affected_component="ML Model",
                        impact="Degraded model performance affects prediction quality and business outcomes",
                        recommendation="Investigate data drift, retrain model with recent data, review feature engineering, check for concept drift",
                        confidence=0.88,
                        metadata={
                            "recent_accuracy": recent_accuracy,
                            "older_accuracy": older_accuracy,
                            "drop": accuracy_drop
                        }
                    ))
        
        # Check latest model performance
        latest_metrics = sorted_metrics[-1]
        accuracy = latest_metrics.get("accuracy", 0)
        f1_score = latest_metrics.get("f1_score", 0)
        
        if f1_score < self.metric_thresholds["model_performance"]["f1_score_threshold"]:
            issues.append(Issue(
                severity="medium",
                category="quality",
                title="Low Model F1 Score",
                description=f"Current F1 score is {f1_score:.2f}, below threshold of {self.metric_thresholds['model_performance']['f1_score_threshold']}",
                affected_component="ML Model",
                impact="Low F1 score indicates poor balance between precision and recall",
                recommendation="Review class imbalance, adjust decision threshold, improve feature selection, collect more training data for underrepresented classes",
                confidence=0.85,
                metadata={"f1_score": f1_score, "accuracy": accuracy}
            ))
        
        return issues
    
    async def _analyze_training(self, training_runs: List[Dict]) -> List[Issue]:
        """Analyze training efficiency and patterns"""
        issues = []
        
        if not training_runs:
            return issues
        
        # Analyze training duration
        durations = [run.get("duration", 0) for run in training_runs if run.get("status") == "completed"]
        if durations:
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            
            if avg_duration > self.metric_thresholds["training"]["max_duration"]:
                issues.append(Issue(
                    severity="medium",
                    category="performance",
                    title="Long Training Times",
                    description=f"Average training time is {avg_duration/3600:.1f} hours",
                    affected_component="Training Pipeline",
                    impact="Long training times slow down model iteration and increase costs",
                    recommendation="Optimize training code, use mixed precision training, implement gradient accumulation, consider distributed training, profile training loop for bottlenecks",
                    confidence=0.82,
                    metadata={"avg_duration": avg_duration, "max_duration": max_duration}
                ))
        
        # Analyze GPU utilization
        gpu_utilizations = []
        for run in training_runs:
            gpu_util = run.get("gpu_utilization", [])
            if gpu_util:
                avg_gpu = statistics.mean(gpu_util)
                gpu_utilizations.append(avg_gpu)
        
        if gpu_utilizations:
            avg_gpu_util = statistics.mean(gpu_utilizations)
            
            if avg_gpu_util < self.metric_thresholds["training"]["gpu_utilization_min"]:
                issues.append(Issue(
                    severity="medium",
                    category="cost",
                    title="Low GPU Utilization",
                    description=f"Average GPU utilization is {avg_gpu_util:.1%}",
                    affected_component="Training Infrastructure",
                    impact=f"Underutilized GPUs waste {(1-avg_gpu_util)*100:.0f}% of compute resources and increase training costs",
                    recommendation="Increase batch size, optimize data loading pipeline, use data prefetching, profile GPU bottlenecks, consider mixed precision training",
                    confidence=0.90,
                    metadata={"avg_gpu_utilization": avg_gpu_util}
                ))
        
        # Check for failed training runs
        failed_runs = [run for run in training_runs if run.get("status") == "failed"]
        failure_rate = len(failed_runs) / len(training_runs) if training_runs else 0
        
        if failure_rate > 0.1:  # More than 10% failure rate
            issues.append(Issue(
                severity="high",
                category="reliability",
                title="High Training Failure Rate",
                description=f"Training failure rate is {failure_rate:.1%}",
                affected_component="Training Pipeline",
                impact="Training failures waste resources and delay model development",
                recommendation="Add robust error handling, implement checkpointing, validate data before training, add memory monitoring, review training logs for common errors",
                confidence=0.87,
                metadata={"failure_rate": failure_rate, "failed_count": len(failed_runs)}
            ))
        
        return issues
    
    async def _analyze_data_quality(self, data_metrics: Dict[str, Any]) -> List[Issue]:
        """Analyze data quality and drift"""
        issues = []
        
        # Check for data drift
        drift_score = data_metrics.get("drift_score", 0)
        if drift_score > self.metric_thresholds["data"]["drift_threshold"]:
            issues.append(Issue(
                severity="high",
                category="quality",
                title="Data Drift Detected",
                description=f"Data drift score is {drift_score:.2f}, exceeding threshold",
                affected_component="Input Data",
                impact="Data drift causes model performance degradation and unreliable predictions",
                recommendation="Retrain model with recent data, implement continuous monitoring, set up automated retraining pipeline, investigate root cause of drift",
                confidence=0.92,
                metadata={"drift_score": drift_score}
            ))
        
        # Check data quality
        quality_score = data_metrics.get("quality_score", 1.0)
        if quality_score < self.metric_thresholds["data"]["quality_threshold"]:
            issues.append(Issue(
                severity="medium",
                category="quality",
                title="Low Data Quality",
                description=f"Data quality score is {quality_score:.2%}",
                affected_component="Input Data",
                impact="Low data quality leads to poor model performance and unreliable predictions",
                recommendation="Implement data validation rules, add data quality checks in pipeline, investigate and fix data collection issues, add data cleaning steps",
                confidence=0.85,
                metadata={"quality_score": quality_score}
            ))
        
        # Check missing values
        missing_rate = data_metrics.get("missing_value_rate", 0)
        if missing_rate > self.metric_thresholds["data"]["missing_values_threshold"]:
            issues.append(Issue(
                severity="medium",
                category="quality",
                title="High Missing Value Rate",
                description=f"Missing value rate is {missing_rate:.1%}",
                affected_component="Input Data",
                impact="High missing value rate reduces model training effectiveness and prediction coverage",
                recommendation="Implement proper imputation strategies, investigate data collection issues, consider dropping features with excessive missing values, add data validation",
                confidence=0.80,
                metadata={"missing_rate": missing_rate}
            ))
        
        return issues
    
    async def _analyze_inference(self, inference_metrics: Dict[str, Any]) -> List[Issue]:
        """Analyze model inference/serving metrics"""
        issues = []
        
        # Check latency
        latency_p95 = inference_metrics.get("latency_p95", 0)
        if latency_p95 > self.metric_thresholds["inference"]["latency_p95"]:
            issues.append(Issue(
                severity="high",
                category="performance",
                title="High Inference Latency",
                description=f"P95 inference latency is {latency_p95:.0f}ms",
                affected_component="Model Serving",
                impact="High latency degrades user experience and may violate SLAs",
                recommendation="Optimize model (quantization, pruning), use model serving optimizations (batching, caching), scale horizontally, consider lighter model architecture",
                confidence=0.88,
                metadata={"latency_p95": latency_p95}
            ))
        
        # Check throughput
        throughput = inference_metrics.get("throughput", 0)
        if throughput < self.metric_thresholds["inference"]["throughput_min"]:
            issues.append(Issue(
                severity="medium",
                category="performance",
                title="Low Inference Throughput",
                description=f"Inference throughput is {throughput:.0f} req/s",
                affected_component="Model Serving",
                impact="Low throughput limits system capacity and may require overprovisioning",
                recommendation="Enable request batching, optimize preprocessing, use GPU inference, implement model parallelism, review resource allocation",
                confidence=0.83,
                metadata={"throughput": throughput}
            ))
        
        # Check error rate
        error_rate = inference_metrics.get("error_rate", 0)
        if error_rate > self.metric_thresholds["inference"]["error_rate_max"]:
            issues.append(Issue(
                severity="critical",
                category="reliability",
                title="High Inference Error Rate",
                description=f"Inference error rate is {error_rate:.1%}",
                affected_component="Model Serving",
                impact="High error rate indicates serving instability and affects user experience",
                recommendation="Investigate error logs, add input validation, implement fallback mechanisms, improve error handling, monitor model serving health",
                confidence=0.95,
                metadata={"error_rate": error_rate}
            ))
        
        return issues
    
    async def _analyze_experiments(self, experiments: List[Dict]) -> List[Issue]:
        """Analyze experiment tracking and management"""
        issues = []
        
        if not experiments:
            return issues
        
        # Check for untagged experiments
        untagged = [e for e in experiments if not e.get("tags")]
        if len(untagged) / len(experiments) > 0.3:  # More than 30% untagged
            issues.append(Issue(
                severity="low",
                category="quality",
                title="Poor Experiment Organization",
                description=f"{len(untagged)} out of {len(experiments)} experiments lack proper tagging",
                affected_component="Experiment Tracking",
                impact="Poor organization makes it difficult to track progress and reproduce results",
                recommendation="Implement consistent tagging strategy, add metadata to experiments, use meaningful names, document experiment purpose",
                confidence=0.75,
                metadata={"untagged_count": len(untagged), "total_count": len(experiments)}
            ))
        
        return issues
    
    async def optimize(self, data: Dict[str, Any], issues: List[Issue]) -> List[Optimization]:
        """Generate optimization suggestions for MLOps pipelines"""
        logger.info("MLOpsAgent generating optimization suggestions")
        optimizations = []
        
        # Training optimization
        training_runs = data.get("training_runs", [])
        if training_runs:
            optimizations.append(Optimization(
                type="performance",
                title="Implement Distributed Training",
                description="Speed up training with data-parallel or model-parallel distributed training",
                estimated_impact="50-70% reduction in training time for large models",
                implementation_effort="high",
                priority=2,
                steps=[
                    "Evaluate distributed training frameworks (PyTorch DDP, Horovod, DeepSpeed)",
                    "Refactor training code for distributed execution",
                    "Set up multi-GPU or multi-node infrastructure",
                    "Optimize data loading for distributed training",
                    "Implement gradient accumulation for effective large batch training",
                    "Test and validate distributed training convergence"
                ],
                metrics_impact={"training_time_reduction": 0.6, "throughput_increase": 2.5}
            ))
        
        # Model optimization
        performance_issues = [i for i in issues if i.category == "performance" and "inference" in i.title.lower()]
        if performance_issues:
            optimizations.append(Optimization(
                type="performance",
                title="Optimize Model for Inference",
                description="Apply model optimization techniques to reduce latency and improve throughput",
                estimated_impact="30-50% latency reduction, 2-3x throughput improvement",
                implementation_effort="medium",
                priority=1,
                steps=[
                    "Apply model quantization (INT8 or mixed precision)",
                    "Prune unnecessary weights and connections",
                    "Use ONNX Runtime or TensorRT for optimized serving",
                    "Implement dynamic batching",
                    "Enable model caching for repeated inputs",
                    "Profile and optimize preprocessing pipeline"
                ],
                metrics_impact={"latency_reduction": 0.4, "throughput_increase": 2.0, "cost_reduction": 0.3}
            ))
        
        # Data pipeline optimization
        data_issues = [i for i in issues if i.category == "quality"]
        if data_issues:
            optimizations.append(Optimization(
                type="quality",
                title="Implement Automated Data Quality Monitoring",
                description="Set up continuous data quality monitoring and alerting",
                estimated_impact="Early detection of data issues, 80% reduction in data-related model failures",
                implementation_effort="medium",
                priority=1,
                steps=[
                    "Define data quality metrics and thresholds",
                    "Implement automated data validation pipeline",
                    "Set up data drift detection monitors",
                    "Create alerting for quality violations",
                    "Build data profiling dashboard",
                    "Implement automated data quality reports"
                ],
                metrics_impact={"data_issue_detection": 0.8, "model_reliability": 0.3}
            ))
        
        # MLOps infrastructure
        optimizations.append(Optimization(
            type="reliability",
            title="Implement Automated Model Retraining Pipeline",
            description="Set up automated retraining triggered by performance degradation or data drift",
            estimated_impact="Maintain model performance automatically, reduce manual intervention by 90%",
            implementation_effort="high",
            priority=2,
            steps=[
                "Define retraining triggers (drift, performance drop, schedule)",
                "Implement automated data preparation pipeline",
                "Set up automated training with hyperparameter optimization",
                "Implement automated model validation and testing",
                "Create automated deployment with A/B testing",
                "Set up rollback mechanisms for failed deployments",
                "Implement continuous monitoring and alerting"
            ],
            metrics_impact={"model_freshness": 0.9, "manual_effort": -0.9, "downtime": -0.5}
        ))
        
        # Cost optimization
        optimizations.append(Optimization(
            type="cost",
            title="Optimize Training and Inference Costs",
            description="Reduce cloud costs through resource optimization and efficient scheduling",
            estimated_impact="25-40% reduction in ML infrastructure costs",
            implementation_effort="medium",
            priority=3,
            steps=[
                "Use spot instances for training workloads",
                "Implement auto-scaling for inference",
                "Optimize model size and complexity",
                "Schedule training during off-peak hours",
                "Use reserved instances for baseline capacity",
                "Implement resource usage monitoring and alerts"
            ],
            metrics_impact={"cost_reduction": 0.35, "resource_efficiency": 0.4}
        ))
        
        return sorted(optimizations, key=lambda x: x.priority)
