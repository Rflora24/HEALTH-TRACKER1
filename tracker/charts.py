import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64
from django.db.models import Avg
from .models import HealthRecord

def generate_sleep_chart(records):
    if not records.exists():
        return None
        
    # Convert records to DataFrame
    df = pd.DataFrame(list(records.values('date', 'sleep_hours')))
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['sleep_hours'], marker='o', linestyle='-', color='#2ecc71')
    plt.axhline(y=8, color='r', linestyle='--', alpha=0.3, label='Recommended (8 hours)')
    
    # Customize the plot
    plt.title('Sleep Hours Over Time', pad=20)
    plt.xlabel('Date')
    plt.ylabel('Hours of Sleep')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    # Encode the image
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph

def generate_water_chart(records):
    if not records.exists():
        return None
        
    # Convert records to DataFrame
    df = pd.DataFrame(list(records.values('date', 'water_intake')))
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['water_intake'], marker='o', linestyle='-', color='#3498db')
    plt.axhline(y=2.5, color='r', linestyle='--', alpha=0.3, label='Recommended (2.5L)')
    
    # Customize the plot
    plt.title('Water Intake Over Time', pad=20)
    plt.xlabel('Date')
    plt.ylabel('Water Intake (Liters)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    # Encode the image
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph

def generate_mood_chart(records):
    if not records.exists():
        return None
        
    # Convert records to DataFrame
    df = pd.DataFrame(list(records.values('date', 'mood')))
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Plot each mood type with different colors
    mood_colors = {
        'happy': '#2ecc71',
        'neutral': '#f1c40f',
        'sad': '#e74c3c',
        'stressed': '#9b59b6'
    }
    
    for mood, color in mood_colors.items():
        mood_data = df[df['mood'] == mood]
        if not mood_data.empty:
            plt.scatter(mood_data['date'], [mood] * len(mood_data), 
                       color=color, label=mood.capitalize(), s=100)

    # Customize the plot
    plt.title('Mood Over Time', pad=20)
    plt.xlabel('Date')
    plt.ylabel('Mood')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    # Encode the image
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph

def get_health_stats(records):
    """Calculate health statistics from records"""
    if not records.exists():
        return {
            'avg_sleep': 0,
            'avg_water': 0,
            'total_records': 0,
            'mood_distribution': {
                'happy': 0,
                'neutral': 0,
                'sad': 0,
                'stressed': 0,
            }
        }
        
    stats = {
        'avg_sleep': records.aggregate(Avg('sleep_hours'))['sleep_hours__avg'] or 0,
        'avg_water': records.aggregate(Avg('water_intake'))['water_intake__avg'] or 0,
        'total_records': records.count(),
        'mood_distribution': {
            'happy': records.filter(mood='happy').count(),
            'neutral': records.filter(mood='neutral').count(),
            'sad': records.filter(mood='sad').count(),
            'stressed': records.filter(mood='stressed').count(),
        }
    }
    return stats 