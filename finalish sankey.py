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
#from raceplotly.plots import barplot
 
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

###################################################################

# year = 2021
# pstn = 1
# drivID = 830

results['position'].replace(to_replace='\\N',value='DNF',inplace=True)
#results['grid'].replace(to_replace=0,value='Pit',inplace=True)
results_driver = results.merge(drivers[['driverId','driverRef','forename','surname','code','dob','nationality']],left_on='driverId',right_on='driverId')
results_driver.insert(len(results_driver.columns),'driverName',results_driver['forename']+' '+results_driver['surname'])
results_driver.drop(columns=['forename','surname'],axis=1,inplace=True)
#results_driver['position']=results_driver['position'].astype(int)

#### Year

# results_year = results_driver[results_driver['raceId']\
#     .apply(lambda x: np.intersect1d(x,\
#          races[races['year']==year]['raceId']).size > 0)]

# results_y = results_year[['driverId',\
#     'driverName','raceId','grid','position','code','dob','nationality']]
# results_y_abr = results_y[['position','grid','driverName']].sort_values(['position','grid','driverName'])
# results_y_abr['driverGrid'] = \
# results_y_abr['driverName'] + ' - ' + results_y_abr['grid'].astype(str)

# results_y_abr.drop(columns=['grid','driverName'],inplace=True)

#making weights

# d_g_list = []

# curr_d_g = list(results_y_abr.iloc[0,:]) + [1]

# for i in range(1,len(results_y_abr['position'])):
#     if results_y_abr['position'].iloc[i] == results_y_abr['position'].iloc[i-1]:
#         if results_y_abr['driverGrid'].iloc[i] == results_y_abr['driverGrid'].iloc[i-1]:
#             curr_d_g[2] += 1
#         else:
#             d_g_list.append(curr_d_g)
#             curr_d_g = list(results_y_abr.iloc[i,:]) + [1]
#     else:
#         d_g_list.append(curr_d_g)
#         curr_d_g = list(results_y_abr.iloc[i,:]) + [1]

# d_g_list.append(curr_d_g)

# d_g_frame = pd.DataFrame(d_g_list,columns=['position','name','weight'])\
#     .sort_values(['position','weight'],ascending=[True,False])

# labels_d_g_line = list(d_g_frame['name'])+list(d_g_frame['position'])
# labels_d_g_uni_line = list(dict.fromkeys(labels_d_g_line))
# labels_d_g_final = [labels_d_g_uni_line.index(x) for x in labels_d_g_line]
# weights_d_g_final = list(d_g_frame['weight'])    


######################################################
######################################################

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
#import json, urllib

##### NEW DFS E CENAS ##########################################################################################
year_drivers = races[['raceId', 'year']].merge(driver_standings[['raceId', 'driverId', ]], on = 'raceId')
year_drivers = year_drivers.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
year_drivers = year_drivers.merge(results[['raceId', 'driverId','grid']], on=['raceId','driverId'])
year_drivers.insert(len(year_drivers.columns),'driverName',year_drivers['forename']+' '+year_drivers['surname'])
year_drivers.drop(columns=['forename','surname'],axis=1,inplace=True)

years_list = list(set(np.array(year_drivers['year'])))
year_grid = results.merge(races[['raceId', 'year']], on = 'raceId')

##### App ###########################################################################################################

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1('Placings per year'),

    html.Br(),

    dcc.Tabs([
        dcc.Tab(label = "Per driver",\
            children=[
            html.Div([
                html.P('Select Year:', className = 'fix_label', style = {'color': 'black'}),
                dcc.Dropdown(id = 'year',
                                    multi = False,
                                    clearable = True,
                                    disabled = False,
                                    style = {'display': True},
                                    value = 2021,
                                    placeholder = 'Select Year',
                                    options = [{'label': c, 'value': c}
                                                for c in years_list], className = 'dcc_compon'),

                html.P('Select Driver:', className = 'fix_label', style = {'color': 'black'}),
                dcc.Dropdown(id = 'drivName',
                                multi = False,
                                clearable = True,
                                disabled = False,
                                style = {'display': True},
                                placeholder = 'Select Driver',
                                options = [], className = 'dcc_compon'),

            ]), 
            html.Br(),

            dcc.Graph(id="graph1",figure={})
        ]),
        dcc.Tab(label = "Per starting position",\
            children=[
            html.Div([
                html.P('Select Year:', className = 'fix_label', style = {'color': 'black'}),
                dcc.Dropdown(id = 'year_sankey',
                                multi = False,
                                clearable = True,
                                disabled = False,
                                style = {'display': True},
                                value = 2021,
                                placeholder = 'Select Year',
                                options = [{'label': c, 'value': c}
                                            for c in years_list], className = 'dcc_compon'),

                html.P('Select Starting Position:', className = 'fix_label', style = {'color': 'black'}),
                dcc.RadioItems(id = 'pstn',
                                value = 1,
                                options = [])
            ]), 
            html.Br(),

            dcc.Graph(id="graph2")
        ]),

    ])
])


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

        fig.update_layout(title_text="Starting positions and placings of driver "\
        + drivName + " in "+str(year), font_size=10)
        return fig

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
    
    fig.update_layout(title_text = f'Placings in {str(year_sankey)} starting at {str(pstn_print)}', font_size=10)

    return fig



if __name__ == "__main__":
    app.run_server(debug=True)