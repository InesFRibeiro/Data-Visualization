import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import seaborn as sns
import plotly.graph_objs as go
import plotly.express as px
import plotly.io as pio
from raceplotly.plots import barplot


# https://htmlcheatsheet.com/css/

##### LOADING THE DATA ##############################################################

path = 'https://raw.githubusercontent.com/josedias97/ds_dv/main/datasets/'
circuits = pd.read_csv(path + 'circuits.csv')
constructor_results = pd.read_csv(path + 'constructor_results.csv')
constructor_standings = pd.read_csv(path + 'constructor_standings.csv')
constructors = pd.read_csv(path + 'constructors.csv')
driver_standings = pd.read_csv(path + 'driver_standings.csv')
drivers = pd.read_csv(path + 'drivers.csv')
lap_times = pd.read_csv(path + 'lap_times.csv')
pit_stops = pd.read_csv(path + 'pit_stops.csv')
qualifying = pd.read_csv(path + 'qualifying.csv')
races = pd.read_csv(path + 'races.csv')
results = pd.read_csv(path + 'results.csv')
seasons = pd.read_csv(path + 'seasons.csv')
sprint_results = pd.read_csv(path + 'sprint_results.csv')
status = pd.read_csv(path + 'status.csv')

##### Correcting some data #############################################################################################
circuits['country'].replace('United States', 'USA', inplace=True)
races.drop(races[races['year']==2022].index, inplace=True)



##### Position of the driver in each lap of a race #####################################################################
palette = [i for i in sns.color_palette('viridis', 20).as_hex()]

years = list(set(np.array(races['year'])))

circuit_id = circuits['circuitId'].values.tolist()
circuit_name = circuits['name'].values.tolist()
dict_circuits = {circuit_id[i] : circuit_name[i] for i in range(len(circuit_id))}


options_year = [{'label':i, 'value':i} for i in years]
options_circuit = [{'label':name, 'value':cid} for cid, name in dict_circuits.items()]


dropdown_year = dcc.Dropdown(
                            id='drop_year',
                            options=options_year,
                            value=2021
                            )

dropdown_circuit = dcc.Dropdown(
                            id='drop_circuit',
                            options=options_circuit,
                            value=21
                            )

##### APP ##############################################################################################################
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1('Position of the driver in each lap of a race'),

    html.Br(),

    html.Label('Choose a year:'),
    dropdown_year,

    html.Br(),

    # html.Label('Choose a circuit:'),
    # dropdown_circuit,

    dcc.Graph(
        id='position_lap'
    )

])


##### CALLBACKS ########################################################################################################

@app.callback(
    Output(component_id='position_lap', component_property='figure'),
    
    [Input(component_id='drop_year', component_property='value')#,
    #Input(component_id='drop_circuit', component_property='value')
    ]
)


##### Position of the driver in each lap of a race #####################################################################

def callback_1(year): #input_value):
    race = races.copy()
    race = race.loc[(race['year']==year) & (race['circuitId']==21)]['raceId'].values[0]

    #dataframe of lap_times for that race
    pos_per_lap = lap_times[lap_times['raceId']==race]  

    driver_ids = np.unique(pos_per_lap['driverId'].values).tolist() #list of the ids of the drivers in that race
    driver_names = [drivers.loc[drivers['driverId']==name]['surname'].values[0] for name in driver_ids] #names of the drivers
    driver_dict = {driver_ids[i]: driver_names[i] for i in range(len(driver_ids))} #dictionary with ids and names


    data_ppl = [dict(type='scatter',
                 x=pos_per_lap[pos_per_lap['driverId']==driver]['lap'],
                 y=pos_per_lap[pos_per_lap['driverId']==driver]['position'],
                 name=name, line=dict(color= palette.pop(0)))
                                for driver, name in driver_dict.items()]
   
    layout_ppl = dict(title=dict(text='Position of the drivers in each lap'),
                      xaxis=dict(title='Lap'),
                      yaxis=dict(title='Position'))


    return go.Figure(data=data_ppl, layout=layout_ppl)


if __name__ == '__main__':
    app.run_server(debug=True) 