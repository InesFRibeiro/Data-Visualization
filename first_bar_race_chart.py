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

##### LOADING THE DATA #######################################################################################

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

##### Correcting some data ###################################################################################
circuits['country'].replace('United States', 'USA', inplace=True)
races.drop(races[races['year']==2022].index, inplace=True)


##### NEW DFS E CENAS ########################################################################################

#palette = [i for i in sns.color_palette('viridis', 20).as_hex()]

team_pos_races = pd.merge(constructor_standings, 
                      races, 
                      on ='raceId', 
                      how ='inner')
team_pos_races.drop(columns=['positionText', 'time', 'url'], inplace=True)
team_pos_races.rename(columns={'name':'Grand Prix'}, inplace=True)

team_pos_races = pd.merge(team_pos_races, 
                      constructors, 
                      on ='constructorId', 
                      how ='inner')
team_pos_races.drop(columns=['url','wins', 'round'], inplace=True)
team_pos_races.rename(columns={'name':'constructor'}, inplace=True)

team_pos_races = pd.merge(team_pos_races, 
                      circuits, 
                      on ='circuitId', 
                      how ='inner')
team_pos_races.rename(columns={'name':'circuit'}, inplace=True)


df = team_pos_races.copy()
df_1 = df[['raceId','constructorId', 'constructor', 'circuitId', 'Grand Prix', 'circuit','position','year']]

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


df_2 = df_1.groupby(['Period','constructor', 'circuit', 'Grand Prix'], as_index=False)['win'].sum()
df_2.rename(columns={'win':'win_period'}, inplace=True)

##### OPTIONS ###############################################################################################

circuits = list(set(np.array(df_2['circuit'])))

# options for the first bar race chart
options_circuit = [{'label':i, 'value':i} for i in circuits]
options_circuit = sorted(options_circuit, key=lambda x: x["label"])


##### DROPDOWN/SLIDERS/ETC ###################################################################################

# dropdown for the first bar race chart
dropdown_circuit = dcc.Dropdown(
                            id='drop_circuit',
                            options=options_circuit#,
                            #value='A1-Ring'
                            )

##### APP ####################################################################################################
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Number of wins of each constructors per era in each circuit'),

    html.Br(),

    html.Label('Choose a circuit:'),
    dropdown_circuit,

    dcc.Graph(
        id='position_lap'
    )

])

##### CALLBACKS ##############################################################################################

@app.callback(
    Output(component_id='position_lap', component_property='figure'),
    
    [
    Input(component_id='drop_circuit', component_property='value')
    ]
)


##### Visualizations #########################################################################################

def callback_1(circuit):#input_value):
    ################ 1st Bar Race Chart ######################################################################
    fig_bar = px.histogram(df_2[df_2['circuit']==circuit], x="constructor", y="win_period", #color="continent",
                         animation_frame="Period", #animation_group="country", 
                         range_y=[0,9],
                         color_discrete_sequence=px.colors.qualitative.T10)
    fig_bar.update_yaxes(showgrid=False),
    fig_bar.update_xaxes(categoryorder='total descending')
    fig_bar.update_traces(hovertemplate=None)
    fig_bar.update_layout(margin=dict(t=70, b=0, l=70, r=40),
                            hovermode="x unified",
                            xaxis_tickangle=360,
                            title=f'Number of wins of each constructors per era in {circuit}',
                            xaxis_title='Constructor ', yaxis_title="#Wins",
                            plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                            title_font=dict(size=25, color='#a5a7ab', family="Lato, sans-serif"),
                            font=dict(color='#8a8d93'),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                              )
    
    return fig_bar

if __name__ == '__main__':
    app.run_server(debug=True) 