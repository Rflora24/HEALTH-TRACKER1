from django.db.models import QuerySet
from typing import Dict, List, Optional
import numpy as np
from scipy.stats import pearsonr

def calculate_mood_correlation(records: QuerySet, metric: str) -> Optional[float]:
    """
    Calculate the correlation between mood and a given metric.
    
    Args:
        records: QuerySet of HealthRecord objects
        metric: The metric to correlate with mood (e.g., 'sleep_hours', 'water_intake')
        
    Returns:
        float: The correlation coefficient between -1 and 1, or None if calculation fails
    """
    try:
        mood_values = []
        metric_values = []
        
        # Convert mood to numerical values
        mood_map = {
            'EXCELLENT': 5,
            'GOOD': 4,
            'NEUTRAL': 3,
            'BAD': 2,
            'TERRIBLE': 1
        }
        
        for record in records:
            if hasattr(record, metric) and getattr(record, metric) is not None:
                mood_value = mood_map.get(record.mood, 3)  # Default to neutral if mood not found
                mood_values.append(mood_value)
                metric_values.append(getattr(record, metric))
        
        if len(mood_values) < 2 or len(metric_values) < 2:
            return None
            
        # Calculate Pearson correlation
        correlation, _ = pearsonr(mood_values, metric_values)
        return correlation
        
    except Exception as e:
        from django.core.exceptions import ValidationError
        raise ValidationError(f"Error calculating mood correlation: {str(e)}")

def calculate_weekly_stats(records: QuerySet) -> Dict[str, float]:
    """
    Calculate weekly averages for various health metrics.
    
    Args:
        records: QuerySet of HealthRecord objects
        
    Returns:
        dict: Dictionary containing weekly averages for each metric
    """
    weekly_stats = {}
    
    # Group records by week
    from django.db.models.functions import TruncWeek
    from django.db.models import Avg
    
    weekly_records = records.annotate(
        week=TruncWeek('date')
    ).values('week')
    
    # Calculate averages for each metric
    metrics = ['sleep_hours', 'water_intake', 'weight']
    
    for metric in metrics:
        weekly_avg = weekly_records.annotate(
            avg_metric=Avg(metric)
        ).values('week', 'avg_metric')
        
        weekly_stats[metric] = {
            week['week'].strftime('%Y-%m-%d'): week['avg_metric']
            for week in weekly_avg
        }
    
    return weekly_stats
