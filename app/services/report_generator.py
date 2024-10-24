from pathlib import Path
import pandas as pd
from typing import Dict, Tuple
import json
from app.utilities.metrics import calculate_company_metrics
from app.services.visualization import ReportVisualizer

class ReportGenerator:
    def __init__(self):
        self.data_file = Path("doc_validation_result.csv")
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.visualizer = ReportVisualizer(self.reports_dir)
    
    def generate_report(self) -> Tuple[Dict, str]:
        """Generate comprehensive validation report"""
        try:
            # Read data
            df = pd.read_csv(self.data_file)
            
            # Calculate metrics for each company
            metrics = {}
            for company in df['company_name'].unique():
                metrics[company] = calculate_company_metrics(df, company)
            
            # Generate visualizations
            self.visualizer.create_confusion_matrix(df)
            self.visualizer.create_metrics_comparison(metrics)
            
            # Create report directory with timestamp
            report_dir = self.reports_dir / pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # Save metrics to JSON
            metrics_file = report_dir / 'metrics.json'
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=4)
            
            return metrics, str(report_dir)
            
        except Exception as e:
            raise RuntimeError(f"Error generating report: {str(e)}")