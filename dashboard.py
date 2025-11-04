import streamlit as st
import pandas as pd
import plotly.express as px
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Bengaluru Vibes Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Data Loading Function ---
@st.cache_data  # Cache the data to avoid reloading on every interaction
def load_data(filepath):
    """Loads the dashboard data from the specified JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error(f"Error: The file '{filepath}' was not found. Make sure it's in the same directory as this script.")
        return None
    except json.JSONDecodeError:
        st.error(f"Error: Could not decode the JSON from '{filepath}'. The file might be corrupted.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Load Data ---
data = load_data("dashboard_data.json")

# If data loading failed, stop the app
if data is None:
    st.stop()

# --- Main Dashboard ---
st.title("📊 Bengaluru Vibes Tracker")
st.markdown("An interactive analysis of r/bangalore posts from 2015-2025")

# --- Sidebar ---
st.sidebar.header("About This Project")
st.sidebar.info(
    "This dashboard visualizes historical trends from the r/bangalore subreddit. "
    "All data was processed from `bangalore_historical_large.csv` into the "
    "final `dashboard_data.json` which powers this app."
)
st.sidebar.header("Key Insights")
st.sidebar.markdown(f"**Total Posts Analyzed:** `{data['insights']['total_posts']}`")
st.sidebar.markdown(f"**Date Range:** `{data['insights']['date_range']['start']}` to `{data['insights']['date_range']['end']}`")
st.sidebar.markdown(f"**Average Score:** `{data['insights']['average_score']:.1f}`")
st.sidebar.markdown(f"**Average Comments:** `{data['insights']['average_comments']:.1f}`")

# --- Key Metrics ---
st.header("📈 At a Glance")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Posts Analyzed", data['insights']['total_posts'])
col2.metric(
    "Top Topic", 
    data['insights']['top_topic']['name'],
    f"{data['insights']['top_topic']['percentage']:.1f}%"
)
col3.metric("Most Commented Topic", data['insights']['most_discussed'][0]['topic'].replace("_", " "))
col4.metric("Trending Up", data['insights']['trending_topics'][0]['topic'])

st.markdown("---") # Adds a nice separator
col5, col6, col7 = st.columns(3)

# Add the new insights we just found:
col5.metric(
    "Most Active Poster", 
    "Pure-Marionberry7778", 
    "11 posts"
)

col6.metric(
    "Top Meaningful Word", 
    "looking", 
    "74 mentions"
)

col7.metric(
    "Top 'Action' Word", 
    "removed", 
    "339 mentions"
)

# --- END: NEW CODE SECTION ---
# --- Main Visualizations ---
st.markdown("---")
col_main1, col_main2 = st.columns([2, 1])

with col_main1:
    # 1. Topic Trends Over Time (Stacked Bar Chart)
    st.subheader("Topic Trends (2015-2025)")
    df_trends = pd.DataFrame(data['topic_trends']).set_index('year')
    fig_trends = px.bar(
        df_trends,
        x=df_trends.index,
        y=df_trends.columns,
        title="Annual Post Count by Topic",
        labels={'value': 'Number of Posts', 'year': 'Year', 'variable': 'Topic'},
        barmode='stack'
    )
    fig_trends.update_layout(legend_title_text='Topics')
    st.plotly_chart(fig_trends, use_container_width=True)

with col_main2:
    # 2. Overall Topic Distribution (Pie Chart)
    st.subheader("Overall Topic Distribution")
    df_dist = pd.DataFrame(data['topic_distribution'])
    fig_pie = px.pie(
        df_dist,
        names='name',
        values='value',
        title="Share of All Discussions",
        color='name',
        color_discrete_map={item['name']: item['color'] for item in data['topic_distribution']}
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)


# --- Deep-Dive Section ---
st.markdown("---")
st.header("Topic Deep-Dive")

# 3. Monthly Topic Deep-Dive (Selectbox + Line Chart)
df_monthly = pd.DataFrame(data['monthly_trends']).set_index('month').fillna(0)
# Get a list of all topics available in the monthly data
all_topics = sorted([col for col in df_monthly.columns if col != 'month'])

selected_topic = st.selectbox(
    "Select a Topic to See its Monthly Trend",
    all_topics,
    index=all_topics.index('Traffic') # Default to 'Traffic'
)

if selected_topic:
    fig_monthly = px.line(
        df_monthly,
        x=df_monthly.index,
        y=selected_topic,
        title=f"Monthly Post Trend for: {selected_topic.replace('_', ' ')}",
        labels={'month': 'Month', selected_topic: 'Number of Posts'},
        markers=True
    )
    st.plotly_chart(fig_monthly, use_container_width=True)


# --- Top Posts & Details ---
st.markdown("---")
st.header("Top Posts & Details")

col_detail1, col_detail2 = st.columns(2)

with col_detail1:
    # 4. Most Discussed Topics (Horizontal Bar Chart)
    st.subheader("Most Discussed Topics")
    df_discussed = pd.DataFrame(data['insights']['most_discussed'])
    fig_discussed = px.bar(
        df_discussed,
        x='total_comments',
        y='topic',
        orientation='h',
        title="Total Comments by Topic (All Time)",
        labels={'total_comments': 'Total Comments', 'topic': 'Topic'}
    )
    fig_discussed.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_discussed, use_container_width=True)

with col_detail2:
    # 5. Top Posts (DataFrame)
    st.subheader("Top Posts of All Time")
    df_top_posts = pd.DataFrame(data['top_posts'])
    # Clean up topic names for display
    df_top_posts['topic'] = df_top_posts['topic'].str.replace('_', ' ')
    st.dataframe(
        df_top_posts,
        column_config={
            "title": "Post Title",
            "score": st.column_config.NumberColumn("Score", format="%d 🔥"),
            "num_comments": st.column_config.NumberColumn("Comments", format="%d 💬"),
            "year": "Year",
            "topic": "Topic"
        },
        use_container_width=True,
        hide_index=True
    )