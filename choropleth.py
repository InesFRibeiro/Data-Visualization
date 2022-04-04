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



nr_races = races.groupby('circuitId').count()
nr_races.rename(columns={'raceId':'nr_races'}, inplace = True)
nr_races.reset_index(inplace=True)
country_races = circuits[['circuitId', 'country', 'name', 'lat', 'lng', 'alt']]
country_races = country_races.merge(nr_races[['circuitId', 'nr_races']], on='circuitId')



##### Visualization ####################################################################################################
data_choropleth = dict(type='choropleth',
                    locations=country_races['country'],  #There are three ways to 'merge' your data with the data pre embedded in the map
                    locationmode='country names',
                    z=country_races['nr_races'],
                    text=country_races['country'],
                    colorscale='viridis'
                    )

layout_choropleth = dict(geo=dict(scope='world',  #default
                                projection=dict(type='orthographic'
                                                ),
                                #showland=True,   # default = True
                                landcolor='gray',
                                lakecolor='azure',
                                showocean=True,   # default = False
                                oceancolor='azure'
                                ),
                        
                        title=dict(text='Number of Races per Country',
                                    x=.5 # Title relative position according to the xaxis, range (0,1)
                                )
                        )

fig_choropleth = go.Figure(data=data_choropleth, layout=layout_choropleth)


##### APP ####################################################################################################
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Number of Races per Country'),

    html.Br(),

    dcc.Graph(
        id='position_lap',
        figure=fig_choropleth
    )

])


if __name__ == '__main__':
    app.run_server(debug=True) 