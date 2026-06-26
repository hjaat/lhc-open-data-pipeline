"""
config.py - Centralized configuration for LHC Open Data Pipeline
Handles data paths, physics parameters, and experiment settings
"""

import os
from dataclasses import dataclass
from typing import Dict, List
from pathlib import Path
import json

# ============================================================================
# PROJECT PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Create directories if they don't exist
for directory in [DATA_DIR, CACHE_DIR, RAW_DIR, PROCESSED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ============================================================================
# PHYSICS PARAMETERS (PDG Constants)
# ============================================================================

@dataclass
class PhysicsConstants:
    """Particle Data Group (PDG) constants"""
    
    # Masses (GeV/c²)
    HIGGS_MASS = 125.09  # Higgs boson mass
    Z_MASS = 91.1876
    W_MASS = 80.379
    TOP_MASS = 173.21
    B_MASS = 4.18
    MUON_MASS = 0.1056
    ELECTRON_MASS = 0.0005109
    
    # Widths (GeV)
    HIGGS_WIDTH = 0.00407
    Z_WIDTH = 2.4952
    W_WIDTH = 2.085
    
    # Coupling constants
    ALPHA_EM = 1.0 / 137.035999  # Fine structure constant
    ALPHA_S = 0.1181  # Strong coupling constant
    
    # CKM matrix elements (unitarity triangle)
    VUD = 0.97437
    VUS = 0.2242
    VUB = 0.00382
    
    @classmethod
    def to_dict(cls) -> Dict[str, float]:
        """Convert to dictionary for serialization"""
        return {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}


# ============================================================================
# DATA SOURCE CONFIGURATION
# ============================================================================

@dataclass
class DataSourceConfig:
    """Configuration for data fetching from CERN Open Data Portal"""
    
    # CMS Dataset (2011-2012, Run A+B)
    DATASET_NAME = "CMSRun2011A"
    DATASET_DOI = "10.7483/CERN.PHYS.4V3Q"
    DATASET_URL = "http://opendata.cern.ch/"
    
    # File patterns
    FILE_PATTERN = "*.root"
    MAX_FILES_SAMPLE = 10  # For initial testing
    MAX_FILES_FULL = None  # All files
    
    # Data specifications
    TREE_NAME = "Events"  # ROOT tree name in files
    
    # Event selection
    FILTERS = {
        "run_number": (160404, 180252),  # Valid run range
        "luminosity_block": (1, 9999),
        "event_triggers": ["HLT_Ele27_WP80", "HLT_Mu30"],  # Trigger paths
    }


# ============================================================================
# PHYSICS ANALYSIS CONFIGURATION
# ============================================================================

@dataclass
class AnalysisConfig:
    """Configuration for physics analysis cuts and parameters"""
    
    # Event-level cuts
    EVENT_CUTS = {
        "min_vertices": 1,
        "vertex_ndof_min": 4,
        "vertex_z_range": (-24, 24),  # cm
        "vertex_rho_range": (0, 2),  # cm
    }
    
    # Muon selection (tight criteria)
    MUON_CUTS = {
        "pt_min": 20.0,  # GeV
        "eta_range": (-2.4, 2.4),
        "isolation_rel_threshold": 0.2,  # Relative isolation < 0.2
        "dz_vertex_max": 0.1,  # cm
        "d0_vertex_max": 0.02,  # cm
        "chi2_ndof_max": 10.0,
    }
    
    # Electron selection (tight criteria)
    ELECTRON_CUTS = {
        "pt_min": 20.0,  # GeV
        "eta_range_barrel": (-1.442, 1.442),
        "eta_range_endcap": (1.560, 2.5),
        "isolation_rel_threshold": 0.15,
        "dz_vertex_max": 0.1,  # cm
        "d0_vertex_max": 0.02,  # cm
    }
    
    # Jet selection (for hadronic channels)
    JET_CUTS = {
        "pt_min": 30.0,  # GeV
        "eta_max": 4.7,
        "neutral_hadron_fraction_max": 0.99,
        "neutral_em_fraction_max": 0.99,
    }
    
    # Higgs analysis specific
    HIGGS_WINDOW = (120, 130)  # GeV (invariant mass window)
    HIGGS_FOUR_LEPTON = {
        "m_ll_range": (60, 120),  # Z candidate mass window
        "m_zz_min": 100,  # Minimum 4-lepton invariant mass
    }
    
    # Di-jet analysis
    DIJET_MASS_RANGE = (40, 200)  # GeV


# ============================================================================
# PROCESSING PIPELINE CONFIGURATION
# ============================================================================

@dataclass
class PipelineConfig:
    """Configuration for data processing pipeline"""
    
    # Execution settings
    BATCH_SIZE = 10000  # Events per batch
    NUM_WORKERS = 4  # Parallel workers
    SHUFFLE_DATA = True
    RANDOM_SEED = 42
    
    # Processing stages
    STAGES = [
        "fetch",
        "parse",
        "validate",
        "reconstruct",
        "select",
        "analyze",
        "visualize"
    ]
    
    # Caching
    ENABLE_CACHE = True
    CACHE_FORMAT = "parquet"  # parquet or hdf5
    CACHE_COMPRESSION = "snappy"
    
    # Output formats
    OUTPUT_FORMATS = ["parquet", "csv", "json"]
    
    # Distributed processing (optional)
    USE_SPARK = False
    SPARK_MASTER = "local[*]"


# ============================================================================
# CLOUD DEPLOYMENT CONFIGURATION
# ============================================================================

@dataclass
class CloudConfig:
    """Configuration for cloud deployment"""
    
    # Google Cloud Project
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")
    GCP_REGION = "us-central1"
    
    # BigQuery dataset for results
    BIGQUERY_DATASET = "lhc_open_data"
    BIGQUERY_RESULTS_TABLE = "analysis_results"
    
    # Cloud Storage buckets
    GCS_BUCKET_DATA = f"{GCP_PROJECT_ID}-lhc-data"
    GCS_BUCKET_RESULTS = f"{GCP_PROJECT_ID}-lhc-results"
    
    # Container registry
    CONTAINER_REGISTRY = "gcr.io"
    IMAGE_NAME = "lhc-open-data-pipeline"
    
    # Kubernetes
    K8S_NAMESPACE = "default"
    K8S_REPLICAS = 3


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "[%(asctime)s] [%(name)s] [%(levelname)s] [%(funcName)s:%(lineno)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(PROJECT_ROOT / "logs" / "pipeline.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_config_dict() -> Dict:
    """Export all configuration as dictionary (for serialization)"""
    return {
        "physics": PhysicsConstants.to_dict(),
        "data_source": DataSourceConfig.__dict__,
        "analysis": AnalysisConfig.__dict__,
        "pipeline": PipelineConfig.__dict__,
        "cloud": CloudConfig.__dict__,
        "logging": LOGGING_CONFIG
    }


def save_config(filepath: Path):
    """Save configuration to JSON file"""
    config_dict = get_config_dict()
    with open(filepath, 'w') as f:
        json.dump(config_dict, f, indent=2, default=str)


# ============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# ============================================================================

# Development environment
if os.getenv("ENV", "development") == "development":
    DataSourceConfig.MAX_FILES_SAMPLE = 5
    PipelineConfig.BATCH_SIZE = 5000

# Production environment
elif os.getenv("ENV") == "production":
    PipelineConfig.USE_SPARK = True
    CloudConfig.K8S_REPLICAS = 10

# Testing environment
elif os.getenv("ENV") == "testing":
    DataSourceConfig.MAX_FILES_SAMPLE = 1
    PipelineConfig.ENABLE_CACHE = False


# ============================================================================
# LOGGER INITIALIZATION
# ============================================================================

import logging.config

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

logger.info(f"Configuration loaded from {__file__}")
logger.debug(f"Project root: {PROJECT_ROOT}")
logger.debug(f"Data directory: {DATA_DIR}")