from turtle import color, position
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
# from plotly.subplots import make_subplots


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

nr_races = races.groupby('circuitId').count()
nr_races.rename(columns={'raceId':'nr_races'}, inplace = True)
nr_races.reset_index(inplace=True)
country_races = circuits[['circuitId', 'country', 'name', 'lat', 'lng', 'alt']]
country_races = country_races.merge(nr_races[['circuitId', 'nr_races']], on='circuitId')
country_races = country_races.groupby('country').sum()
country_races.reset_index(inplace=True)

df['wins (total)'] = np.where(df['position']==1, 1, 0)
df_3 = df.groupby(['circuit', 'constructor' ], as_index=False)['wins (total)'].sum()
df_3.rename(columns={'circuit':'Circuit', 'constructor':'Constructor'}, inplace=True)

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


results['position'].replace(to_replace='\\N',value='DNF',inplace=True)
results_driver = results.merge(drivers[['driverId','driverRef','forename','surname','code','dob','nationality']],left_on='driverId',right_on='driverId')
results_driver.insert(len(results_driver.columns),'driverName',results_driver['forename']+' '+results_driver['surname'])

year_drivers = races[['raceId', 'year']].merge(driver_standings[['raceId', 'driverId', ]], on = 'raceId')
year_drivers = year_drivers.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
year_drivers = year_drivers.merge(results[['raceId', 'driverId','grid']], on=['raceId','driverId'])
year_drivers.insert(len(year_drivers.columns),'driverName',year_drivers['forename']+' '+year_drivers['surname'])

years_list = list(set(np.array(year_drivers['year'])))
year_grid = results.merge(races[['raceId', 'year']], on = 'raceId')


##### OPTIONS #################################################################################################
years = list(set(np.array(races['year'])))
circuits = list(set(np.array(df_2['circuit'])))

years_circuits = list(set(np.array(lap_times_2['year'])))

##### Choices #################################################################################################
drop_scatter_years = dcc.Dropdown(id = 'scatter_years',
                                multi = False,
                                clearable = True,
                                disabled = False,
                                style = {'display': True, 'width':'40%'},
                                value = 2021,
                                placeholder = 'Select Year',
                                options = [{'label': c, 'value': c}
                                        for c in years_circuits], className = 'dcc_compon')

drop_scatter_circuits = dcc.Dropdown(id = 'scatter_circuits',
                                    multi = False,
                                    clearable = True,
                                    disabled = False,
                                    style = {'display': True, 'width':'60%'},
                                    placeholder = 'Select Circuit',
                                    options = [], className = 'dcc_compon')

##### Visualization 1 ####################################################################################################

def bar_chart():
    fig_bar = px.histogram(df_3, x="Constructor", y="wins (total)",
                    animation_frame="Circuit", 
                    range_y=[0,16],
                    color_discrete_sequence=['red'])
    fig_bar.update_yaxes(showgrid=False),
    fig_bar.update_xaxes(categoryorder='total descending')
    fig_bar.update_layout(margin=dict(t=70, b=0, l=70, r=40),
                            xaxis_tickangle=360,
                            title=f"Number of wins of each constructor from 1950-2021 in each circuit",
                            xaxis_title='Constructor ', yaxis_title="Number of Wins",
                            plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                            title_font=dict(size=25, color='white', family="Lato, sans-serif"),
                            font=dict(color='white'), 
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                            )
    return fig_bar


def choropleth():
    fig = go.Figure(data=go.Choropleth(
        locations=country_races['country'], # Spatial coordinates
        z = country_races['nr_races'],
        locationmode = 'country names', 
        text=country_races['nr_races'],
        colorbar_title = "nr races",
        hoverinfo="location+z",
        colorscale='reds',
        reversescale=False,
        ),
        layout=dict(geo=dict(scope='world',
                            landcolor='white',
                            showocean=True,
                            oceancolor='skyblue'
                            )
        )
    )

    fig.update_layout(
        title_text = 'Number of Races per Country', 
        plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
        title_font=dict(size=25, color='white', family="Lato, sans-serif"),
        font=dict(color='white'), 
        margin=dict(l=5, r=5, t=35, b=20)
        )

    return fig


