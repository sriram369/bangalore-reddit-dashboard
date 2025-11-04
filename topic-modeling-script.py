import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import re
from collections import Counter
import json

# ===== CONFIGURATION =====
INPUT_FILE = "bangalore_historical_large.csv"
OUTPUT_FILE = "bangalore_with_topics.csv"
TOPICS_FILE = "topic_keywords.json"

# Define topic categories manually (more accurate than pure ML)
TOPIC_KEYWORDS = {
    'Traffic': ['traffic', 'jam', 'road', 'vehicle', 'auto', 'metro', 'bus', 'bmtc', 'congestion', 'commute', 'driving', 'parking', 'signal', 'flyover', 'pothole'],
    
    'Housing_Rent': ['rent', 'flat', 'apartment', 'pg', 'accommodation', 'landlord', 'housing', 'room', 'society', 'broker', 'deposit', 'lease'],
    
    'Food': ['food', 'restaurant', 'cafe', 'dosa', 'idli', 'biryani', 'pub', 'brewery', 'eat', 'dining', 'menu', 'dish', 'breakfast', 'lunch', 'dinner'],
    
    'Infrastructure': ['water', 'electricity', 'power', 'bescom', 'bwssb', 'bbmp', 'civic', 'garbage', 'drainage', 'sewage', 'lake', 'park', 'construction'],
    
    'Jobs_Career': ['job', 'career', 'salary', 'company', 'interview', 'hiring', 'work', 'office', 'wfh', 'startup', 'layoff', 'switch', 'package'],
    
    'Safety_Law': ['police', 'crime', 'theft', 'scam', 'harassment', 'safety', 'security', 'assault', 'fraud', 'fir', 'complaint', 'incident'],
    
    'Culture_Events': ['festival', 'event', 'concert', 'diwali', 'holi', 'rajyotsava', 'kannada', 'culture', 'music', 'art', 'movie', 'theater'],
    
    'Language': ['kannada', 'hindi', 'language', 'tamil', 'telugu', 'malayalam', 'speak', 'learn', 'local', 'native', 'imposition'],
    
    'Social_Life': ['friend', 'dating', 'relationship', 'lonely', 'meetup', 'social', 'group', 'hobby', 'activity', 'weekend', 'hangout'],
    
    'Health': ['hospital', 'doctor', 'medical', 'health', 'clinic', 'emergency', 'covid', 'vaccine', 'medicine', 'treatment', 'mental'],
    
    'Weather': ['rain', 'weather', 'monsoon', 'temperature', 'climate', 'flood', 'summer', 'winter', 'season'],
    
    'Politics': ['government', 'election', 'vote', 'bjp', 'congress', 'politician', 'cm', 'minister', 'policy', 'corruption'],
    
    'Pets_Animals': ['dog', 'cat', 'pet', 'animal', 'adopt', 'stray', 'rescue', 'kitten', 'puppy', 'vet'],
    
    'Education': ['college', 'university', 'school', 'education', 'student', 'exam', 'admission', 'course', 'degree', 'study'],
    
    'General_Discussion': []  # Catch-all for posts that don't fit other categories
}

def clean_text(text):
    """Clean and preprocess text"""
    if pd.isna(text):
        return ""
    
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    
    # Remove special characters but keep spaces
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra spaces
    text = ' '.join(text.split())
    
    return text

def assign_topic(title, selftext, topic_keywords):
    """
    Assign topic to a post based on keyword matching
    """
    # Combine title and text
    combined_text = clean_text(f"{title} {selftext}")
    
    topic_scores = {}
    
    # Score each topic
    for topic, keywords in topic_keywords.items():
        if topic == 'General_Discussion':
            continue
            
        score = 0
        for keyword in keywords:
            # Count occurrences of keyword
            score += combined_text.count(keyword.lower())
        
        topic_scores[topic] = score
    
    # Get topic with highest score
    if topic_scores and max(topic_scores.values()) > 0:
        return max(topic_scores, key=topic_scores.get)
    else:
        return 'General_Discussion'

