#!/usr/bin/env python
"""Parse and process data"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_mock_dataset(n_events=10000):
    """Create mock dataset for testing"""
    return pd.DataFrame({
        'event': range(n_events),
        'run': 160404,
        'nMuon': np.random.randint(0, 4, n_events),
        'nElectron': np.random.randint(0, 4, n_events),
        'nJet': np.random.randint(0, 8, n_events),
    })


def main():
    logger.info("Creating mock data...")
    
    df = create_mock_dataset(10000)
    
    # Save to Parquet
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "events.parquet"
    df.to_parquet(output_file, compression="snappy")
    
    logger.info(f"✓ Saved {len(df):,} events to {output_file}")
    logger.info(f"  Columns: {len(df.columns)}")
    logger.info(f"  Size: {output_file.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()