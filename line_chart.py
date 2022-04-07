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

##### LOADING THE DATA #########################################################################################

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

##### Correcting some data #####################################################################################
circuits['country'].replace('United States', 'USA', inplace=True)
races.drop(races[races['year']==2022].index, inplace=True)


##### NEW DFS E CENAS ##########################################################################################

palette = [i for i in sns.color_palette('hls', 25).as_hex()]

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


lap_times_2 = lap_times.merge(df_1[['raceId', 'circuitId', 'circuit', 'year']], on='raceId')
##### OPTIONS #################################################################################################
years = list(set(np.array(races['year'])))
circuits = list(set(np.array(df_2['circuit'])))

years_circuits = list(set(np.array(lap_times_2['year'])))


##### Choices #################################################################################################
drop_scatter_years = dcc.Dropdown(id = 'scatter_years',
                                multi = False,
                                clearable = True,
                                disabled = False,
                                style = {'display': True},
                                value = 1996,
                                placeholder = 'Select Year',
                                options = [{'label': c, 'value': c}
                                        for c in years_circuits], className = 'dcc_compon')

drop_scatter_circuits = dcc.Dropdown(id = 'scatter_circuits',
                                    multi = False,
                                    clearable = True,
                                    disabled = False,
                                    style = {'display': True},
                                    placeholder = 'Select Circuit',
                                    options = [], className = 'dcc_compon')





##### APP #####################################################################################################
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1('Position of the drivers in each lap '),

    html.Br(),

    html.Div([
        html.Div([
            html.P('Select Year:', className = 'fix_label', style = {'color': 'black'}),
            drop_scatter_years,

            html.P('Select Circuit:', className = 'fix_label', style = {'color': 'black'}),
            drop_scatter_circuits,

        ], className = "create_container three columns"),

        html.Div([
            dcc.Graph(id = 'scatter_plot',
                      config = {'displayModeBar': 'hover'}),

        ], className = "create_container six columns"),

    ], className = "row flex-display"),

], id = "mainContainer", style = {"display": "flex", "flex-direction": "column"})



##### CALLBACKS ###############################################################################################

@app.callback(
    Output('scatter_circuits', 'options'),
    Input('scatter_years', 'value'))
def get_circuit_options(scatter_years):
    df_3 = df_1[df_1['year'] == scatter_years]
    return [{'label': i, 'value': i} for i in sorted(list(set(df_3['circuit'])))]


@app.callback(
    Output('scatter_circuits', 'value'),
    Input('scatter_circuits', 'options'))
def get_circuit_value(scatter_circuits):
    return [k['value'] for k in scatter_circuits][0]



@app.callback(Output('scatter_plot', 'figure'),
              [Input('scatter_years', 'value')],
              [Input('scatter_circuits', 'value')])



##### Visualizations ##########################################################################################

def callback_1(scatter_years, scatter_circuits):
    ############# Scatter (line) plot #########################################################################
    race = races.copy()
    race =  df_1.loc[(df_1['year']==scatter_years) & (df_1['circuit']==scatter_circuits)]['raceId'].values[0]
    
    #dataframe of lap_times for that race
    pos_per_lap = lap_times[lap_times['raceId']==race]  

    driver_ids = np.unique(pos_per_lap['driverId'].values).tolist() #list of the ids of the drivers in that race
    driver_names = [drivers.loc[drivers['driverId']==name]['surname'].values[0] for name in driver_ids] #names of the drivers
    driver_dict = {driver_ids[i]: driver_names[i] for i in range(len(driver_ids))} #dictionary with ids and names


    data_ppl = [dict(type='scatter',
                 x=pos_per_lap[pos_per_lap['driverId']==driver]['lap'],
                 y=pos_per_lap[pos_per_lap['driverId']==driver]['position'],
                 name=name)#, line=dict(color= palette.pop(0)))
                                for driver, name in driver_dict.items()]
   
    layout_ppl = dict(title=dict(text='Position of the drivers in each lap of this race'),
                      xaxis=dict(title='Lap'),
                      yaxis=dict(title='Position'),
                      plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                      title_font=dict(size=25, color='#a5a7ab', family="Lato, sans-serif"),
                      font=dict(color='#8a8d93'))

    fig_ppl = go.Figure(data=data_ppl, layout=layout_ppl)
    # fig_ppl.update_layout(#margin=dict(t=70, b=0, l=70, r=40),
    #                     #hovermode="x unified",
    #                     #xaxis_tickangle=360,
    #                     #title=f"Number of wins of each constructor from 1950-2021",
    #                     #xaxis_title='Constructor ', yaxis_title="#Wins",
    #                     plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
    #                     title_font=dict(size=25, color='#a5a7ab', family="Lato, sans-serif"),
    #                     font=dict(color='#8a8d93'),
    #                     #legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    #                       )
    fig_ppl.update_xaxes(showgrid=False)
    fig_ppl.update_yaxes(showgrid=False)

    x_max = pos_per_lap['lap'].max()
    fig_ppl.update_xaxes(range=(1,x_max))

    return fig_ppl

if __name__ == '__main__':
    app.run_server(debug=True) 