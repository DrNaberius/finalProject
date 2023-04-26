import streamlit as st
import pandas as pd
import requests

# Set up the API endpoint and parameters
url = "https://api.newsdata.io/v1/news"
params = {
    "apikey": "pub_20640989cdbc220e019539b45ae6f2ff6ec8f",
    "language": "en",
    "sort_by": "relevancy"
}

# Define a function to get news data for a given location
def get_news_data(location):
    params["q"] = location
    response = requests.get(url, params=params)
    data = response.json()
    return pd.json_normalize(data["data"])

# Define the Streamlit app
def app():
    st.title("Global News")
    st.write("Enter a location to see the latest news:")
    location = st.text_input("Location", "United States")

    if st.button("Get News"):
        news_df = get_news_data(location)
        st.write(news_df)

# Run the app
if __name__ == "__main__":
    app()
