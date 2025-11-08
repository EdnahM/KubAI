#!/usr/bin/env python3
"""
AI-Powered DevOps and MLOps Pipeline Optimizer
Main application entry point
"""

import asyncio
import argparse
from datetime import datetime
from pathlib import Path

from src.orchestrator import PipelineOrchestrator
from src.config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="AI-powered DevOps/MLOps pipeline issue detection and optimization"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["analyze", "monitor", "optimize"],
        default="analyze",
        help="Operation mode: analyze (one-time), monitor (continuous), optimize (suggest fixes)"
    )
    parser.add_argument(
        "--pipeline-type",
        type=str,
        choices=["devops", "mlops", "both"],
        default="both",
        help="Type of pipeline to analyze"
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Pipeline source (e.g., Jenkins URL, GitLab CI, Kubernetes cluster)"
    )
    parser.add_argument(
        "--report-output",
        type=str,
        default="reports",
        help="Directory for output reports"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.load(args.config)
    
    # Initialize orchestrator
    orchestrator = PipelineOrchestrator(config)
    
    logger.info(f"Starting pipeline optimizer in {args.mode} mode")
    logger.info(f"Pipeline type: {args.pipeline_type}")
    
    try:
        if args.mode == "analyze":
            # One-time analysis
            results = await orchestrator.analyze_pipelines(
                pipeline_type=args.pipeline_type,
                source=args.source
            )
            
            # Generate report
            report_path = orchestrator.generate_report(
                results,
                output_dir=args.report_output
            )
            logger.info(f"Analysis complete. Report saved to: {report_path}")
            
        elif args.mode == "monitor":
            # Continuous monitoring
            logger.info("Starting continuous monitoring mode...")
            await orchestrator.start_monitoring(
                pipeline_type=args.pipeline_type,
                source=args.source
            )
            
        elif args.mode == "optimize":
            # Analyze and suggest optimizations
            results = await orchestrator.analyze_and_optimize(
                pipeline_type=args.pipeline_type,
                source=args.source
            )
            
            # Generate optimization report
            report_path = orchestrator.generate_optimization_report(
                results,
                output_dir=args.report_output
            )
            logger.info(f"Optimization suggestions saved to: {report_path}")
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        raise
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
