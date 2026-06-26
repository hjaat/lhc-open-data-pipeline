# Architecture & Design

## System Overview

The LHC Open Data Pipeline processes particle physics data through 6 stages: RAW DATA (ROOT files)
↓
[FETCH]
↓
CACHED FILES
↓
[PARSE]
↓
DATAFRAME (Pandas)
↓
[VALIDATE]
↓
CLEANED DATA
↓
[RECONSTRUCT]
↓
PHYSICS OBJECTS
↓
[SELECT]
↓
SELECTED EVENTS
↓
[ANALYZE]
↓
RESULTS

## Module Breakdown

### src/config.py
- Physics constants (Higgs mass, Z mass, etc.)
- Analysis cuts (pT thresholds, isolation)
- Pipeline settings

### src/data/fetcher.py
- Download from CERN Open Data Portal
- Manage cached files
- Verify file integrity

### src/physics.py
- 4-vector mathematics
- Invariant mass calculation
- Event selection

### src/pipeline.py
- Main orchestration
- Stage management
- Error handling

### src/analysis.py
- Higgs reconstruction
- Event-level analysis
- Mass spectrum fitting

### src/ml.py
- BDT classifier training
- Signal/background discrimination
- Feature importance

### src/statistics.py
- Significance calculation
- Statistical tests
- Mass spectrum fitting

### src/uncertainties.py
- Systematic error propagation
- Uncertainty quantification

## Design Patterns

### Stage Pattern
Pipeline divided into discrete, reusable stages. Each stage:
- Has clear input/output format
- Tracks status (pending, running, complete, failed)
- Reports metrics (events processed, runtime)
- Can be skipped or retried

### Configuration Objects
All parameters in `src/config.py` for:
- Easy modification
- Reproducibility
- Clear documentation

### Dataframe-Centric
Most operations on Pandas DataFrames:
- Vectorized operations (fast)
- Easy integration with ML libraries
- Natural Python interface

## Performance

### Local Execution
- Small dataset: ~30 seconds
- Medium dataset: ~5 minutes
- Large dataset: May run out of memory

### Optimization Strategies
1. Parquet caching (50x faster than ROOT)
2. Vectorized NumPy operations
3. Selective column loading
4. Batch processing

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Data I/O | uproot, Parquet | Pure Python, no C++ dependency |
| Physics | NumPy, SciPy | Numerical computing standard |
| ML | scikit-learn, XGBoost | Lightweight, interpretable |
| Distributed | Spark (optional) | Scales to multi-TB |
| Visualization | Matplotlib, Plotly | Publication-quality plots |
| Testing | pytest | Industry standard |
| Docs | Sphinx (optional) | Professional documentation |

## Scalability

### Current Limits
- Single machine: ~100k events
- Virtual machine: ~1M events
- Spark cluster: ~100M events

### Future Improvements
- Implement Spark distributed processing
- Add GPU support for ML
- Cloud deployment (BigQuery, Cloud Run)
- Real-time streaming pipeline