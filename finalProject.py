import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Newsdata API endpoint
url = "https://newsapi.org/v2/top-headlines"

# Newsdata API key
api_key = "9eebec314c544f61b0aef624863db955"

# Define a function to fetch news data for a given location
def get_news_data(location):
    # Define query parameters
    params = {
        "apikey": api_key,
        "language": "en",
        "sort_by": "relevancy",
        "q": location
    }

    # Send a GET request to the Newsdata API
    response = requests.get(url, params=params)

    # Convert the response to a Pandas dataframe
    news_df = pd.DataFrame(response.json()["articles"])

    # Return the news dataframe
    return news_df

# Define the Streamlit app
def app():
    # Set the title of the app
    st.title("Global News Explorer")

    # Ask the user for a location
    location = st.text_input("Enter a location:")

    # Fetch the news data for the specified location
    news_df = get_news_data(location)

    # Display the news articles
    st.subheader("News Articles")
    st.dataframe(news_df)

    # Create a map showing the location of the news articles
    st.subheader("Map of News Coverage")
    if not news_df.empty:
        # Group the news articles by country and count the number of articles
        country_counts = news_df.groupby("country").size().reset_index(name="count")

        # Create a choropleth map of the news coverage
        fig = px.choropleth(
            country_counts,
            locations="country",
            color="count",
            color_continuous_scale=px.colors.sequential.Plasma,
            projection="natural earth",
        )
        st.plotly_chart(fig)

    # Create a plot showing the amount of news coverage per day
    st.subheader("News Coverage Over Time")
    if not news_df.empty:
        # Convert the publishedAt column to a datetime object
        news_df["publishedAt"] = pd.to_datetime(news_df["publishedAt"])

        # Group the news articles by date and count the number of articles
        daily_counts = news_df.groupby(pd.Grouper(key="publishedAt", freq="D")).size().reset_index(name="count")

        # Create a line plot of the daily news coverage
        fig = go.Figure(
            go.Scatter(
                x=daily_counts["publishedAt"],
                y=daily_counts["count"],
                mode="lines+markers",
            )
        )
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Articles",
        )
        st.plotly_chart(fig)

# Run the Streamlit app
if __name__ == "__main__":
    app()
