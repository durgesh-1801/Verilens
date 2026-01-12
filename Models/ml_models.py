"""
Machine Learning Models for Anomaly Detection
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler
from scipy import stats
from typing import Tuple, List, Dict

class AnomalyDetector:
    """Simple anomaly detector"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
    
    def detect(
        self, 
        df: pd.DataFrame, 
        features: List[str], 
        algorithm: str = 'ensemble'
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Run anomaly detection"""
        
        # Prepare data
        X = df[features].fillna(df[features].median())
        X_scaled = self.scaler.fit_transform(X)
        
        if algorithm == 'ensemble':
            return self._ensemble(X_scaled)
        elif algorithm == 'isolation_forest':
            return self._isolation_forest(X_scaled)
        elif algorithm == 'lof':
            return self._lof(X_scaled)
        elif algorithm == 'zscore':
            return self._zscore(X_scaled)
        else:
            return self._isolation_forest(X_scaled)
    
    def _isolation_forest(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        model = IsolationForest(contamination=self.contamination, random_state=42)
        pred = model.fit_predict(X)
        scores = -model.decision_function(X)
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        return pred, scores
    
    def _lof(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        model = LocalOutlierFactor(contamination=self.contamination)
        pred = model.fit_predict(X)
        scores = -model.negative_outlier_factor_
        scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
        return pred, scores
    
    def _zscore(self, X: np.ndarray, threshold: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        z = np.abs(stats.zscore(X, nan_policy='omit'))
        z = np.nan_to_num(z, nan=0)
        max_z = np.max(z, axis=1)
        pred = np.where(max_z > threshold, -1, 1)
        scores = max_z / (max_z.max() + 1e-10)
        return pred, scores
    
    def _ensemble(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        pred1, score1 = self._isolation_forest(X)
        pred2, score2 = self._lof(X)
        pred3, score3 = self._zscore(X)
        
        # Majority voting
        votes = np.array([pred1, pred2, pred3])
        anomaly_votes = np.sum(votes == -1, axis=0)
        final_pred = np.where(anomaly_votes >= 2, -1, 1)
        final_score = np.mean([score1, score2, score3], axis=0)
        
        return final_pred, final_score