##### APP #####################################################################################################
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div([
    html.H1('Formula 1 - Trends & Performance', style = {'color': 'white'}),

    html.Br(),

    html.P('The goal of this dashboard is \
        to develop an interactive visualization about Formula 1. \
        The dashboard will give important information to the users \
        about the countries with the most and the least number of races,\
        the number of wins of each constructor from 1950-2021 per circuit,\
        the position in which each driver starts and their final position in \
        each year, as well as the position of each driver in each lap of a race.',
        style = {'color': 'white'}),

    html.Br(),

    html.Div([
        dcc.Graph(id='globe_plot', 
                figure = choropleth()
                )
        ], className = "create_container six columns", style={'width':'100%'}),

    html.Br(),

    html.Div([
        dcc.Graph(id='bar_chart_plot', 
                figure = bar_chart()
                )
    ], className = "create_container six columns", style={'width':'100%'}),
    

    html.Br(),

    html.Div([
        html.Div([
            html.P('Year:', className = 'fix_label', style = {'color': 'white'}),
            drop_scatter_years,

            html.P('Circuit:', className = 'fix_label', style = {'color': 'white'}),
            drop_scatter_circuits
        ], style={'display':'flex', 'width':'95%', 'margin-left': '3.5vw'}),

        dcc.Graph(id = 'scatter_plot',
                    config = {'displayModeBar': 'hover'}) 

    ], className = "create_container six columns", style={'width':'100%'}),

    html.Br(),

    html.Div([
        dcc.Tabs(parent_className='custom-tabs',
            className='custom-tabs-container',
            children=[        
            dcc.Tab(className='custom-tab',
                selected_className='custom-tab--selected',
                label = "Per driver",\
                children=[
                html.Div([
                    html.P('Year:', className = 'fix_label', style = {'color': 'white'}),
                    dcc.Dropdown(id = 'year',
                                        multi = False,
                                        clearable = True,
                                        disabled = False,
                                        style = {'display': True, 'width':'40%'},
                                        value = 2021,
                                        placeholder = 'Select Year',
                                        options = [{'label': c, 'value': c}
                                                    for c in years_list], className = 'dcc_compon'),

                    html.P('Driver:', className = 'fix_label', style = {'color': 'white'}),
                    dcc.Dropdown(id = 'drivName',
                                    multi = False,
                                    clearable = True,
                                    disabled = False,
                                    style = {'display': True, 'width':'60%'},
                                    placeholder = 'Select Driver',
                                    options = [], className = 'dcc_compon'),

                ], style={'display':'flex', 'width':'95%', 'margin-left': '3.5vw'}), 
                html.Br(),

                dcc.Graph(id="graph1",figure={})
            ]),
            dcc.Tab(className='custom-tab',
                selected_className='custom-tab--selected',
                label = "Per starting position",\
                children=[
                html.Div([
                    html.P('Select Year:', className = 'fix_label', style = {'color': 'white'}),
                    dcc.Dropdown(id = 'year_sankey',
                                    multi = False,
                                    clearable = True,
                                    disabled = False,
                                    style = {'display': True},
                                    value = 2021,
                                    placeholder = 'Select Year',
                                    options = [{'label': c, 'value': c}
                                                for c in years_list], className = 'dcc_compon'),

                    html.P('Select Starting Position:', className = 'fix_label', style = {'color': 'white'}),
                    dcc.Dropdown(id = 'pstn',
                                    multi = False,
                                    value = 1,
                                    style = {'display': True},
                                    options = [], className = 'dcc_compon')
                ]), 
                html.Br(),

                dcc.Graph(id="graph2")
            ]),    

        ])
    ], className = "create_container six columns", style={'width':'100%'}),
    
    html.Br(),
    html.Br(),

    html.P('Authors: Inês Ribeiro, m20210595; J. Daniel Conde, José Dias, m20211009; m20210656; Matias Neves, m20211000',
        style = {'color': 'white'}),
    html.Br(),
    html.P('Dataset source: https://www.kaggle.com/rohanrao/formula-1-world-championship-1950-2020?select=results.csv',
        style = {'color': 'white'})
], id = "mainContainer", style = {"display": "flex", "flex-direction": "column"})



##### Line Chart ###############################################################################################

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


