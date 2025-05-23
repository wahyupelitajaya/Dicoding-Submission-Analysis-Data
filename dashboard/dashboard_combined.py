import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
day_df = pd.read_csv("https://raw.githubusercontent.com/wahyupelitajaya/Dicoding-Submission-Analysis-Data/refs/heads/main/data/day.csv")
hour_df = pd.read_csv("https://raw.githubusercontent.com/wahyupelitajaya/Dicoding-Submission-Analysis-Data/refs/heads/main/data/hour.csv")

# Data cleaning and renaming columns for day_df
day_df['dteday'] = pd.to_datetime(day_df['dteday'])
day_df = day_df.drop(['instant', 'holiday'], axis=1)
day_df = day_df.rename(columns={
    'dteday': 'date',
    'yr': 'year',
    'mnth': 'month',
    'weekday': 'day',
    'workingday': 'day_type',
    'weathersit': 'weather_type',
    'atemp': 'feels',
    'hum': 'humidity',
    'cnt': 'total'
})
day_df['season'] = day_df['season'].replace({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}).astype(str)
day_df['month'] = day_df['month'].replace({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}).astype(str)
day_df['day'] = day_df['day'].replace({
    0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
    4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}).astype(str)
day_df['day_type'] = day_df['day_type'].replace({0: 'Working Day', 1: 'Weekend'}).astype(str)
day_df['weather_type'] = day_df['weather_type'].replace({
    1: 'Clear/Cloudy', 2: 'Mist', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Fog'
}).astype(str)

# Data cleaning and renaming columns for hour_df
hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
hour_df = hour_df.drop(['instant', 'holiday'], axis=1)
hour_df = hour_df.rename(columns={
    'dteday': 'date',
    'yr': 'year',
    'mnth': 'month',
    'hr': 'hour',
    'weekday': 'day',
    'workingday': 'day_type',
    'weathersit': 'weather_type',
    'atemp': 'feels',
    'hum': 'humidity',
    'cnt': 'total'
})
hour_df['season'] = hour_df['season'].replace({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}).astype(str)
hour_df['month'] = hour_df['month'].replace({
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
}).astype(str)
hour_df['day'] = hour_df['day'].replace({
    0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
    4: 'Thursday', 5: 'Friday', 6: 'Saturday'
}).astype(str)
hour_df['day_type'] = hour_df['day_type'].replace({0: 'Working Day', 1: 'Weekend'}).astype(str)
hour_df['weather_type'] = hour_df['weather_type'].replace({
    1: 'Clear/Cloudy', 2: 'Mist', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Fog'
}).astype(str)

# Sidebar filters for global filtering
st.sidebar.header("Filter Data")

years = sorted(day_df['year'].unique())
selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)

seasons = sorted(day_df['season'].unique())
selected_seasons = st.sidebar.multiselect("Select Season(s)", seasons, default=seasons)

day_types = sorted(day_df['day_type'].unique())
selected_day_types = st.sidebar.multiselect("Select Day Type(s)", day_types, default=day_types)

weather_types = sorted(day_df['weather_type'].unique())
selected_weather_types = st.sidebar.multiselect("Select Weather Type(s)", weather_types, default=weather_types)

# Filter dataframes based on selections
filtered_day_df = day_df[
    (day_df['year'].isin(selected_years)) &
    (day_df['season'].isin(selected_seasons)) &
    (day_df['day_type'].isin(selected_day_types)) &
    (day_df['weather_type'].isin(selected_weather_types))
]

filtered_hour_df = hour_df[
    (hour_df['year'].isin(selected_years)) &
    (hour_df['season'].isin(selected_seasons)) &
    (hour_df['day_type'].isin(selected_day_types)) &
    (hour_df['weather_type'].isin(selected_weather_types))
]

# Streamlit dashboard layout
st.title("Bike Sharing Data Analysis Dashboard")

# Display Seasonal Bike Usage by Year in its own container
with st.container():
    st.header("Seasonal Bike Usage by Year")
    season_counts = filtered_day_df.groupby(['season', 'year']).agg({'total': 'sum'}).reset_index()
    plt.figure(figsize=(8, 5))
    sns.barplot(data=season_counts, x='season', y='total', hue='year', palette='viridis')
    plt.xlabel("Season")
    plt.ylabel("Total Bike Rentals")
    plt.title("Total Bike Rentals by Season and Year")
    plt.grid(True, axis='y', linestyle='--')
    st.pyplot(plt)
    plt.clf()

# Display Bike Usage by Day Type in its own container
with st.container():
    st.header("Bike Usage by Day Type")
    day_type_totals = filtered_day_df.groupby('day_type')['total'].sum()
    plt.figure(figsize=(6, 6))
    plt.pie(day_type_totals, labels=day_type_totals.index, autopct='%1.1f%%', startangle=90)
    plt.title("Total Bike Shares by Day Type")
    st.pyplot(plt)
    plt.clf()

# Display Weather Impact on Bike Usage by Year
with st.container():
    st.header("Weather Impact on Bike Usage by Year")
    weather_counts = filtered_day_df.groupby(['weather_type', 'year']).agg({'total': 'sum'}).reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=weather_counts, x='weather_type', y='total', hue='year', palette='viridis')
    plt.xlabel("Weather Type")
    plt.ylabel("Total Bike Rentals")
    plt.title("Total Bike Rentals by Weather Type and Year")
    plt.grid(True, axis='y', linestyle='--')
    st.pyplot(plt)
    plt.clf()

# Display Clustering of Casual and Registered Users by Month
with st.container():
    st.header("Clustering of Casual and Registered Users by Month")

    def casual_and_registered(df, low_threshold=(30000, 200000), medium_threshold=(50000, 300000)):
        monthly_data = df.groupby('month').agg({'casual': 'sum', 'registered': 'sum'})
        clusters = {}
        low_casual, low_registered = low_threshold
        med_casual, med_registered = medium_threshold

        for month, row in monthly_data.iterrows():
            casual = row['casual']
            registered = row['registered']

            if casual < low_casual and registered < low_registered:
                cluster_name = 'Low Usage'
            elif casual < med_casual and registered < med_registered:
                cluster_name = 'Medium Usage'
            else:
                cluster_name = 'High Usage'

            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append((casual, registered, month))

        plt.figure(figsize=(10, 6))
        for cluster_name, dots in clusters.items():
            x_values = [point[0] for point in dots]
            y_values = [point[1] for point in dots]
            month_labels = [point[2] for point in dots]
            plt.scatter(x_values, y_values, label=cluster_name)
            for j, month in enumerate(month_labels):
                plt.text(x_values[j], y_values[j], month, fontsize=8, ha='right', va='bottom')

        plt.xlabel('Total Casual Users')
        plt.ylabel('Total Registered Users')
        plt.title('Clustering of Casual and Registered Users by Month')
        plt.legend()
        plt.grid(True)
        st.pyplot(plt)
        plt.clf()

    casual_and_registered(filtered_hour_df)
