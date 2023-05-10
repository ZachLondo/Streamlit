import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from PIL import Image


# Read in data (https://stackoverflow.com/questions/55240330/how-to-read-csv-file-from-github-using-pandas)
path = '/Users/Londo/Desktop/CS230/CS230 Final Project/stadiums-geocoded.txt'
df = pd.read_csv(path)

# Changing all state abbreviations to their full name (https://stackoverflow.com/questions/70127242/changing-abbreviated-state-names-with-full-name)
state_abbrev = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
}

df['state'] = df['state'].replace(state_abbrev)

# Adding Streamlit header
st.title('Final Project - NCAA Football Stadiums')

image = Image.open('https://github.com/ZachLondo/Streamlit/blob/main/SpartanStadium.jpg')

st.image(image, caption='Spartan Stadium')

# Defining search fields
## A loop that iterates through items in a list, dictionary, or data frame
all_conferences = ['All Conferences']
for conference in df['conference'].unique():
    all_conferences.append(conference)
## A list comprehension
all_teams = ['All Teams'] + [team for team in df['team'].unique().tolist()]
all_divisions = ['All Divisions'] + df['div'].unique().tolist()
all_states = ['All States'] + df['state'].unique().tolist()

# Add label to the sidebar for clarity
st.sidebar.title('Map Controls')

# Sidebar control - Division, Conference, Team
division = st.sidebar.selectbox('Division', all_divisions)
if division != 'All Divisions':
    filtered_conferences = df.loc[df['div'] == division, 'conference'].unique()
    all_conferences = ['All Conferences'] + filtered_conferences.tolist()
    conference = st.sidebar.selectbox('Conference', all_conferences)
    if conference != 'All Conferences':
        filtered_teams = df.loc[(df['div'] == division) & (df['conference'] == conference), 'team'].unique()
        all_teams = ['All Teams'] + filtered_teams.tolist()
        team = st.sidebar.selectbox('Team', all_teams)
    else:
        team = st.sidebar.selectbox('Team', all_teams)
else:
    conference = st.sidebar.selectbox('Conference', all_conferences)
    if conference != 'All Conferences':
        filtered_teams = df.loc[df['conference'] == conference, 'team'].unique()
        all_teams = ['All Teams'] + filtered_teams.tolist()
        team = st.sidebar.selectbox('Team', all_teams)
    else:
        team = st.sidebar.selectbox('Team', all_teams)


# Filter data based on sidebar controls
if division != 'All Divisions':
    filtered_df = df.loc[df['div'] == division]
    if conference != 'All Conferences' and team != 'All Teams':
        filtered_df = filtered_df.loc[(filtered_df['conference'] == conference) & (filtered_df['team'] == team)]
    elif conference != 'All Conferences':
        filtered_df = filtered_df.loc[filtered_df['conference'] == conference]
else:
    if conference != 'All Conferences' and team != 'All Teams':
        filtered_df = df.loc[(df['conference'] == conference) & (df['team'] == team)]
    elif conference != 'All Conferences':
        filtered_df = df.loc[df['conference'] == conference]
    else:
        filtered_df = df.copy()


# Define new selectbox adding various filters
sort_by = st.sidebar.selectbox('Sort By', ['Capacity', 'Built', 'State'])


if sort_by == 'Capacity':
    capacity_range = st.sidebar.radio("Select Capacity Range", ["All", "Custom"])
    if capacity_range == "Custom":
        min_cap, max_cap = st.sidebar.slider("Capacity Range", int(filtered_df.capacity.min()), int(filtered_df.capacity.max()), (int(filtered_df.capacity.min()), int(filtered_df.capacity.max())))
        filtered_df = filtered_df.loc[(filtered_df['capacity'] >= min_cap) & (filtered_df['capacity'] <= max_cap)]

elif sort_by == 'Built':
    built_range = st.sidebar.radio("Select Year Built", ["All", "Custom"])
    if built_range == "Custom":
        min_cap, max_cap = st.sidebar.slider("Capacity Range", int(filtered_df.built.min()), int(filtered_df.built.max()), (int(filtered_df.built.min()), int(filtered_df.built.max())))
        filtered_df = filtered_df.loc[(filtered_df['built'] >= min_cap) & (filtered_df['built'] <= max_cap)]

## A function with two or more parameters, one of which has a default value
elif sort_by == 'State':
    states = st.sidebar.multiselect('Select States', all_states, default=['All States'])
    if 'All States' not in states:
        filtered_df = filtered_df.loc[filtered_df['state'].isin(states)]

# Title for map
st.subheader('Stadium Map')
'''Controls located on the left sidebar'''

# Display the map - (https://towardsdatascience.com/3-easy-ways-to-include-interactive-maps-in-a-streamlit-app-b49f6a22a636)
fig = px.scatter_mapbox(
    filtered_df,
    lat="latitude",
    lon="longitude",
    hover_name="stadium",
    hover_data=["team", "capacity"],
    color_discrete_sequence=["blue"],
    zoom=3,
    height=300,
)
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.update_layout(mapbox_bounds={"west": -180, "east": -50, "south": 20, "north": 90})
st.plotly_chart(fig)