def line_chart(scatter_years, scatter_circuits):
    ############# Scatter (line) plot #########################################################################
    race = races.copy()
    race =  df_1.loc[(df_1['year']==scatter_years) & (df_1['circuit']==scatter_circuits)]['raceId'].values[0]
    
    # dataframe of lap_times for that race
    pos_per_lap = lap_times[lap_times['raceId']==race]  

    # df w/ raceId, driverID, lap, position, constructors (& id) and the index of the constructor in this race
    driver_team = pos_per_lap.copy()
    driver_team.drop(columns=['time','milliseconds'], inplace=True)
    driver_team = driver_team.merge(qualifying[['raceId', 'driverId', 'constructorId']], on=['raceId', 'driverId'])
    driver_team = driver_team.merge(constructors[['constructorId', 'name']], on='constructorId')
    driver_team.rename(columns={'name':'constructor'}, inplace=True)
    driver_team['constructor_index'] = 100

    # list w/ the names of the teams that participated in this race
    team_names = np.unique(driver_team['constructor'].values).tolist()
    for i in team_names:
        driver_team['constructor_index'] = np.where(driver_team['constructor']==i, team_names.index(i),driver_team['constructor_index'])

    # list with the ids of the drivers in this race
    driver_ids = np.unique(pos_per_lap['driverId'].values).tolist()
    # list with the names of the drivers in this race
    driver_names = [drivers.loc[drivers['driverId']==drivId]['surname'].values[0] for drivId in driver_ids]

    # list of the constructor of each driver (length == #drivers)
    driv_team = [driver_team.loc[driver_team['driverId']==drivId]['constructor'].values[0] for drivId in driver_ids]
    # list w/ the index of the constructor of each driver in this race
    team_index = [driver_team.loc[driver_team['driverId']==drivId]['constructor_index'].values[0] for drivId in driver_ids]

    # dict w/ ids of the drivers as the keys and a list with drivers names, team index and team name as the values
    driver_dict = {driver_ids[i]: [driver_names[i], driv_team[i], team_index[i]] for i in range(len(driver_ids))} 
    driver_dict = dict(sorted(driver_dict.items(), key=lambda x: [x[1][1], x[1][0]]))

    colors = ['red', 'gold', 'darkorange', 'forestgreen', 'lightgray', 'turquoise', 'dodgerblue','#458B74','#8470FF','#8B6914','#8A3324']
    

    data_ppl = [dict(type='scatter',
                x=pos_per_lap[pos_per_lap['driverId']==driverid]['lap'],
                y=pos_per_lap[pos_per_lap['driverId']==driverid]['position'],
                name = name[0]+ ' - ' + name[1] , line=dict(color= colors[name[2]]))
                            for driverid, name in driver_dict.items()]


    layout_ppl = dict(title=dict(text='Position of the drivers in each lap of this race'),
                      xaxis=dict(title='Lap'),
                      yaxis=dict(title='Position'),
                      plot_bgcolor='#2d3035', paper_bgcolor='#2d3035',
                      title_font=dict(size=25, color='white', family="Lato, sans-serif"),
                      font=dict(color='white'))

    fig_ppl = go.Figure(data=data_ppl, layout=layout_ppl)

    fig_ppl.update_xaxes(showgrid=False)
    fig_ppl.update_yaxes(showgrid=False)

    x_max = pos_per_lap['lap'].max()
    fig_ppl.update_xaxes(range=(1,x_max))

    return fig_ppl


###############################################################################################################
@app.callback(
    Output('drivName', 'options'),
    Input('year', 'value'))
def get_circuit_options(year):
    year_drivers2 = year_drivers[year_drivers['year'] == year]
    return [{'label': i, 'value': i} for i in sorted(list(set(year_drivers2['driverName'])))]


@app.callback(
    Output('drivName', 'value'),
    Input('drivName', 'options'))
def get_driver_value(drivName):
    return [k['value'] for k in drivName][0]


@app.callback(
    Output('pstn', 'options'),
    Input('year_sankey', 'value'))
def get_pstn_options(year_sankey):
    year_grid2 = year_grid[year_grid['year'] == year_sankey]
    return [{'label': i, 'value': i} for i in sorted(list(set(year_grid2['grid'])))]


@app.callback(
    Output('pstn', 'value'),
    Input('pstn', 'options'))
def get_pstn_value(pstn):
    return [k['value'] for k in pstn][0]


@app.callback(
    Output("graph1", "figure"), 
    Input("year", "value"),
    Input("drivName", "value"))

    
