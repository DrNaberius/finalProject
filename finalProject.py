import streamlit as st
import pandas as pd
import numpy as np
import requests
from bokeh.plotting import figure, show
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models import ColumnDataSource, HoverTool

# Define the NewsData.io API URL
NEWS_API_URL = "https://newsdata.io/api/1/news"

# Define the Bokeh tile provider for the map
tile_provider = get_provider(Vendors.CARTODBPOSITRON_RETINA)

# Define the function to retrieve news articles from NewsData.io API
def get_news(location):
    payload = {"apikey": "pub_20640989cdbc220e019539b45ae6f2ff6ec8f", "q": location}
    response = requests.get(NEWS_API_URL, params=payload)
    return response.json()

# Define the Streamlit app
def main():
    # Set the title and page configuration
    st.set_page_config(page_title="Global News", page_icon=":newspaper:", layout="wide")
    st.title("Global News")

    # Get the user input for the location
    location = st.text_input("Enter a location:", "New York")

    # Get the news articles for the location
    news_json = get_news(location)
    news_df = pd.json_normalize(news_json)

    # Create the map
    p = figure(x_range=(-20000000, 20000000), y_range=(-10000000, 10000000),
               x_axis_type="mercator", y_axis_type="mercator")
    p.add_tile(tile_provider)

    # Add the news article markers to the map
    source = ColumnDataSource(data=dict(lon=news_df['location.long'], lat=news_df['location.lat'],
                                         title=news_df['title'], source=news_df['source']))
    hover_tool = HoverTool(tooltips=[("Title", "@title"), ("Source", "@source")])
    p.add_tools(hover_tool)
    p.circle(x="lon", y="lat", size=10, fill_color="blue", fill_alpha=0.8, source=source)

    # Display the map
    st.bokeh_chart(p, use_container_width=True)

    # Group the news articles by date and count the number of articles per day
    news_df['published'] = pd.to_datetime(news_df['published'])
    daily_news_count = news_df.groupby(news_df['published'].dt.date).size().reset_index(name='count')

    # Create the plot graph
    plot = figure(x_axis_type="datetime", title="News coverage over time", plot_height=350, plot_width=800)
    plot.line(x=daily_news_count['published'], y=daily_news_count['count'], line_width=2)
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'Number of articles'

    # Display the plot graph
    st.bokeh_chart(plot, use_container_width=True)

    # Display the news articles in a table
    st.write(news_df[['title', 'source', 'published', 'link']])

if __name__ == "__main__":
    main()
