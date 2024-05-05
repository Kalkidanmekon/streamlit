matplotlib == 3.5.0
import streamlit as st
import pydeck as pdk
import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('2017_Crashes.csv', nrows=10000)  # Reading Data file

# calculating the total number of fatal and non-fatal injuries
city_stats = df.groupby('CITY_TOWN_NAME').agg({'NUMB_FATAL_INJR': 'sum', 'NUMB_NONFATAL_INJR': 'sum', 'CRASH_NUMB': 'count'}).reset_index()

coords = df.groupby('CITY_TOWN_NAME')[['LAT', 'LON']].mean().reset_index()  #Grouping by city/town name and resetting index
city_data = pd.merge(city_stats, coords, on='CITY_TOWN_NAME')
city_data = city_data.dropna(subset=['LAT', 'LON'])

st.title("Massachusetts Car Crashes in 2017")
st.write("")

page = st.sidebar.selectbox("What would you like to see?", ["Car Crash statistics by City"
    , "Crashes by Junction Type", "Road Surface impact", "Lighting and Crashes"])    #Pages

if page == "Car Crash statistics by City":
    st.title(page)

    #Identifying slider range
    min_crashes, max_crashes = st.slider('Select the range of crashes:', min_value=0, max_value=500, value=(0, 500))


    filtered_data = city_data[(city_data['CRASH_NUMB'] >= min_crashes) & (city_data['CRASH_NUMB'] <= max_crashes)]

    view_state = pdk.ViewState(
        latitude=filtered_data['LAT'].mean(),
        longitude=filtered_data['LON'].mean(),
        zoom=7,
        pitch=0
    )


    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_data,
        get_position=['LON', 'LAT'],
        get_fill_color='[255, NUMB_FATAL_INJR * 2.55, NUMB_NONFATAL_INJR * 2.55, 200]',
        get_radius="(NUMB_FATAL_INJR + NUMB_NONFATAL_INJR) * 30",
        pickable=True
    )


    map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[scatterplot_layer],
        tooltip={"text": "{CITY_TOWN_NAME}\nFatal Injuries: {NUMB_FATAL_INJR}\nNon-Fatal Injuries: {NUMB_NONFATAL_INJR}\nCrashes: {CRASH_NUMB}"}
    )
    st.pydeck_chart(map)

elif page == "Crashes by Junction Type":

    junction_type_counts = df['RDWY_JNCT_TYPE_DESCR'].value_counts()
    st.title(page)
    st.bar_chart(junction_type_counts)
    st.pyplot(plt)

elif page == "Road Surface impact":
    # Displaying pie chart for percentage of crashes by road surface condition

    def calculate_road_condition_percentage(df):
        #Calculating the percentage of crashes by road surface condition
        road_conditions = df['ROAD_SURF_COND_DESCR'].value_counts(normalize=True) * 100
        return road_conditions


    def display_pie_chart(df, road_conditions, selected_condition=None):

        all_road_conditions = ['Dry', 'Unknown', 'Ice', 'Wet', 'Snow', 'Other', 'Water (standing, moving)', 'Slush',
                               'Sand, mud, dirt, oil, gravel', 'Not reported']

        if selected_condition is None:
            selected_condition = st.selectbox('Select a road condition:', all_road_conditions)

        filtered_data = df[df['ROAD_SURF_COND_DESCR'] == selected_condition]
        selected_condition_percentage = road_conditions[selected_condition]
        st.write(f"Percentage for {selected_condition}: {selected_condition_percentage:.2f}%")

        sizes = [filtered_data.shape[0], df.shape[0] - filtered_data.shape[0]]

        fig, ax = plt.subplots()
        wedges, texts = ax.pie(sizes, startangle=90, colors=plt.cm.tab20.colors[:2])
        ax.legend(wedges, ['Selected Condition', 'Other Conditions'], title="Road Conditions", loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        ax.set_title('Road Surface Conditions Impact on Crashes')
        ax.axis('equal')

        st.pyplot(fig)
        return selected_condition_percentage
    road_conditions = calculate_road_condition_percentage(df)
    selected_condition_percentage = display_pie_chart(df, road_conditions)

elif page == "Lighting and Crashes":

    filtered_df = df[~df['AMBNT_LIGHT_DESCR'].isin(['Unknown', 'Not reported', 'Other'])]


    light_conditions_counts = filtered_df['AMBNT_LIGHT_DESCR'].value_counts()


    st.title(page)
    plt.figure(figsize=(10, 6))
    light_conditions_counts.plot(kind='line', marker='o')
    plt.xticks(rotation=45)
    plt.xlabel("Ambient Light Condition")
    plt.ylabel("Number of Crashes")
    plt.grid(True)
    st.pyplot(plt)
