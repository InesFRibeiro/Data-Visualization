import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import dash


#Load the data

circuits = pd.read_csv(r'./datasets/circuits.csv')
constructor_results = pd.read_csv(r'./datasets/constructor_results.csv')
constructor_standings = pd.read_csv(r'./datasets/constructor_standings.csv')
constructors = pd.read_csv(r'./datasets/constructors.csv')
driver_standings = pd.read_csv(r'./datasets/driver_standings.csv')
drivers = pd.read_csv(r'./datasets/drivers.csv')
lap_times = pd.read_csv(r'./datasets/lap_times.csv')
pit_stops = pd.read_csv(r'./datasets/pit_stops.csv')
qualifying = pd.read_csv(r'./datasets/qualifying.csv')
races = pd.read_csv(r'./datasets/races.csv')
results = pd.read_csv(r'./datasets/results.csv')
seasons = pd.read_csv(r'./datasets/seasons.csv')
sprint_results = pd.read_csv(r'./datasets/sprint_results.csv')
status = pd.read_csv(r'./datasets/status.csv')

#Data

circuits['country'].replace('United States', 'USA', inplace=True)

#Visualizations

#Position of the driver in each lap of a race

#palette = [i for i in sns.color_palette('viridis', 20).as_hex()]


def pos_lap(year, circuit):
    # choosing the race
    race = races.loc[(races['year'] == year) & (races['circuitId'] == circuit)]['raceId'].values[0]

    # dataframe of lap_times for that race
    pos_per_lap = lap_times[lap_times['raceId'] == race]

    driver_ids = np.unique(pos_per_lap['driverId'].values).tolist()  # list of the ids of the drivers in that race
    driver_names = [drivers.loc[drivers['driverId'] == name]['surname'].values[0] for name in
                    driver_ids]  # names of the drivers
    driver_dict = {driver_ids[i]: driver_names[i] for i in range(len(driver_ids))}  # dictionary with ids and names

    data_ppl = [dict(type='scatter',
                     x=pos_per_lap[pos_per_lap['driverId'] == driver]['lap'],
                     y=pos_per_lap[pos_per_lap['driverId'] == driver]['position'],
                     name=name) #line=dict(color=palette.pop(0)))
                for driver, name in driver_dict.items()]

    layout_ppl = dict(title=dict(
        text='Position of the drivers in each lap'
    ),
        xaxis=dict(title='Lap'),
        yaxis=dict(title='Position'))

    fig_ppl = go.Figure(data=data_ppl, layout=layout_ppl)

    return fig_ppl

pos_lap(2021, 21)