#!/usr/bin/env python
"""Run the LHC analysis pipeline"""

import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.pipeline import LHCDataPipeline


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description="LHC Open Data Pipeline"
    )
    
    parser.add_argument(
        '--analysis', '-a',
        type=str,
        default='higgs_search',
        choices=['higgs_search', 'dijet', 'ttbar'],
        help='Type of analysis'
    )
    
    parser.add_argument(
        '--sample', '-s',
        action='store_true',
        help='Run with sample data'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate without executing'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('results'),
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s: %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting pipeline: {args.analysis}")
    
    try:
        # Create and run pipeline
        pipeline = LHCDataPipeline(output_dir=args.output)
        results_df, metrics = pipeline.run(
            analysis_type=args.analysis,
            dry_run=args.dry_run
        )
        
        logger.info(f"✓ Pipeline complete!")
        logger.info(f"  Selected events: {len(results_df)}")
        logger.info(f"  Runtime: {metrics.total_runtime_seconds:.1f}s")
        
        return 0
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())