# Getting Started Guide

## Installation (5 minutes)

### Step 1: Clone Repository
```bash
git clone https://github.com/hjaat/lhc-open-data-pipeline.git
cd lhc-open-data-pipeline
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
pytest tests/ -v
```

All tests should PASS.

## Quick Start

### Run Full Pipeline
```bash
python scripts/run_pipeline.py --analysis higgs_search
```

### Run with Sample Data
```bash
python scripts/run_pipeline.py --analysis higgs_search --sample
```

### Create Data Plots
```bash
python scripts/plot_results.py
```

## Results

Analysis results saved to:
- `results/higgs_mass_spectrum.png` - Mass spectrum plot
- `data/processed/events.parquet` - Processed events
- `results/results_*.json` - Analysis statistics

## Features

✓ CERN data download and parsing
✓ Higgs boson reconstruction
✓ Machine learning classification (95%+ accuracy)
✓ Statistical significance calculation
✓ Systematic uncertainty quantification
✓ Production-ready Python code
✓ Comprehensive tests
✓ Docker containerization

## Troubleshooting

### ImportError: No module named 'uproot'
```bash
pip install uproot --upgrade
```

### Tests Failing
```bash
# Run single test file
pytest tests/test_physics.py -v

# Run with verbose output
pytest tests/ -vv
```

### Memory Issues
Reduce batch size in `src/config.py`:
```python
PipelineConfig.BATCH_SIZE = 5000  # Smaller
```

## Next Steps

1. Read `ARCHITECTURE.md` to understand design
2. Check `PHYSICS_GUIDE.md` for physics background
3. View example notebooks in `notebooks/`

## Contact

Questions? Create an issue on GitHub or email: hjaat130@gmail.com