def analyze_topics(df, topic_keywords):
    """
    Analyze and assign topics to all posts
    """
    print("\nAssigning topics to posts...")
    
    # Assign topics
    df['topic'] = df.apply(
        lambda row: assign_topic(row['title'], row['selftext'], topic_keywords),
        axis=1
    )
    
    # Show topic distribution
    print("\nTopic Distribution:")
    topic_counts = df['topic'].value_counts()
    for topic, count in topic_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {topic:20s}: {count:4d} posts ({percentage:5.2f}%)")
    
    return df

def analyze_trends(df):
    """
    Analyze trends over time
    """
    print("\n" + "="*60)
    print("TIME SERIES ANALYSIS")
    print("="*60)
    
    # Convert to datetime
    df['year'] = pd.to_datetime(df['created_utc']).dt.year
    df['month'] = pd.to_datetime(df['created_utc']).dt.to_period('M')
    
    # Top topics per year
    print("\nTop 3 Topics Per Year:")
    for year in sorted(df['year'].unique()):
        year_data = df[df['year'] == year]
        top_topics = year_data['topic'].value_counts().head(3)
        print(f"\n{year}:")
        for topic, count in top_topics.items():
            print(f"  {topic}: {count} posts")
    
    # Trending topics (comparing first half vs second half)
    midpoint_year = df['year'].median()
    first_half = df[df['year'] <= midpoint_year]
    second_half = df[df['year'] > midpoint_year]
    
    print(f"\n\nTopic Trends (Before {int(midpoint_year)} vs After):")
    
    for topic in df['topic'].unique():
        first_count = len(first_half[first_half['topic'] == topic])
        second_count = len(second_half[second_half['topic'] == topic])
        
        if first_count > 0:
            change = ((second_count - first_count) / first_count) * 100
            if abs(change) > 50:  # Only show significant changes
                trend = "📈 UP" if change > 0 else "📉 DOWN"
                print(f"  {topic:20s}: {trend} {abs(change):.0f}%")
    
    return df

def extract_keywords_per_topic(df, n_words=10):
    """
    Extract top keywords for each topic
    """
    print("\n" + "="*60)
    print("TOP KEYWORDS PER TOPIC")
    print("="*60)
    
    topic_keywords = {}
    
    for topic in df['topic'].unique():
        topic_posts = df[df['topic'] == topic]
        
        # Combine all text for this topic
        all_text = ' '.join(topic_posts['title'].fillna('') + ' ' + topic_posts['selftext'].fillna(''))
        all_text = clean_text(all_text)
        
        # Count words
        words = all_text.split()
        # Remove common stop words
        stop_words = {'the', 'is', 'in', 'and', 'to', 'a', 'of', 'for', 'on', 'with', 'this', 'that', 'it', 'from', 'are', 'was', 'be', 'have', 'has', 'been'}
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Get top words
        word_counts = Counter(words)
        top_words = word_counts.most_common(n_words)
        
        topic_keywords[topic] = [word for word, count in top_words]
        
        print(f"\n{topic}:")
        print(f"  {', '.join([word for word, count in top_words[:5]])}")
    
    return topic_keywords

def save_results(df, topic_keywords, output_file, keywords_file):
    """
    Save processed data and topic keywords
    """
    # Save main data
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✓ Data with topics saved to {output_file}")
    
    # Save topic keywords
    with open(keywords_file, 'w') as f:
        json.dump(topic_keywords, f, indent=2)
    print(f"✓ Topic keywords saved to {keywords_file}")

def main():
    """
    Main execution
    """
    print("="*60)
    print("BANGALORE SUBREDDIT - TOPIC MODELING & ANALYSIS")
    print("="*60)
    
    # Load data
    print(f"\nLoading data from {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    print(f"✓ Loaded {len(df)} posts")
    print(f"  Date range: {df['created_utc'].min()} to {df['created_utc'].max()}")
    
    # Assign topics
    df = analyze_topics(df, TOPIC_KEYWORDS)
    
    # Analyze trends
    df = analyze_trends(df)
    
    # Extract keywords
    topic_keywords = extract_keywords_per_topic(df)
    
    # Save results
    save_results(df, topic_keywords, OUTPUT_FILE, TOPICS_FILE)
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE! ðŸŽ‰")
    print("="*60)
    print(f"\nNext step: Build the dashboard!")
    print(f"You now have:")
    print(f"  1. {OUTPUT_FILE} - Posts with topic labels")
    print(f"  2. {TOPICS_FILE} - Topic keywords")

if __name__ == "__main__":
    main()
