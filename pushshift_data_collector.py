import requests
import pandas as pd
from datetime import datetime
import time

# ===== CONFIGURATION =====
SUBREDDIT = "bangalore"
OUTPUT_FILE = "bangalore_historical_large.csv"

# Date range: Jan 2015 to Nov 2025
START_DATE = int(datetime(2015, 1, 1).timestamp())
END_DATE = int(datetime(2025, 11, 4).timestamp())

# We'll collect in chunks (yearly batches)
POSTS_PER_REQUEST = 100  # Pushshift max

def get_posts_pushshift(subreddit, after, before, limit=100):
    """
    Get posts from Pushshift API
    """
    url = "https://api.pullpush.io/reddit/search/submission"
    
    params = {
        'subreddit': subreddit,
        'after': after,
        'before': before,
        'size': limit,
        'sort': 'created_utc',
        'sort_type': 'asc'
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"Error: Status code {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def collect_year_data(year):
    """
    Collect all posts from a specific year
    """
    print(f"\n{'='*60}")
    print(f"Collecting data for year {year}")
    print(f"{'='*60}")
    
    start = int(datetime(year, 1, 1).timestamp())
    end = int(datetime(year, 12, 31, 23, 59, 59).timestamp())
    
    all_posts = []
    current_after = start
    
    while current_after < end:
        print(f"  Fetching posts after {datetime.fromtimestamp(current_after)}")
        
        posts = get_posts_pushshift(SUBREDDIT, current_after, end, POSTS_PER_REQUEST)
        
        if not posts:
            print(f"  No more posts found for {year}")
            break
        
        all_posts.extend(posts)
        print(f"  Got {len(posts)} posts | Total so far: {len(all_posts)}")
        
        # Update after timestamp to last post's timestamp + 1
        current_after = posts[-1]['created_utc'] + 1
        
        # Be nice to the API
        time.sleep(1)
        
        # Safety check - if we got less than requested, we're done
        if len(posts) < POSTS_PER_REQUEST:
            print(f"  Reached end of data for {year}")
            break
    
    print(f"✓ Collected {len(all_posts)} posts from {year}")
    return all_posts

def clean_and_save_data(all_posts, filename):
    """
    Clean the data and save to CSV
    """
    print(f"\nCleaning and saving {len(all_posts)} posts...")
    
    cleaned_posts = []
    
    for post in all_posts:
        try:
            cleaned_post = {
                'id': post.get('id', ''),
                'title': post.get('title', ''),
                'author': post.get('author', '[deleted]'),
                'score': post.get('score', 0),
                'num_comments': post.get('num_comments', 0),
                'created_utc': datetime.fromtimestamp(post.get('created_utc', 0)),
                'selftext': post.get('selftext', '')[:1000],  # First 1000 chars
                'url': post.get('url', ''),
                'is_self': post.get('is_self', False),
                'link_flair_text': post.get('link_flair_text', '')
            }
            cleaned_posts.append(cleaned_post)
        except Exception as e:
            print(f"Error processing post: {e}")
            continue
    
    df = pd.DataFrame(cleaned_posts)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['id'])
    
    # Sort by date
    df = df.sort_values('created_utc')
    
    # Save to CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    
    print(f"\n✓ Data saved to {filename}")
    print(f"  Total unique posts: {len(df)}")
    print(f"  Date range: {df['created_utc'].min()} to {df['created_utc'].max()}")
    
    # Show stats per year
    df['year'] = df['created_utc'].dt.year
    posts_per_year = df['year'].value_counts().sort_index()
    print("\nPosts per year:")
    for year, count in posts_per_year.items():
        print(f"  {year}: {count} posts")
    
    return df

def main():
    """
    Main execution function
    """
    print("="*60)
    print("BANGALORE SUBREDDIT - LARGE HISTORICAL DATA COLLECTION")
    print("Using Pushshift API")
    print("="*60)
    
    all_posts = []
    
    # Collect year by year from 2015 to 2025
    for year in range(2015, 2026):
        year_posts = collect_year_data(year)
        all_posts.extend(year_posts)
        
        print(f"\nTotal posts collected so far: {len(all_posts)}")
        
        # Save intermediate results every few years
        if year % 3 == 0:
            print(f"\n💾 Saving intermediate results...")
            clean_and_save_data(all_posts, f"bangalore_intermediate_{year}.csv")
    
    # Final save
    print("\n" + "="*60)
    print("FINAL DATA PROCESSING")
    print("="*60)
    
    df = clean_and_save_data(all_posts, OUTPUT_FILE)
    
    print("\n" + "="*60)
    print("COLLECTION COMPLETE! ðŸŽ‰")
    print("="*60)
    print(f"Total posts collected: {len(df)}")
    print(f"\nNext steps:")
    print(f"1. Open {OUTPUT_FILE} to see your data")
    print(f"2. We'll now build topic modeling to categorize posts")
    print(f"3. Then create the time-series visualizations")

if __name__ == "__main__":
    main()