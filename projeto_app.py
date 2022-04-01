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


##### NEW DFS E CENAS ################################################################################################
##### Position of the driver in each lap of a race #####################################################################


#palette = [i for i in sns.color_palette('viridis', 20).as_hex()]

years = list(set(np.array(races['year'])))

circuit_id = circuits['circuitId'].values.tolist()
circuit_name = circuits['name'].values.tolist()
dict_circuits = {circuit_id[i] : circuit_name[i] for i in range(len(circuit_id))}

grandprix_id = races['circuitId'].values.tolist()
grandprix_name = races['name'].values.tolist()
dict_grandprix = {grandprix_id[i] : grandprix_name[i] for i in range(len(circuit_id))}

options_year = [{'label':i, 'value':i} for i in years]
options_year = sorted(options_year, key=lambda x: x["label"])

options_circuit = [{'label':name, 'value':cid} for cid, name in dict_circuits.items()]
options_circuit = sorted(options_circuit, key=lambda x: x["label"])

options_grandprix = [{'label':name, 'value':cid} for cid, name in dict_grandprix.items()]
options_grandprix = sorted(options_grandprix, key=lambda x: x["label"])


team_pos_races = pd.merge(constructor_standings, 
                      races, 
                      on ='raceId', 
                      how ='inner')
team_pos_races.drop(columns=['positionText', 'time', 'url'], inplace=True)
team_pos_races.rename(columns={'name':'circuit'}, inplace=True)

team_pos_races = pd.merge(team_pos_races, 
                      constructors, 
                      on ='constructorId', 
                      how ='inner')
team_pos_races.drop(columns=['url','wins', 'round'], inplace=True)
team_pos_races.rename(columns={'name':'constructor'}, inplace=True)


df = team_pos_races.copy()
df.rename(columns={'circuit':'Grand Prix'}, inplace=True)
df_1 = df[['constructorId', 'constructor', 'circuitId', 'Grand Prix', 'position','year']]

df_1['61-65'] = np.where((df_1['year']>=1961)&(df_1['year']<=1965), 1, 0)
df_1['66-86'] = np.where((df_1['year']>=1966)&(df_1['year']<=1986), 1, 0)
df_1['87-88'] = np.where((df_1['year']>=1987)&(df_1['year']<=1988), 1, 0)
df_1['89-94'] = np.where((df_1['year']>=1989)&(df_1['year']<=1994), 1, 0)
df_1['95-05'] = np.where((df_1['year']>=1995)&(df_1['year']<=2005), 1, 0)
df_1['06-13'] = np.where((df_1['year']>=2006)&(df_1['year']<=2013), 1, 0)
df_1['14-21'] = np.where((df_1['year']>=2014)&(df_1['year']<=2021), 1, 0)

df_1['Period'] = 0
df_1['Period'] = np.where(df_1['61-65']==1,'1961-1965', df_1['Period'])
df_1['Period'] = np.where(df_1['66-86']==1,'1966-1986', df_1['Period'])
df_1['Period'] = np.where(df_1['87-88']==1,'1966-1986', df_1['Period'])
df_1['Period'] = np.where(df_1['89-94']==1,'1989-1994', df_1['Period'])
df_1['Period'] = np.where(df_1['95-05']==1,'1995-2005', df_1['Period'])
df_1['Period'] = np.where(df_1['06-13']==1,'2006-2013', df_1['Period'])
df_1['Period'] = np.where(df_1['14-21']==1,'2014-2021', df_1['Period'])

df_1.drop(df_1[df_1['Period']=='0'].index, inplace=True)   #observações de 1958-1960
df_1.drop(columns=['61-65','66-86','87-88', '89-94', '95-05', '06-13', '14-21'], inplace=True)

df_1['win'] = np.where(df_1['position']==1, 1, 0)
df_1.drop(columns=['position'], inplace=True)

df_2 = df_1.groupby(['constructorId', 'constructor', 'circuitId', 'Grand Prix','Period', ], as_index=False)['win'].sum()

#circuito = df_2.loc[df_2['circuitId']==6]['Grand Prix'].values[0]


##### OPTIONS ################################################################################################
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

dropdown_grandprix = dcc.Dropdown(
                            id='drop_grandprix',
                            options=options_grandprix,
                            value=1
                            )

##### APP ##############################################################################################################
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1('Position of the driver in each lap of a race'),

    html.Br(),

    # html.Label('Choose a year:'),
    # dropdown_year,

    #html.Br(),
    html.Label('Choose a Grand Prix:'),
    dropdown_grandprix,
    
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
    
    [Input(component_id='drop_grandprix', component_property='value')#,
    #Input(component_id='drop_circuit', component_property='value')
    ]
)


##### Position of the driver in each lap of a race #####################################################################

def callback_1(circuit):#year #input_value):
    fig_bar = px.histogram(df_2[df_2['circuitId']==circuit], x="constructor", y="win", 
                         animation_frame="Period", 
                         range_y=[0,9],
                         color_discrete_sequence=px.colors.qualitative.T10)
    fig_bar.update_yaxes(showgrid=False),
    fig_bar.update_xaxes(categoryorder='total descending')
    fig_bar.update_traces(hovertemplate=None)
    fig_bar.update_layout(margin=dict(t=70, b=0, l=70, r=40),
                            hovermode="x unified",
                            xaxis_tickangle=360,
                            title=f"Number of wins of each constructors per season in {circuit}",
                            xaxis_title='Constructor ', yaxis_title="#Wins",
                            plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                            title_font=dict(size=25, color='#a5a7ab', family="Lato, sans-serif"),
                            font=dict(color='#8a8d93'),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                              )
    
    return fig_bar















    # race = races.copy()
    # race = race.loc[(race['year']==year) & (race['circuitId']==21)]['raceId'].values[0]

    # #dataframe of lap_times for that race
    # pos_per_lap = lap_times[lap_times['raceId']==race]  

    # driver_ids = np.unique(pos_per_lap['driverId'].values).tolist() #list of the ids of the drivers in that race
    # driver_names = [drivers.loc[drivers['driverId']==name]['surname'].values[0] for name in driver_ids] #names of the drivers
    # driver_dict = {driver_ids[i]: driver_names[i] for i in range(len(driver_ids))} #dictionary with ids and names


    # data_ppl = [dict(type='scatter',
    #              x=pos_per_lap[pos_per_lap['driverId']==driver]['lap'],
    #              y=pos_per_lap[pos_per_lap['driverId']==driver]['position'],
    #              name=name)#, line=dict(color= palette.pop(0)))
    #                             for driver, name in driver_dict.items()]
   
    # layout_ppl = dict(title=dict(text='Position of the drivers in each lap'),
    #                   xaxis=dict(title='Lap'),
    #                   yaxis=dict(title='Position'))


    # return go.Figure(data=data_ppl, layout=layout_ppl)


if __name__ == '__main__':
    app.run_server(debug=True) 