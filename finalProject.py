import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta

# Set API endpoint
url = "https://newsapi.org/v2/top-headlines"

# Create Streamlit app
st.set_page_config(page_title="Top Headlines", page_icon="📰", layout="wide")
st.title("Top Headlines")
st.markdown("Search for top headlines by country")

# Create text input box for country code
country_code = st.sidebar.text_input("Enter country code (e.g. us, gb, ca, au):")

# Create checkbox for toggling between map and chart
display_map = st.sidebar.checkbox("Display Map", value=True)
display_chart = st.sidebar.checkbox("Display Chart", value=True)

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
        locations = []
        for i, article in enumerate(articles):
            row = [article["title"],
                   article["url"],
                   article["source"]["name"],
                   article["publishedAt"]
                   ]
            table.append(row)
            if article["author"]:
                locations.append(article["author"])
            else:
                locations.append(article["source"]["name"])

        st.table(pd.DataFrame(table, columns=["Headline", "Link", "Author", "Date Posted"]).style.set_properties(
            **{'width': '100%'}))

        # Create a map using Plotly Express if the checkbox is selected
        if display_map:
            geolocator = Nominatim(user_agent="my_app")
            location = geolocator.geocode(country_code)
            if location:
                df = pd.DataFrame({'location': locations})
                df['country'] = location.address
                df['latitude'] = location.latitude
                df['longitude'] = location.longitude
                fig = px.scatter_mapbox(df, lat='latitude', lon='longitude', zoom=3, height=600, width=800)
                fig.update_layout(mapbox_style="carto-positron", mapbox_domain={"x": [0, 1], "y": [0, 1]})
                st.plotly_chart(fig)
            else:
                st.write("Could not find coordinates for the selected country.")

        # Create a pandas DataFrame with article dates and count the number of articles per day
        df = pd.DataFrame(articles)
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df['date'] = df['publishedAt'].dt.date
        df = df.groupby('date').count().reset_index()

        # Create a bar chart using Plotly Express if the checkbox is selected
        if display_chart and not df.empty:
            # Filter the data to only show the last 7 days
            last_7_days = [(datetime.now() - timedelta(days=i)).date() for i in range(7)]
            df = df[df['date'].isin(last_7_days)]
            fig = px.bar(df, x='date', y='title', labels={'date': 'Date', 'title': 'Number of articles'})
            fig.update_layout(xaxis_range=[last_7_days[-1], last_7_days[0]])
            st.plotly_chart(fig)
        else:
            st.write("No articles found in the last 7 days for the selected country.")

    else:
        st.write("No articles found for the selected country.")
else:
    st.write("Enter a country code to get started.")