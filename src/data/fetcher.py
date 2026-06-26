"""
data_fetcher.py & data_parser.py - Download and parse CERN Open Data ROOT files
Automatically fetch datasets and convert ROOT → Pandas/Parquet
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import urllib.request
import urllib.error
import tempfile

import pandas as pd
import numpy as np

try:
    import uproot
    HAS_UPROOT = True
except ImportError:
    HAS_UPROOT = False

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# DATA FETCHER
# ============================================================================

@dataclass
class DataFile:
    """Represents a single ROOT data file"""
    filename: str
    url: str
    size_bytes: int
    checksum: str
    date_added: str


class DataFetcher:
    """
    Downloads data from CERN Open Data Portal
    Handles resumable downloads, integrity checking, and caching
    """
    
    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.cache_dir / "manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load or create manifest of downloaded files"""
        if self.manifest_file.exists():
            with open(self.manifest_file) as f:
                return json.load(f)
        return {"files": {}, "metadata": {"created": datetime.now().isoformat()}}
    
    def _save_manifest(self):
        """Save manifest to disk"""
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    @staticmethod
    def _checksum_file(filepath: Path, algorithm: str = "md5") -> str:
        """Calculate file checksum"""
        hasher = hashlib.new(algorithm)
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _download_file(self, url: str, destination: Path, resume: bool = True) -> bool:
        """
        Download file from URL with resume support
        Returns True if successful
        """
        logger.info(f"Downloading {url} → {destination}")
        
        try:
            # Resume download if file already exists and resume=True
            if destination.exists() and resume:
                existing_size = destination.stat().st_size
                request = urllib.request.Request(url)
                request.add_header('Range', f'bytes={existing_size}-')
            else:
                request = urllib.request.Request(url)
            
            # Download with progress reporting
            with urllib.request.urlopen(request) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(destination, 'ab' if resume else 'wb') as f:
                    while chunk := response.read(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            logger.debug(f"Progress: {percent:.1f}%")
            
            logger.info(f"Download complete: {destination}")
            return True
            
        except urllib.error.URLError as e:
            logger.error(f"Download failed: {e}")
            return False
    
    def fetch_cms_2011_sample(self, n_files: int = 10) -> List[Path]:
        """
        Fetch sample of CMS 2011 data (small, for testing)
        Returns list of file paths
        
        Real URLs (example):
        - http://opendata.cern.ch/record/22/files/Zmumu_2011.root
        - http://opendata.cern.ch/record/23/files/Zee_2011.root
        """
        
        # Example manifest - in real implementation, fetch from CERN API
        cms_sample_urls = [
            "http://opendata.cern.ch/eos/opendata/cms/Run2011A/DoubleMuon/AOD/12Oct2013-v1/00000/0015C0F1-4FF8-E211-8E65-002264FFF722.root",
            "http://opendata.cern.ch/eos/opendata/cms/Run2011A/DoubleElectron/AOD/12Oct2013-v1/00000/00002B09-61F8-E211-9456-003048F259CB.root",
            # ... more URLs ...
        ]
        
        downloaded_files = []
        
        for i, url in enumerate(cms_sample_urls[:n_files]):
            filename = url.split('/')[-1]
            filepath = self.cache_dir / filename
            
            # Check if already cached
            if filename in self.manifest["files"]:
                logger.info(f"Using cached file: {filename}")
                downloaded_files.append(filepath)
                continue
            
            # Download if not cached
            if self._download_file(url, filepath):
                checksum = self._checksum_file(filepath)
                self.manifest["files"][filename] = {
                    "url": url,
                    "size": filepath.stat().st_size,
                    "checksum": checksum,
                    "downloaded": datetime.now().isoformat()
                }
                self._save_manifest()
                downloaded_files.append(filepath)
        
        return downloaded_files
    
    def get_cached_files(self) -> List[Path]:
        """List all cached ROOT files"""
        return list(self.cache_dir.glob("*.root"))


# ============================================================================
# DATA PARSER
# ============================================================================

class DataParser:
    """
    Parse ROOT files using uproot
    Convert to Pandas DataFrames and Parquet for fast iteration
    """
    
    def __init__(self, output_dir: Path = None):
        if not HAS_UPROOT:
            raise ImportError("uproot not installed. Run: pip install uproot")
        
        self.output_dir = output_dir or Path("data/processed")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_root_file(
        self,
        filepath: Path,
        tree_name: str = "Events",
        branches: Optional[List[str]] = None,
        entry_start: int = 0,
        entry_stop: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Parse ROOT file and return as Pandas DataFrame
        
        Args:
            filepath: Path to ROOT file
            tree_name: Name of ROOT tree (usually "Events")
            branches: List of branch names to read (None = all)
            entry_start: Starting entry index
            entry_stop: Ending entry index (None = all)
        
        Returns:
            DataFrame with all selected branches
        """
        logger.info(f"Parsing {filepath}")
        
        try:
            with uproot.open(filepath) as file:
                tree = file[tree_name]
                
                # Get available branches
                available_branches = tree.keys()
                logger.debug(f"Available branches: {len(available_branches)}")
                
                # Select branches to read
                if branches is None:
                    branches_to_read = available_branches
                else:
                    branches_to_read = [b for b in branches if b in available_branches]
                    missing = set(branches) - set(branches_to_read)
                    if missing:
                        logger.warning(f"Missing branches: {missing}")
                
                # Read data
                logger.info(f"Reading {len(branches_to_read)} branches...")
                arrays = tree.arrays(
                    expressions=branches_to_read,
                    entry_start=entry_start,
                    entry_stop=entry_stop,
                    library="pd"
                )
                
                df = pd.DataFrame(arrays)
                logger.info(f"Parsed {len(df)} events")
                return df
        
        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            raise
    
    def batch_parse_files(
        self,
        filepaths: List[Path],
        tree_name: str = "Events",
        output_format: str = "parquet"
    ) -> pd.DataFrame:
        """
        Parse multiple ROOT files and combine into single DataFrame
        Optionally save to disk
        
        Args:
            filepaths: List of ROOT files to parse
            tree_name: ROOT tree name
            output_format: "parquet", "csv", or "hdf5"
        
        Returns:
            Combined DataFrame
        """
        dfs = []
        
        for filepath in filepaths:
            df = self.parse_root_file(filepath, tree_name=tree_name)
            df['_source_file'] = str(filepath)  # Track source
            dfs.append(df)
        
        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Combined {len(dfs)} files into {len(combined_df)} events")
        
        # Save to disk
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == "parquet":
            output_path = self.output_dir / f"combined_{timestamp}.parquet"
            combined_df.to_parquet(output_path, compression="snappy")
            logger.info(f"Saved to {output_path}")
        
        elif output_format == "csv":
            output_path = self.output_dir / f"combined_{timestamp}.csv"
            combined_df.to_csv(output_path, index=False)
            logger.info(f"Saved to {output_path}")
        
        elif output_format == "hdf5":
            output_path = self.output_dir / f"combined_{timestamp}.h5"
            combined_df.to_hdf(output_path, key='data', mode='w')
            logger.info(f"Saved to {output_path}")
        
        return combined_df
    
    @staticmethod
    def inspect_root_file(filepath: Path, tree_name: str = "Events") -> Dict:
        """Inspect ROOT file structure without loading data"""
        logger.info(f"Inspecting {filepath}")
        
        with uproot.open(filepath) as file:
            tree = file[tree_name]
            
            branches = {}
            for branch_name in tree.keys():
                branch = tree[branch_name]
                branches[branch_name] = {
                    "dtype": str(branch.type),
                    "entries": tree.num_entries,
                }
            
            return {
                "filename": filepath.name,
                "tree": tree_name,
                "num_entries": tree.num_entries,
                "num_branches": len(branches),
                "branches": branches
            }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def main():
    """Example: Fetch and parse data"""
    
    # 1. Create fetcher and download sample
    fetcher = DataFetcher()
    sample_files = fetcher.fetch_cms_2011_sample(n_files=2)
    
    # 2. Inspect files
    parser = DataParser()
    for filepath in sample_files:
        info = parser.inspect_root_file(filepath)
        print(json.dumps(info, indent=2))
    
    # 3. Parse and combine
    df = parser.batch_parse_files(sample_files, output_format="parquet")
    print(f"\nLoaded dataset shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()