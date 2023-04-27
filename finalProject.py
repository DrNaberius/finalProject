import streamlit as st
import requests

# Set API endpoint
url = "https://newsapi.org/v2/top-headlines"

# Create Streamlit app
st.title("Top Headlines")
st.markdown("Search for top headlines by country")

# Create text input box for country code
country_code = st.text_input("Enter country code (e.g. us, gb, ca, au):")

# Set API parameters
if country_code:
    params = {
        "country": country_code,
        "apiKey": "9eebec314c544f61b0aef624863db955"
    }

    # Make API call and parse JSON response
    response = requests.get(url, params=params).json()
    articles = response["articles"]

    # Display article information in a table
    if articles:
        table = []
        for i, article in enumerate(articles):
            row = [
                str(i+1),
                article["title"],
                article["description"],
                article["url"],
                article["source"]["name"],
                article["publishedAt"]
            ]
            table.append(row)
        st.table(table)
    else:
        st.write("No articles found for the selected country.")
else:
    st.write("Enter a country code to get started.")