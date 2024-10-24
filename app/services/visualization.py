# app/services/visualization.py
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
from typing import Dict
from sklearn.metrics import confusion_matrix

class ReportVisualizer:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Setting default matplotlib style instead of seaborn
        plt.style.use('default')
        # Set the color palette and styling through seaborn
        sns.set_theme(style="whitegrid")
        sns.set_palette("husl")
    
    def create_confusion_matrix(self, df: pd.DataFrame) -> Path:
        """Generate confusion matrix visualization"""
        plt.figure(figsize=(10, 8))
        cm = confusion_matrix(df['is_valid_actual'], df['is_valid_predicted'])
        
        # Using seaborn's heatmap with custom styling
        ax = sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                        xticklabels=['Invalid', 'Valid'],
                        yticklabels=['Invalid', 'Valid'])
        
        plt.title('Overall Confusion Matrix', pad=20)
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        
        # Improve layout
        plt.tight_layout()
        
        output_path = self.output_dir / 'confusion_matrix.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path

    def create_metrics_comparison(self, metrics: Dict) -> Path:
        """Generate metrics comparison visualization"""
        companies = list(metrics.keys())
        metrics_df = pd.DataFrame({
            'Company': companies,
            'Precision': [metrics[c]['precision'] for c in companies],
            'Recall': [metrics[c]['recall'] for c in companies],
            'F1 Score': [metrics[c]['f1_score'] for c in companies],
            'Accuracy': [metrics[c]['accuracy'] for c in companies]
        })
        
        plt.figure(figsize=(15, 8))
        metrics_df_melted = pd.melt(metrics_df, id_vars=['Company'], 
                                  var_name='Metric', value_name='Score')
        
        # Using seaborn's barplot with improved styling
        ax = sns.barplot(data=metrics_df_melted, x='Company', y='Score', hue='Metric')
        
        plt.title('Performance Metrics by Company', pad=20)
        plt.xticks(rotation=45, ha='right')
        
        # Adjust legend position
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Improve layout
        plt.tight_layout()
        
        output_path = self.output_dir / 'metrics_comparison.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        return output_path