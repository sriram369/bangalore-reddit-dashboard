# 📊 Bengaluru Vibes Tracker: A 10-Year Analysis of r/bangalore

An interactive dashboard that visualizes a decade of discussions, trends, and sentiments from the r/bangalore subreddit, built with Streamlit, Pandas, and Plotly.



---

## 🚀 Live Dashboard

**[View the live Streamlit app here!]([r-bangalore] (https://r-bangalore.streamlit.app/))**

https://r-bangalore.streamlit.app/

---

## 📖 About This Project

This project was built to understand the pulse of Bengaluru over the last 10 years. By analyzing over 1,000 posts from the r/bangalore subreddit (from 2015 to 2025), this dashboard reveals what topics have defined the city's online conversation.

What are people talking about? Is traffic *really* getting worse? What topics are trending, and what has faded away? This dashboard answers those questions by visualizing the data.

### ✨ Key Features

* **📈 At a Glance:** Key metrics for the entire 10-year period, including total posts analyzed, the all-time top topic, and the most active users.
* **🗓️ Topic Trends (2015-2025):** A stacked bar chart showing the rise and fall of 15 different topics, year by year.
* **📊 Overall Topic Distribution:** A pie chart showing the percentage share of every topic discussed.
* **📉 Topic Deep-Dive:** A dropdown menu that lets you select any topic (like "Traffic," "Housing," or "Food") and see its specific post-count trend over time.
* **🏆 Top Posts:** A searchable table of the highest-scoring posts of all time.

### 🛠️ Tech Stack

* **Data Analysis:** Python, Pandas
* **Dashboard & Visualization:** Streamlit, Plotly
* **Data Collection:** `pushshift_data_collector.py` (using Pushshift API)
* **Topic Modeling:** `topic-modeling-script.py` (using keyword-based categorization)

---

## ⚙️ Our Methodology: The 5-Phase Plan

This project was built in five distinct phases, from raw data to a deployed application.

### Phase 1: Historical Data Collection
* **Goal:** Get 10 years of post data from the r/bangalore subreddit.
* **Action:** Used the `pushshift_data_collector.py` script to query the Pushshift API, which archives Reddit data.
* **Output:** `bangalore_historical_large.csv` — A single, massive CSV with raw post data (title, author, score, text, etc.).

### Phase 2: Data Processing & Topic Modeling
* **Goal:** Clean the data and assign a relevant topic to every single post.
* **Action:** Ran the `topic-modeling-script.py`. This script loads the large CSV, cleans the text, and uses a predefined dictionary of keywords (`topic_keywords.json`) to categorize each post into one of 15 topics (e.g., "Traffic," "Housing," "Food," "Jobs").
* **Output:** `bangalore_with_topics.csv` — The dataset, now enriched with a `topic` column for every post.

### Phase 3: Time-Series & Insight Generation
* **Goal:** Pre-calculate all the data needed for the dashboard charts to ensure the app loads instantly.
* **Action:** Ran the `dashboard-data-generator.py` script. This script processed `bangalore_with_topics.csv` to create aggregated dataframes for:
    * `topic_trends`: Post counts per topic, per year.
    * `monthly_trends`: Post counts per topic, per month.
* **Output:** `dashboard_data.json` — A single, clean JSON file containing all the data the dashboard needs.

### Phase 4: Interactive Dashboard Creation
* **Goal:** Build the front-end application to visualize the data.
* **Action:** Wrote the `dashboard.py` Streamlit script. This app loads `dashboard_data.json` and uses Plotly to generate all the interactive charts and metrics.
* **Output:** A fully functional local web application.

### Phase 5: Deployment
* **Goal:** Put the dashboard online for public access.
* **Action:**
    1.  Created a `requirements.txt` file.
    2.  Uploaded the project (`dashboard.py`, `dashboard_data.json`, `requirements.txt`) to this GitHub repository.
    3.  Linked the repository to [Streamlit Community Cloud](https://streamlit.io/cloud) for free, automated deployment.

---

## 💻 How to Run This Project Locally

Want to run this dashboard on your own machine?

**Prerequisites:**
* Python 3.9+
* `pip` (Python package installer)

**Installation:**

1.  **Clone this repository:**
    ```sh
    git clone [https://github.com/your-username/bangalore-reddit-dashboard.git](https://github.com/your-username/bangalore-reddit-dashboard.git)
    cd bangalore-reddit-dashboard
    ```

2.  **Install the required libraries:**
    ```sh
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    ```sh
    streamlit run dashboard.py
    ```

Your browser will automatically open, and you'll see the dashboard running locally!
