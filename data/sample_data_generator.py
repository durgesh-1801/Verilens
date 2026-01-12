import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(n_samples=1000, anomaly_rate=0.1):
    """Generate sample transaction data with embedded anomalies"""
    
    np.random.seed(42)
    
    # Generate base data
    n_normal = int(n_samples * (1 - anomaly_rate))
    n_anomaly = n_samples - n_normal
    
    # Normal transactions
    normal_data = {
        'transaction_id': [f'TXN{i:06d}' for i in range(n_normal)],
        'date': [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(n_normal)],
        'amount': np.random.lognormal(mean=6, sigma=1, size=n_normal),
        'category': np.random.choice(['Supplies', 'Services', 'Equipment', 'Travel', 'Utilities'], n_normal),
        'department': np.random.choice(['Finance', 'HR', 'IT', 'Operations', 'Marketing'], n_normal),
        'vendor_id': [f'V{random.randint(1, 100):03d}' for _ in range(n_normal)],
        'payment_method': np.random.choice(['Check', 'Wire', 'ACH', 'Credit Card'], n_normal, p=[0.3, 0.2, 0.4, 0.1]),
        'approval_level': np.random.choice([1, 2, 3], n_normal, p=[0.6, 0.3, 0.1]),
        'processing_time': np.random.normal(2, 0.5, n_normal),
        'is_weekend': np.random.choice([0, 1], n_normal, p=[0.8, 0.2]),
    }
    
    # Anomalous transactions
    anomaly_data = {
        'transaction_id': [f'TXN{i:06d}' for i in range(n_normal, n_samples)],
        'date': [datetime.now() - timedelta(days=random.randint(0, 365)) for _ in range(n_anomaly)],
        'amount': np.concatenate([
            np.random.lognormal(mean=10, sigma=1.5, size=n_anomaly // 2),  # Very high amounts
            np.random.uniform(0.01, 10, size=n_anomaly - n_anomaly // 2)   # Suspiciously low amounts
        ]),
        'category': np.random.choice(['Consulting', 'Misc', 'Supplies'], n_anomaly),
        'department': np.random.choice(['Finance', 'HR', 'IT', 'Operations', 'Marketing'], n_anomaly),
        'vendor_id': [f'V{random.randint(900, 999):03d}' for _ in range(n_anomaly)],  # New/unknown vendors
        'payment_method': np.random.choice(['Wire', 'Check'], n_anomaly, p=[0.7, 0.3]),
        'approval_level': np.random.choice([1, 3], n_anomaly, p=[0.4, 0.6]),  # Unusual approval patterns
        'processing_time': np.random.choice(
            [np.random.uniform(0, 0.5), np.random.uniform(10, 20)], 
            n_anomaly
        ),  # Too fast or too slow
        'is_weekend': np.random.choice([0, 1], n_anomaly, p=[0.3, 0.7]),  # More weekend transactions
    }
    
    # Combine data
    normal_df = pd.DataFrame(normal_data)
    anomaly_df = pd.DataFrame(anomaly_data)
    
    df = pd.concat([normal_df, anomaly_df], ignore_index=True)
    
    # Shuffle the data
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Add some computed features
    df['amount_log'] = np.log1p(df['amount'])
    df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
    df['month'] = pd.to_datetime(df['date']).dt.month
    df['is_high_value'] = (df['amount'] > df['amount'].quantile(0.95)).astype(int)
    
    return df

def generate_government_procurement_data(n_samples=2000):
    """Generate sample government procurement/tender data"""
    
    np.random.seed(42)
    
    data = {
        'tender_id': [f'TEND{i:06d}' for i in range(n_samples)],
        'date_published': [datetime.now() - timedelta(days=random.randint(0, 730)) for _ in range(n_samples)],
        'estimated_value': np.random.lognormal(mean=12, sigma=2, size=n_samples),
        'final_value': None,
        'department': np.random.choice([
            'Public Works', 'Health', 'Education', 'Defense', 
            'Transport', 'Environment', 'Social Services'
        ], n_samples),
        'category': np.random.choice([
            'Construction', 'IT Services', 'Medical Supplies', 
            'Consulting', 'Equipment', 'Maintenance'
        ], n_samples),
        'num_bidders': np.random.poisson(5, n_samples) + 1,
        'winner_id': [f'COMP{random.randint(1, 500):04d}' for _ in range(n_samples)],
        'bid_difference_pct': np.random.normal(5, 10, n_samples),
        'contract_duration_days': np.random.choice([30, 60, 90, 180, 365, 730], n_samples),
        'amendments_count': np.random.poisson(1, n_samples),
        'time_to_award_days': np.random.lognormal(mean=3, sigma=0.5, size=n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Calculate final value based on estimated value and bid difference
    df['final_value'] = df['estimated_value'] * (1 - df['bid_difference_pct'] / 100)
    
    # Inject anomalies
    anomaly_indices = np.random.choice(range(n_samples), size=int(n_samples * 0.1), replace=False)
    
    for idx in anomaly_indices:
        anomaly_type = random.choice(['single_bidder', 'high_amendment', 'price_manipulation', 'fast_award'])
        
        if anomaly_type == 'single_bidder':
            df.loc[idx, 'num_bidders'] = 1
        elif anomaly_type == 'high_amendment':
            df.loc[idx, 'amendments_count'] = random.randint(5, 15)
            df.loc[idx, 'final_value'] = df.loc[idx, 'estimated_value'] * random.uniform(1.3, 2.0)
        elif anomaly_type == 'price_manipulation':
            df.loc[idx, 'bid_difference_pct'] = random.choice([-0.5, 0.5, 49.9])
        elif anomaly_type == 'fast_award':
            df.loc[idx, 'time_to_award_days'] = random.uniform(1, 3)
    
    return df

if __name__ == "__main__":
    # Generate and save sample data
    df = generate_sample_data()
    df.to_csv('data/data.csv', index=False)
    print(f"Generated {len(df)} sample records")
    
    procurement_df = generate_government_procurement_data()
    procurement_df.to_csv('data/procurement_data.csv', index=False)
    print(f"Generated {len(procurement_df)} procurement records")
