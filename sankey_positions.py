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

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go


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


##### Correcting some data #####################################################################################
circuits['country'].replace('United States', 'USA', inplace=True)
races.drop(races[races['year']==2022].index, inplace=True)


##### NEW DFS E CENAS ##########################################################################################
results['position'].replace(to_replace='\\N',value='DNF',inplace=True)
#results['grid'].replace(to_replace=0,value='Pit',inplace=True)

results_driver = results.merge(drivers[['driverId','driverRef','forename','surname','code','dob','nationality']],left_on='driverId',right_on='driverId')
results_driver.insert(len(results_driver.columns),'driverName',results_driver['forename']+' '+results_driver['surname'])
results_driver.drop(columns=['forename','surname'],axis=1,inplace=True)


year_drivers = races[['raceId', 'year']].merge(driver_standings[['raceId', 'driverId', ]], on = 'raceId')
year_drivers = year_drivers.merge(drivers[['driverId', 'forename', 'surname']], on='driverId')
# year_drivers['name'] = year_drivers['forename'] + ' ' + year_drivers['surname']

years_list = list(set(np.array(year_drivers['year'])))

year_grid = results.merge(races[['raceId', 'year']], on = 'raceId')



##### Dropdowns, Sliders, Radios, etc ###############################################################################


##### App ###########################################################################################################

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1('Sankey test'),

    html.Br(),

    html.Div([
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
    ]),

    html.Br(),

    dcc.Graph(id="graph")

])


####### Callbacks ##########################################################################################
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
    Output("graph", "figure"), 
    [Input("year_sankey", "value")],
    [Input("pstn", "value")])


####### Visualization ##########################################################################################

def display_sankey(year_sankey,pstn):

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