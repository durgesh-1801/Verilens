import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class AnomalyDetector:
    """Multi-method anomaly detection system"""
    
    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.scaler = StandardScaler()
        self.models = {}
        
    def preprocess_data(self, df, columns=None):
        """Preprocess data for anomaly detection"""
        if columns is None:
            # Select only numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
        else:
            numeric_df = df[columns]
        
        # Handle missing values
        numeric_df = numeric_df.fillna(numeric_df.median())
        
        # Scale data
        scaled_data = self.scaler.fit_transform(numeric_df)
        
        return scaled_data, numeric_df.columns.tolist()
    
    def isolation_forest(self, data, contamination=None):
        """Isolation Forest for anomaly detection"""
        if contamination is None:
            contamination = self.contamination
            
        model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        predictions = model.fit_predict(data)
        scores = model.decision_function(data)
        
        self.models['isolation_forest'] = model
        
        return predictions, scores
    
    def local_outlier_factor(self, data, n_neighbors=20):
        """Local Outlier Factor for anomaly detection"""
        model = LocalOutlierFactor(
            n_neighbors=n_neighbors,
            contamination=self.contamination
        )
        predictions = model.fit_predict(data)
        scores = model.negative_outlier_factor_
        
        return predictions, scores
    
    def one_class_svm(self, data):
        """One-Class SVM for anomaly detection"""
        model = OneClassSVM(
            nu=self.contamination,
            kernel='rbf',
            gamma='auto'
        )
        predictions = model.fit_predict(data)
        scores = model.decision_function(data)
        
        self.models['one_class_svm'] = model
        
        return predictions, scores
    
    def statistical_zscore(self, df, threshold=3):
        """Z-Score based anomaly detection"""
        numeric_df = df.select_dtypes(include=[np.number])
        z_scores = np.abs(stats.zscore(numeric_df.fillna(numeric_df.median())))
        anomalies = (z_scores > threshold).any(axis=1)
        
        return anomalies.astype(int) * -2 + 1, z_scores.max(axis=1)
    
    def iqr_method(self, df, multiplier=1.5):
        """IQR based anomaly detection"""
        numeric_df = df.select_dtypes(include=[np.number])
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        anomalies = ((numeric_df < lower_bound) | (numeric_df > upper_bound)).any(axis=1)
        
        return anomalies.astype(int) * -2 + 1
    
    def dbscan_clustering(self, data, eps=0.5, min_samples=5):
        """DBSCAN clustering for anomaly detection"""
        model = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = model.fit_predict(data)
        
        # Points labeled as -1 are anomalies
        predictions = np.where(clusters == -1, -1, 1)
        
        return predictions, clusters
    
    def ensemble_detection(self, df, columns=None, methods=['isolation_forest', 'lof', 'zscore']):
        """Ensemble method combining multiple detection algorithms"""
        scaled_data, used_columns = self.preprocess_data(df, columns)
        
        results = {}
        all_predictions = []
        
        if 'isolation_forest' in methods:
            pred, scores = self.isolation_forest(scaled_data)
            results['isolation_forest'] = {'predictions': pred, 'scores': scores}
            all_predictions.append(pred)
            
        if 'lof' in methods:
            pred, scores = self.local_outlier_factor(scaled_data)
            results['lof'] = {'predictions': pred, 'scores': scores}
            all_predictions.append(pred)
            
        if 'svm' in methods:
            pred, scores = self.one_class_svm(scaled_data)
            results['svm'] = {'predictions': pred, 'scores': scores}
            all_predictions.append(pred)
            
        if 'zscore' in methods:
            pred, scores = self.statistical_zscore(df)
            results['zscore'] = {'predictions': pred, 'scores': scores}
            all_predictions.append(pred)
        
        # Ensemble voting
        if all_predictions:
            predictions_array = np.array(all_predictions)
            # Majority voting: if more than half say anomaly (-1), it's an anomaly
            ensemble_pred = np.where(
                np.sum(predictions_array == -1, axis=0) >= len(all_predictions) / 2,
                -1, 1
            )
            
            # Confidence score based on agreement
            agreement = np.sum(predictions_array == ensemble_pred, axis=0) / len(all_predictions)
            
            results['ensemble'] = {
                'predictions': ensemble_pred,
                'confidence': agreement,
                'anomaly_indices': np.where(ensemble_pred == -1)[0]
            }
        
        return results
    
    def get_anomaly_details(self, df, anomaly_indices, top_features=5):
        """Get detailed information about detected anomalies"""
        anomaly_details = []
        numeric_df = df.select_dtypes(include=[np.number])
        
        # Calculate feature importance for anomalies
        for idx in anomaly_indices:
            row = numeric_df.iloc[idx]
            median = numeric_df.median()
            std = numeric_df.std()
            
            # Calculate deviation from median
            deviation = np.abs((row - median) / (std + 1e-10))
            top_deviating = deviation.nlargest(top_features)
            
            detail = {
                'index': idx,
                'top_features': top_deviating.to_dict(),
                'original_data': df.iloc[idx].to_dict()
            }
            anomaly_details.append(detail)
        
        return anomaly_details


class RuleBasedDetector:
    """Rule-based fraud detection for specific use cases"""
    
    def __init__(self):
        self.rules = []
        
    def add_rule(self, name, condition_func, severity='medium'):
        """Add a detection rule"""
        self.rules.append({
            'name': name,
            'condition': condition_func,
            'severity': severity
        })
    
    def detect(self, df):
        """Apply all rules to detect fraud"""
        results = []
        
        for rule in self.rules:
            mask = df.apply(rule['condition'], axis=1)
            flagged_indices = df[mask].index.tolist()
            
            if flagged_indices:
                results.append({
                    'rule_name': rule['name'],
                    'severity': rule['severity'],
                    'flagged_count': len(flagged_indices),
                    'flagged_indices': flagged_indices
                })
        
        return results
    
    def add_common_fraud_rules(self, amount_col='amount', date_col=None):
        """Add common fraud detection rules"""
        
        # High amount transactions
        self.add_rule(
            'High Amount Transaction',
            lambda x: x[amount_col] > x[amount_col].mean() + 3 * x[amount_col].std() 
                      if amount_col in x.index else False,
            severity='high'
        )
        
        # Round number amounts (potential manipulation)
        self.add_rule(
            'Suspicious Round Amount',
            lambda x: x[amount_col] % 1000 == 0 and x[amount_col] > 10000 
                      if amount_col in x.index else False,
            severity='medium'
        )
        
        # Zero or negative amounts
        self.add_rule(
            'Invalid Amount',
            lambda x: x[amount_col] <= 0 if amount_col in x.index else False,
            severity='high'
        )