# Aggregate capacity grouped by Division, Conference, State
capacity_by_div = df.groupby('div')['capacity'].sum().reset_index()
capacity_by_conf = df.groupby('conference')['capacity'].sum().reset_index()
capacity_by_state = df.groupby('state')['capacity'].sum().reset_index()

# Title for bar chart controls
st.subheader('Bar Chart With Filters')

# Selectbox to allow the user to choose what to filter by
agg_group_by = st.selectbox('Sort By', ['Division', 'Conference', 'State'])

"""
This function takes a dataframe and a grouping variable and returns a plotly bar chart showing
the capacity grouped by the selected variable.
"""

## A function with two or more parameters, one of which has a default value
def plot_capacity_by_group(df, group_by='conference'):
    capacity_by_group = df.groupby(group_by)['capacity'].sum().reset_index()
    fig = px.bar(capacity_by_group, x=group_by, y='capacity', color=group_by, title='Capacity by '+group_by)
    fig.update_xaxes(title=group_by)
    fig.update_yaxes(title='Capacity')
    fig.update_layout(xaxis={'categoryorder': 'total descending'})  ## sort by descending order of capacity
    st.plotly_chart(fig)

if agg_group_by == 'Division':
    plot_capacity_by_group(df, 'div')

elif agg_group_by == 'Conference':
    plot_capacity_by_group(df, 'conference')

elif agg_group_by == 'State':
    plot_capacity_by_group(df, 'state')

#Pivot Table header
st.subheader("Pivot Table for all teams")

# Building a pivot table, adopted - (https://blog.streamlit.io/building-a-pivottable-report-with-streamlit-and-ag-grid/)
shouldDisplayPivoted = st.checkbox("Pivot data on Conference")

gb = GridOptionsBuilder()

gb.configure_default_column(
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
)
gb.configure_column(
    field="state",
    header_name="State",
    width=80,
    rowGroup=shouldDisplayPivoted
)

gb.configure_column(
    field="team",
    header_name="Team",
    width=100,
    tooltipField="team",
    rowGroup=True if shouldDisplayPivoted else False,
)

gb.configure_column(
    field="conference",
    header_name="Conference",
    width=110,
    rowGroup=shouldDisplayPivoted,
)

gb.configure_column(
    field="capacity",
    header_name="Capacity",
    width=100,
    type=["numericColumn"],
    aggFunc="sum",
    valueFormatter="value.toLocaleString()",
)

gb.configure_column(
    field="built",
    header_name="Built",
    width=80,
    type=["numericColumn"],
)

gb.configure_column(
    field="expanded",
    header_name="Expanded",
    width=80,
    type=["numericColumn"],
)

gb.configure_column(
    field="div",
    header_name="Division",
    width=80,
)

gb.configure_column(
    field="latitude",
    header_name="Latitude",
    width=100,
    type=["numericColumn"],
)

gb.configure_column(
    field="longitude",
    header_name="Longitude",
    width=100,
    type=["numericColumn"],
)

gb.configure_grid_options(
    tooltipShowDelay=0,
    pivotMode=shouldDisplayPivoted,
)

gb.configure_grid_options(
    autoGroupColumnDef=dict(
        minWidth=300,
        pinned="left",
        cellRendererParams=dict(suppressCount=True)
    )
)
go = gb.build()

AgGrid(df, gridOptions=go, height=400)

# Visualization for year built vs. capacity (https://docs.streamlit.io/library/api-reference/charts/st.plotly_chart)
st.subheader("Capacity vs. Year Built Scatterplot")
fig = px.scatter(
    df,
    x="built",
    y="capacity",
    color="div",
    hover_name="stadium"
)

tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
with tab1:
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with tab2:
    st.plotly_chart(fig, theme=None, use_container_width=True)

# Creating pie chart for top 10 state capacities - (https://plotly.com/python/pie-charts/)
st.subheader('Top 10 Capacities by conference')

# Calculate total capacity by state
conference_capacity = df.groupby('conference')['capacity'].sum().reset_index()

# Sort states by capacity in descending order and get top 5
top_conferences = conference_capacity.sort_values(by='capacity', ascending=False).head(10)

# Create pie chart
fig = px.pie(top_conferences, values='capacity', names='conference',
             title='Conferences with Highest Aggregate Capacity',
             hover_data=['conference'])

fig.update_traces(textposition='inside', textinfo='percent+label')

# Display chart in Streamlit app
st.plotly_chart(fig)

# Query Questions:
st.subheader('What are the five largest stadiums?')
# Get the 5 largest stadiums
largest_stadiums = df.nlargest(5, "capacity")

# Display the result
st.write("The 5 largest stadiums are:")
st.write(largest_stadiums)

st.subheader('What states have the largest aggregate capacity?')

# Group the DataFrame by state and sum the capacity
state_capacity = df.groupby("state")["capacity"].sum().sort_values(ascending=False)

# Get the top 5 states by total capacity
top_states = state_capacity.head(5)
st.write('The states with the largest aggregate capacity:')
st.write(top_states)
