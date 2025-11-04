import pandas as pd
import json
from datetime import datetime
from collections import Counter

# ===== CONFIGURATION =====
INPUT_FILE = "bangalore_with_topics.csv"
OUTPUT_FILE = "dashboard_data.json"

def load_and_prepare_data(filename):
    """Load and prepare the data"""
    print(f"Loading data from {filename}...")
    df = pd.read_csv(filename)
    
    # Convert created_utc to datetime
    df['created_utc'] = pd.to_datetime(df['created_utc'])
    df['year'] = df['created_utc'].dt.year
    df['month'] = df['created_utc'].dt.month
    df['year_month'] = df['created_utc'].dt.to_period('M').astype(str)
    
    print(f"✓ Loaded {len(df)} posts")
    print(f"  Date range: {df['created_utc'].min()} to {df['created_utc'].max()}")
    
    return df

def generate_topic_trends(df):
    """Generate topic trends over years"""
    print("\nGenerating topic trends...")
    
    # Get all unique topics and years
    all_topics = df['topic'].unique()
    all_years = sorted(df['year'].unique())
    
    trends = []
    
    for year in all_years:
        year_data = {'year': int(year)}
        year_df = df[df['year'] == year]
        
        # Count posts per topic for this year
        topic_counts = year_df['topic'].value_counts()
        
        for topic in all_topics:
            # Clean topic name for JSON
            topic_clean = topic.replace('_', ' ')
            year_data[topic] = int(topic_counts.get(topic, 0))
        
        trends.append(year_data)
    
    print(f"✓ Generated trends for {len(all_years)} years")
    return trends

def generate_topic_distribution(df):
    """Generate overall topic distribution"""
    print("\nGenerating topic distribution...")
    
    topic_counts = df['topic'].value_counts()
    
    # Define colors for each topic
    topic_colors = {
        'Traffic': '#ef4444',
        'Housing_Rent': '#f59e0b',
        'Food': '#10b981',
        'Infrastructure': '#3b82f6',
        'Jobs_Career': '#8b5cf6',
        'Safety_Law': '#ec4899',
        'Culture_Events': '#14b8a6',
        'Language': '#f97316',
        'Social_Life': '#06b6d4',
        'Health': '#84cc16',
        'Weather': '#a855f7',
        'Politics': '#f43f5e',
        'Pets_Animals': '#22c55e',
        'Education': '#eab308',
        'General_Discussion': '#6b7280'
    }
    
    distribution = []
    for topic, count in topic_counts.items():
        distribution.append({
            'name': topic.replace('_', ' & '),
            'value': int(count),
            'color': topic_colors.get(topic, '#6b7280')
        })
    
    print(f"✓ Generated distribution for {len(distribution)} topics")
    return distribution

def generate_top_posts(df, n=10):
    """Get top posts by score for each major topic"""
    print("\nGenerating top posts...")
    
    # Get top topics
    top_topics = df['topic'].value_counts().head(8).index.tolist()
    
    top_posts = []
    
    for topic in top_topics:
        topic_df = df[df['topic'] == topic].nlargest(3, 'score')
        
        for _, post in topic_df.iterrows():
            top_posts.append({
                'topic': topic,
                'title': post['title'][:100] + ('...' if len(post['title']) > 100 else ''),
                'year': int(post['year']),
                'score': int(post['score']),
                'num_comments': int(post['num_comments'])
            })
    
    # Sort by score and take top N
    top_posts = sorted(top_posts, key=lambda x: x['score'], reverse=True)[:n]
    
    print(f"✓ Generated {len(top_posts)} top posts")
    return top_posts

