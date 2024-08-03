import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import mysql.connector


# Function to connect to the MySQL database and fetch data
def fetch_data():
    connection_string = 'mysql+mysqlconnector://root:Rupeek%40123@localhost/redbus_p2'
# Create SQLAlchemy engine
    engine = create_engine(connection_string)
    query = 'SELECT  busname,cast(arriving_time as char) as arriving_time, cast(departure_time as char) as departure_time, time_duration, bus_routelink, price, seat_available, bus_type, rating FROM bus_routes'
    df = pd.read_sql(query, engine)
    return df

# Streamlit app
st.title('Scraped redbus Data Visualization')

# Fetch data from the database
data = fetch_data()
# print(data.dtypes)
# print(data)
#data cleaning and transformation
data['busname'] = data['busname'].replace({'\r': '', '\n': ''}, regex=True)
data['bus_routelink'] = data['bus_routelink'].replace({'\r': '', '\n': ''}, regex=True)
data['price'] = pd.to_numeric(data['price'], errors='coerce')
data['departure_time'] = pd.to_datetime(data['departure_time'], format='%H:%M:%S').dt.time
data['arriving_time'] = pd.to_datetime(data['arriving_time'], format='%H:%M:%S').dt.time

selected_bus_routelink = st.selectbox(
    'Select bus_routelink',
    options=list(data['bus_routelink'].unique())
)
selected_bus_type = st.selectbox(
    'Select Bus Type (Optional)',
    options=['All'] + list(data['bus_type'].unique())
)
selected_departure_time = st.slider('Select departure_time', min_value=0, max_value=23, value=0)
selected_arriving_time = st.slider('Select arrival time', min_value=0, max_value=23, value=23)


# Slider for price range
min_price, max_price = st.slider(
    'Select Price Range',
    min_value=float(data['price'].min()),
    max_value=float(data['price'].max()),
    value=(float(data['price'].min()), float(data['price'].max()))
)
data['price'] = data['price'].astype(float)
#filtering data
filtered_data = data.copy()
filtered_data = filtered_data[filtered_data['bus_routelink'] == selected_bus_routelink]
if selected_bus_type != 'All':
        filtered_data = filtered_data[filtered_data['bus_type'] == selected_bus_type]
        
print(" data count: "+selected_bus_routelink +" - "+ selected_bus_type,len(filtered_data))

if len(filtered_data)>0:        
    filtered_data = filtered_data[
                     (filtered_data['price'] >= min_price) & (filtered_data['price'] <= max_price)]
if len(filtered_data)>0:
     filtered_data = filtered_data[
                     filtered_data['arriving_time'].apply(lambda x: x.hour <= selected_arriving_time)]
if len(filtered_data)>0:
    filtered_data = filtered_data[
                     filtered_data['departure_time'].apply(lambda x: x.hour >= selected_departure_time)]

if len(filtered_data)>0:
    st.write('Bus Details', filtered_data)
else:
     st.write('No bus found: '+ selected_bus_routelink +" - "+ selected_bus_type)   

