"""Configuration management for the pipeline optimizer"""

import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AgentConfig:
    """Configuration for AI agents"""
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None


@dataclass
class MonitoringConfig:
    """Configuration for monitoring"""
    interval: int = 300  # seconds
    alert_threshold: Dict[str, float] = field(default_factory=lambda: {
        "failure_rate": 0.1,
        "duration_increase": 1.5,
        "resource_usage": 0.8
    })
    enable_notifications: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])


@dataclass
class PipelineConfig:
    """Configuration for pipeline analysis"""
    devops_sources: List[str] = field(default_factory=list)
    mlops_sources: List[str] = field(default_factory=list)
    max_history: int = 100  # Number of pipeline runs to analyze
    analysis_depth: str = "detailed"  # basic, detailed, comprehensive


@dataclass
class Config:
    """Main configuration class"""
    agent: AgentConfig = field(default_factory=AgentConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    
    @classmethod
    def load(cls, config_path: str) -> "Config":
        """Load configuration from YAML file"""
        path = Path(config_path)
        
        if not path.exists():
            # Return default configuration
            return cls()
        
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        return cls(
            agent=AgentConfig(**data.get("agent", {})),
            monitoring=MonitoringConfig(**data.get("monitoring", {})),
            pipeline=PipelineConfig(**data.get("pipeline", {}))
        )
    
    def save(self, config_path: str):
        """Save configuration to YAML file"""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "agent": {
                "model": self.agent.model,
                "temperature": self.agent.temperature,
                "max_tokens": self.agent.max_tokens
            },
            "monitoring": {
                "interval": self.monitoring.interval,
                "alert_threshold": self.monitoring.alert_threshold,
                "enable_notifications": self.monitoring.enable_notifications,
                "notification_channels": self.monitoring.notification_channels
            },
            "pipeline": {
                "devops_sources": self.pipeline.devops_sources,
                "mlops_sources": self.pipeline.mlops_sources,
                "max_history": self.pipeline.max_history,
                "analysis_depth": self.pipeline.analysis_depth
            }
        }
        
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