def generate_insights(df):
    """Generate key insights and statistics"""
    print("\nGenerating insights...")
    
    insights = {}
    
    # Basic stats
    insights['total_posts'] = int(len(df))
    insights['date_range'] = {
        'start': df['created_utc'].min().strftime('%Y-%m-%d'),
        'end': df['created_utc'].max().strftime('%Y-%m-%d')
    }
    insights['years_analyzed'] = int(df['year'].nunique())
    insights['topics_tracked'] = int(df['topic'].nunique())
    
    # Top topic overall
    top_topic = df['topic'].value_counts().index[0]
    top_topic_count = int(df['topic'].value_counts().values[0])
    insights['top_topic'] = {
        'name': top_topic.replace('_', ' & '),
        'count': top_topic_count,
        'percentage': round((top_topic_count / len(df)) * 100, 1)
    }
    
    # Growth analysis - compare first half vs second half
    midpoint_year = df['year'].median()
    first_half = df[df['year'] <= midpoint_year]
    second_half = df[df['year'] > midpoint_year]
    
    growth_topics = []
    
    for topic in df['topic'].unique():
        first_count = len(first_half[first_half['topic'] == topic])
        second_count = len(second_half[second_half['topic'] == topic])
        
        if first_count > 5:  # Only if we have enough data
            growth_rate = ((second_count - first_count) / first_count) * 100
            
            if abs(growth_rate) > 30:  # Significant change
                growth_topics.append({
                    'topic': topic.replace('_', ' & '),
                    'growth_rate': round(growth_rate, 1),
                    'trend': 'up' if growth_rate > 0 else 'down'
                })
    
    # Sort by absolute growth rate
    growth_topics = sorted(growth_topics, key=lambda x: abs(x['growth_rate']), reverse=True)[:5]
    insights['trending_topics'] = growth_topics
    
    # Year-by-year post counts
    posts_per_year = df['year'].value_counts().sort_index()
    insights['posts_per_year'] = {int(year): int(count) for year, count in posts_per_year.items()}
    
    # Average engagement
    insights['average_score'] = round(df['score'].mean(), 1)
    insights['average_comments'] = round(df['num_comments'].mean(), 1)
    
    # Most discussed topics (by comments)
    topic_comments = df.groupby('topic')['num_comments'].sum().sort_values(ascending=False).head(5)
    insights['most_discussed'] = [
        {
            'topic': topic.replace('_', ' & '),
            'total_comments': int(count)
        }
        for topic, count in topic_comments.items()
    ]
    
    print(f"✓ Generated comprehensive insights")
    return insights

def generate_monthly_trends(df):
    """Generate monthly trends for detailed view"""
    print("\nGenerating monthly trends...")
    
    monthly = df.groupby(['year_month', 'topic']).size().reset_index(name='count')
    
    # Convert to list of dicts
    monthly_data = []
    for month in sorted(df['year_month'].unique()):
        month_data = {'month': month}
        month_df = monthly[monthly['year_month'] == month]
        
        for _, row in month_df.iterrows():
            topic = row['topic']
            month_data[topic] = int(row['count'])
        
        monthly_data.append(month_data)
    
    print(f"✓ Generated monthly trends for {len(monthly_data)} months")
    return monthly_data

def generate_topic_keywords(df):
    """Extract top keywords for each topic"""
    print("\nExtracting topic keywords...")
    
    from collections import Counter
    import re
    
    stop_words = {'the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'on', 'with', 
                  'this', 'that', 'it', 'from', 'are', 'was', 'be', 'have', 
                  'has', 'been', 'my', 'i', 'you', 'me', 'we', 'they'}
    
    topic_keywords = {}
    
    for topic in df['topic'].unique():
        topic_df = df[df['topic'] == topic]
        
        # Combine all titles for this topic
        all_text = ' '.join(topic_df['title'].fillna('').astype(str))
        
        # Clean and tokenize
        words = re.findall(r'\b[a-z]+\b', all_text.lower())
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get top 5 keywords
        word_counts = Counter(words)
        top_words = [word for word, count in word_counts.most_common(5)]
        
        topic_keywords[topic] = top_words
    
    print(f"✓ Extracted keywords for {len(topic_keywords)} topics")
    return topic_keywords

def save_dashboard_data(data, filename):
    """Save all data to JSON"""
    print(f"\nSaving dashboard data to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Dashboard data saved!")

def main():
    """Main execution"""
    print("="*60)
    print("GENERATING DASHBOARD DATA FROM REAL CSV")
    print("="*60)
    
    # Load data
    df = load_and_prepare_data(INPUT_FILE)
    
    # Generate all dashboard data
    dashboard_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'source_file': INPUT_FILE
        },
        'insights': generate_insights(df),
        'topic_trends': generate_topic_trends(df),
        'topic_distribution': generate_topic_distribution(df),
        'top_posts': generate_top_posts(df, n=15),
        'monthly_trends': generate_monthly_trends(df),
        'topic_keywords': generate_topic_keywords(df)
    }
    
    # Save to JSON
    save_dashboard_data(dashboard_data, OUTPUT_FILE)
    
    print("\n" + "="*60)
    print("DATA GENERATION COMPLETE! 🎉")
    print("="*60)
    print(f"\nGenerated {OUTPUT_FILE} with:")
    print(f"  • {dashboard_data['insights']['total_posts']} posts analyzed")
    print(f"  • {dashboard_data['insights']['years_analyzed']} years of data")
    print(f"  • {dashboard_data['insights']['topics_tracked']} topics tracked")
    print(f"  • Top topic: {dashboard_data['insights']['top_topic']['name']}")
    print(f"\nNext step: Update the dashboard to load this JSON file!")

if __name__ == "__main__":
    main()
