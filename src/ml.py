"""Machine learning for particle classification"""

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import logging

logger = logging.getLogger(__name__)


class SignalBackgroundClassifier:
    """Train BDT to distinguish Higgs signal from background"""
    
    def __init__(self):
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = None
    
    def prepare_features(self, df):
        """Select features for training"""
        # Use numeric columns with 'pt', 'eta', 'phi', 'mass' in name
        feature_cols = [
            col for col in df.columns 
            if isinstance(df[col].dtype, (np.integer, np.floating))
            and col not in ['event', 'run', 'luminosity_block']
        ]
        
        if len(feature_cols) == 0:
            # Fallback: create mock features if data is limited
            feature_cols = [col for col in df.columns if col not in ['event', 'run']]
        
        return df[feature_cols].fillna(0).values, feature_cols
    
    def train(self, df_signal, df_background):
        """Train classifier"""
        logger.info("Preparing training data...")
        
        # Get features
        X_signal, self.feature_names = self.prepare_features(df_signal)
        X_background, _ = self.prepare_features(df_background)
        
        # Create labels
        y_signal = np.ones(len(X_signal))
        y_background = np.zeros(len(X_background))
        
        # Combine
        X = np.vstack([X_signal, X_background])
        y = np.hstack([y_signal, y_background])
        
        # Shuffle
        idx = np.random.permutation(len(X))
        X, y = X[idx], y[idx]
        
        # Normalize
        X = self.scaler.fit_transform(X)
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        logger.info(f"Training on {len(X_train)} events...")
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        logger.info(f"Training accuracy: {train_score:.4f}")
        logger.info(f"Testing accuracy: {test_score:.4f}")
        
        return train_score, test_score
    
    def predict(self, df):
        """Apply classifier to data"""
        X, _ = self.prepare_features(df)
        X = self.scaler.transform(X)
        
        # Get probabilities
        proba = self.model.predict_proba(X)[:, 1]  # Signal probability
        
        df_copy = df.copy()
        df_copy['signal_prob'] = proba
        df_copy['is_signal'] = proba > 0.5
        
        return df_copy
    
    def feature_importance(self):
        """Get feature importances"""
        importances = self.model.feature_importances_
        return pd.DataFrame({
            'feature': self.feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False)


def main():
    """Main training function"""
    logging.basicConfig(level=logging.INFO)
    logger.info("ML Classifier Training")
    logger.info("=" * 50)
    
    # Create synthetic training data
    np.random.seed(42)
    
    # Signal: Higgs-like events (high mass, high energy)
    df_signal = pd.DataFrame({
        'pt': np.random.normal(100, 20, 500),
        'eta': np.random.normal(0, 1, 500),
        'mass': np.random.normal(125, 5, 500),
        'energy': np.random.normal(200, 30, 500),
    })
    
    # Background: QCD-like events (low mass, variable)
    df_background = pd.DataFrame({
        'pt': np.random.normal(50, 15, 500),
        'eta': np.random.normal(0, 2, 500),
        'mass': np.random.normal(80, 30, 500),
        'energy': np.random.normal(100, 40, 500),
    })
    
    logger.info(f"Signal events: {len(df_signal)}")
    logger.info(f"Background events: {len(df_background)}")
    
    # Train
    clf = SignalBackgroundClassifier()
    train_score, test_score = clf.train(df_signal, df_background)
    
    # Show results
    logger.info("\n✓ Training Complete!")
    logger.info(f"Train accuracy: {train_score:.1%}")
    logger.info(f"Test accuracy:  {test_score:.1%}")
    
    # Feature importance
    logger.info("\nTop features:")
    print(clf.feature_importance().head())
    
    return clf


if __name__ == "__main__":
    main()