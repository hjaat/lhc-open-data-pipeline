"""Test ML module"""

import pytest
import pandas as pd
import numpy as np
from src.ml import SignalBackgroundClassifier


def test_classifier_training():
    """Test BDT classifier"""
    
    # Create synthetic data
    df_signal = pd.DataFrame({
        'pt': np.random.normal(100, 20, 100),
        'eta': np.random.normal(0, 1, 100),
        'mass': np.random.normal(125, 5, 100),
    })
    
    df_background = pd.DataFrame({
        'pt': np.random.normal(50, 15, 100),
        'eta': np.random.normal(0, 2, 100),
        'mass': np.random.normal(80, 30, 100),
    })
    
    # Train
    clf = SignalBackgroundClassifier()
    train_score, test_score = clf.train(df_signal, df_background)
    
    # Verify
    assert 0 < train_score <= 1.0
    assert 0 < test_score <= 1.0
    assert train_score > 0.5


def test_prediction():
    """Test prediction on new data"""
    
    # Create and train
    df_signal = pd.DataFrame({
        'pt': np.random.normal(100, 20, 50),
        'eta': np.random.normal(0, 1, 50),
        'mass': np.random.normal(125, 5, 50),
    })
    
    df_background = pd.DataFrame({
        'pt': np.random.normal(50, 15, 50),
        'eta': np.random.normal(0, 2, 50),
        'mass': np.random.normal(80, 30, 50),
    })
    
    clf = SignalBackgroundClassifier()
    clf.train(df_signal, df_background)
    
    # Test data
    test_data = pd.DataFrame({
        'pt': [100, 50, 100],
        'eta': [0, 0, 0],
        'mass': [125, 80, 125],
    })
    
    # Predict
    results = clf.predict(test_data)
    
    # Verify
    assert 'signal_prob' in results.columns
    assert 'is_signal' in results.columns
    assert len(results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])