def display_sankey(year,drivName):

    results_year = results_driver[results_driver['raceId']\
    .apply(lambda x: np.intersect1d(x,\
         races[races['year']==year]['raceId']).size > 0)]      

    results_year_driver = results_year[results_year['driverName']==drivName]
    if len(results_year_driver) == 0:
        return dash.no_update
    else:
        results_yd = results_year_driver[['driverId',\
        'driverName','raceId','grid','position']]
        results_yd_abr = results_yd[['position','grid']].sort_values(['position','grid'])

        posit_list = []

        curr_posit = list(results_yd_abr.iloc[0,:]) + [1]

        for i in range(1,len(results_yd_abr['position'])):
            if results_yd_abr['position'].iloc[i] == results_yd_abr['position'].iloc[i-1]:
                if results_yd_abr['grid'].iloc[i] == results_yd_abr['grid'].iloc[i-1]:
                    curr_posit[2] += 1
                else:
                    posit_list.append(curr_posit)
                    curr_posit = list(results_yd_abr.iloc[i,:]) + [1]
            else:
                posit_list.append(curr_posit)
                curr_posit = list(results_yd_abr.iloc[i,:]) + [1]

        posit_list.append(curr_posit)


        posit_frame = pd.DataFrame(posit_list,columns=['position','grid','weight'])\
        .sort_values(['position','weight'],ascending=[True,False])

        labels_line = list(posit_frame['grid'])+list(posit_frame['position'])
        labels_uni_line = list(dict.fromkeys(labels_line))
        labels_final = [labels_uni_line.index(x) for x in labels_line]
        weights_final = list(posit_frame['weight'])

   

        fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = labels_uni_line
        ),
        link = dict(
        source = labels_final[:len(labels_final)//2], # indices correspond to labels, eg A1, A2, A1, B1, ...
        target = labels_final[len(labels_final)//2:],
        value = weights_final
        ))])

        fig.update_layout(title_text="Starting positions and placings of "\
        + drivName + " in "+str(year), font=dict(size = 10, color = 'white'),
        plot_bgcolor='#2d3035', paper_bgcolor='#2d3035')
    
        return fig


###############################################################################################################
@app.callback(
    Output("graph2", "figure"), 
    [Input("year_sankey", "value")],
    [Input("pstn", "value")])

def display_sankey_2(year_sankey,pstn):
    results_year = results_driver[results_driver['raceId']\
    .apply(lambda x: np.intersect1d(x,\
         races[races['year']==year_sankey]['raceId']).size > 0)]      

    results_year_pstn = results_year[results_year['grid']==pstn]


    results_yp = results_year_pstn[['driverId',\
        'driverName','raceId','grid','position','code','dob','nationality']]
    results_yp_abr = results_yp[['position','driverName']].sort_values(['position','driverName'])
    


    driver_list = []

    curr_driver = list(results_yp_abr.iloc[0,:]) + [1]

    for i in range(1,len(results_yp_abr['position'])):
        if results_yp_abr['position'].iloc[i] == results_yp_abr['position'].iloc[i-1]:
            if results_yp_abr['driverName'].iloc[i] == results_yp_abr['driverName'].iloc[i-1]:
                curr_driver[2] += 1
            else:
                driver_list.append(curr_driver)
                curr_driver = list(results_yp_abr.iloc[i,:]) + [1]
        else:
            driver_list.append(curr_driver)
            curr_driver = list(results_yp_abr.iloc[i,:]) + [1]

    driver_list.append(curr_driver)

    driver_frame = pd.DataFrame(driver_list,columns=['position','name','weight'])\
        .sort_values(['position','weight'],ascending=[True,False])

    labels_driver_line = list(driver_frame['name'])+list(driver_frame['position'])
    labels_driver_uni_line = list(dict.fromkeys(labels_driver_line))
    labels_driver_final = [labels_driver_uni_line.index(x) for x in labels_driver_line]
    weights_driver_final = list(driver_frame['weight'])


    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = "black", width = 0.5),
        label = labels_driver_uni_line
        ),
        link = dict(
        source = labels_driver_final[:len(labels_driver_final)//2], # indices correspond to labels, eg A1, A2, A1, B1, ...
        target = labels_driver_final[len(labels_driver_final)//2:],
        value = weights_driver_final
    ))])
    if pstn==0:
        pstn_print='the pit lane'
    else:
        pstn_print='position '+str(pstn)
    
    fig.update_layout(title_text = f'Placings in {str(year_sankey)} starting at {str(pstn_print)}',
    font=dict(size = 10, color = 'white'),
        plot_bgcolor='#2d3035', paper_bgcolor='#2d3035')



    return fig



# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

if __name__ == '__main__':
    app.run_server(debug=True) 