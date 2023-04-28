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


# Define a function to set the page style
def set_page_style(primary_color):
    page_bg = f"rgba({primary_color[0]}, {primary_color[1]}, {primary_color[2]}, 1)"
    font_color = "#000000"
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background-color: {page_bg};
            color: {font_color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Add a color picker widget
primary_color = st.color_picker("Pick a primary color for the app", "#00FF00")

# Call the set_page_style function with the selected color
set_page_style(primary_color)

# Create date input box for selecting a date range
date_range = st.date_input("Select a date range", value=(datetime.now() - timedelta(days=7), datetime.now()))

# Create text input box for country code
country_code = st.text_input("Enter country code (e.g. us, gb, ca, au):")

# Create select slider to filter number of articles shown
num_articles = st.select_slider("Number of articles to show", options=list(range(0, 21)), value=10)

# Create a search button
search_button = st.button("Search")

# Create checkbox for toggling between map and chart
display_map = st.sidebar.checkbox("Display Map", value=True)
display_chart = st.sidebar.checkbox("Display Chart", value=True)

# Initialize a DataFrame to store the filtered results
filtered_df = pd.DataFrame()


# Define a function to filter the data
def filter_data(df, num_articles):
    # Filter the data based on the number of articles to show
    if num_articles > 0:
        filtered_df = df.iloc[:num_articles]
    else:
        filtered_df = df
    return filtered_df


if search_button:
    # Set API parameters
    if country_code:
        start_date = date_range[0].strftime('%Y-%m-%d')
        end_date = date_range[1].strftime('%Y-%m-%d')
        params = {
            "country": country_code,
            "apiKey": "9eebec314c544f61b0aef624863db955",
            "from": start_date,
            "to": end_date
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

            # Convert the article data to a DataFrame
            df = pd.DataFrame(table, columns=["Headline", "Link", "Author", "Date Posted"])

            # Filter the data based on the number of articles to show
            filtered_df = filter_data(df, num_articles)

            # Display the filtered results in a table
            st.table(filtered_df.style.set_properties(**{'width': '100%'}))

            # Create a map using Plotly Express if the checkbox is selected
            if display_map:
                geolocator = Nominatim(user_agent="my_app")
                location = geolocator.geocode(country_code)
                if location:
                    df_map = pd.DataFrame({'location': locations})
                    df_map['country'] = location.address
                    df_map['latitude'] = location.latitude
                    df_map['longitude'] = location.longitude
                    fig = px.scatter_mapbox(df_map, lat='latitude', lon='longitude', zoom=3, height=600, width=800)
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
                fig_bar = px.bar(df, x='date', y='title', labels={'date': 'Date', 'title': 'Number of articles'})
                fig_bar.update_layout(xaxis_range=[last_7_days[-1], last_7_days[0]])

                # Create a line chart using Plotly Express
                fig_line = px.line(df, x='date', y='title', labels={'date': 'Date', 'title': 'Number of articles'})
                fig_line.update_traces(line_color='red')
                fig_line.update_layout(xaxis_range=[last_7_days[-1], last_7_days[0]])

                # Create a chart container
                chart_container = st.container()
                with chart_container:
                    # Display both the bar chart and line chart
                    st.plotly_chart(fig_bar)
                    st.plotly_chart(fig_line)
        else:
            st.write("No articles found in the last 7 days for the selected country.")

    else:
        st.write("No articles found for the selected country.")
else:
    st.write("Enter a country code to get started.")
