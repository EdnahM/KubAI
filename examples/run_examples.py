"""Example usage of the Pipeline Optimizer"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator import PipelineOrchestrator
from src.config import Config


async def example_analysis():
    """Example: One-time pipeline analysis"""
    print("=" * 60)
    print("Example 1: One-Time Pipeline Analysis")
    print("=" * 60)
    
    # Load configuration
    config = Config.load("config/config.yaml")
    
    # Create orchestrator
    orchestrator = PipelineOrchestrator(config)
    
    # Analyze both DevOps and MLOps pipelines
    results = await orchestrator.analyze_pipelines(
        pipeline_type="both",
        source=None  # Will use simulated data
    )
    
    # Display summary
    print("\n📊 Analysis Summary:")
    print("-" * 60)
    
    if results.get("devops"):
        devops_summary = results["devops"]["summary"]
        print(f"\nDevOps Pipeline:")
        print(f"  Total Issues: {devops_summary['total']}")
        print(f"  By Severity: {devops_summary['by_severity']}")
        print(f"  By Category: {devops_summary['by_category']}")
    
    if results.get("mlops"):
        mlops_summary = results["mlops"]["summary"]
        print(f"\nMLOps Pipeline:")
        print(f"  Total Issues: {mlops_summary['total']}")
        print(f"  By Severity: {mlops_summary['by_severity']}")
        print(f"  By Category: {mlops_summary['by_category']}")
    
    # Generate report
    report_path = orchestrator.generate_report(results, output_dir="reports")
    print(f"\n📄 Full report saved to: {report_path}")
    
    await orchestrator.shutdown()


async def example_optimization():
    """Example: Generate optimization suggestions"""
    print("\n" + "=" * 60)
    print("Example 2: Optimization Suggestions")
    print("=" * 60)
    
    config = Config.load("config/config.yaml")
    orchestrator = PipelineOrchestrator(config)
    
    # Analyze and optimize
    results = await orchestrator.analyze_and_optimize(
        pipeline_type="both",
        source=None
    )
    
    # Display optimization summary
    print("\n🔧 Optimization Suggestions:")
    print("-" * 60)
    
    if results.get("optimizations", {}).get("devops"):
        print(f"\nDevOps Optimizations: {len(results['optimizations']['devops'])}")
        for i, opt in enumerate(results['optimizations']['devops'][:3], 1):
            print(f"  {i}. {opt['title']} (Priority: {opt['priority']})")
    
    if results.get("optimizations", {}).get("mlops"):
        print(f"\nMLOps Optimizations: {len(results['optimizations']['mlops'])}")
        for i, opt in enumerate(results['optimizations']['mlops'][:3], 1):
            print(f"  {i}. {opt['title']} (Priority: {opt['priority']})")
    
    # Generate optimization report
    report_path = orchestrator.generate_optimization_report(results, output_dir="reports")
    print(f"\n📄 Optimization plan saved to: {report_path}")
    
    await orchestrator.shutdown()


async def example_issue_details():
    """Example: Display detailed issue information"""
    print("\n" + "=" * 60)
    print("Example 3: Detailed Issue Analysis")
    print("=" * 60)
    
    config = Config.load("config/config.yaml")
    orchestrator = PipelineOrchestrator(config)
    
    results = await orchestrator.analyze_pipelines(pipeline_type="both")
    
    # Display critical and high severity issues
    print("\n🔴 Critical and High Severity Issues:")
    print("-" * 60)
    
    issue_count = 0
    
    if results.get("devops"):
        for issue in results["devops"]["issues"]:
            if issue["severity"] in ["critical", "high"]:
                issue_count += 1
                print(f"\n{issue_count}. [{issue['severity'].upper()}] {issue['title']}")
                print(f"   Component: {issue['affected_component']}")
                print(f"   Impact: {issue['impact'][:100]}...")
                print(f"   Recommendation: {issue['recommendation'][:100]}...")
    
    if results.get("mlops"):
        for issue in results["mlops"]["issues"]:
            if issue["severity"] in ["critical", "high"]:
                issue_count += 1
                print(f"\n{issue_count}. [{issue['severity'].upper()}] {issue['title']}")
                print(f"   Component: {issue['affected_component']}")
                print(f"   Impact: {issue['impact'][:100]}...")
                print(f"   Recommendation: {issue['recommendation'][:100]}...")
    
    if issue_count == 0:
        print("\n✅ No critical or high severity issues found!")
    
    await orchestrator.shutdown()


async def main():
    """Run all examples"""
    print("\n🤖 AI-Powered Pipeline Optimizer - Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await example_analysis()
        await example_optimization()
        await example_issue_details()
        
        print("\n" + "=" * 60)
        print("✅ All examples completed successfully!")
        print("=" * 60)
        print("\nCheck the 'reports/' directory for generated reports.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
