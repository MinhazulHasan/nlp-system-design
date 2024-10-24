import pandas as pd
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score
from typing import Dict, Tuple

def calculate_company_metrics(df: pd.DataFrame, company: str) -> Dict:
    """Calculate metrics for a specific company"""
    company_data = df[df['company_name'] == company]
    y_true = company_data['is_valid_actual']
    y_pred = company_data['is_valid_predicted']
    
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary')
    accuracy = accuracy_score(y_true, y_pred)
    
    return {
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'accuracy': float(accuracy),
        'total_documents': len(company_data),
        'valid_documents': int(company_data['is_valid_actual'].sum()),
        'invalid_documents': int(len(company_data) - company_data['is_valid_actual'].sum())
    }