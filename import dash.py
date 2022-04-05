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

results['position'].replace(to_replace='\\N',value=21,inplace=True)
results_driver = results.merge(drivers[['driverId','driverRef','forename','surname','code','dob','nationality']],left_on='driverId',right_on='driverId')
results_driver.insert(len(results_driver.columns),'driverName',results_driver['forename']+' '+results_driver['surname'])
results_driver.drop(columns=['forename','surname'],axis=1,inplace=True)
results_driver['position']=results_driver['position'].astype(int)

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

### Year and position

# results_year_pstn = results_year[results_year['grid']==pstn]
# results_yp = results_year_pstn[['driverId',\
#     'driverName','raceId','grid','position','code','dob','nationality']]
# results_yp_abr = results_yp[['position','driverName']].sort_values(['position','driverName'])

#making weights

# driver_list = []

# curr_driver = list(results_yp_abr.iloc[0,:]) + [1]

# for i in range(1,len(results_yp_abr['position'])):
#     if results_yp_abr['position'].iloc[i] == results_yp_abr['position'].iloc[i-1]:
#         if results_yp_abr['driverName'].iloc[i] == results_yp_abr['driverName'].iloc[i-1]:
#             curr_driver[2] += 1
#         else:
#             driver_list.append(curr_driver)
#             curr_driver = list(results_yp_abr.iloc[i,:]) + [1]
#     else:
#         driver_list.append(curr_driver)
#         curr_driver = list(results_yp_abr.iloc[i,:]) + [1]

# driver_list.append(curr_driver)

# driver_frame = pd.DataFrame(driver_list,columns=['position','name','weight'])\
#     .sort_values(['position','weight'],ascending=[True,False])

# labels_driver_line = list(driver_frame['name'])+list(driver_frame['position'])
# labels_driver_uni_line = list(dict.fromkeys(labels_driver_line))
# labels_driver_final = [labels_driver_uni_line.index(x) for x in labels_driver_line]
# weights_driver_final = list(driver_frame['weight'])

### Year position driver

# results_year_pstn_driver = \
#     results_year_pstn[results_year_pstn['driverId']==drivID]
# results_ypd = results_year_pstn_driver[['driverId',\
#     'driverName','raceId','grid','position','code','dob','nationality']]
# results_ypd_abr = results_ypd[['position','driverName']].sort_values('position')

#making weights

# posit_list = []

# curr_posit = list(results_ypd_abr.iloc[0,:]) + [1]

# for i in range(1,len(results_ypd_abr['position'])):
#     if results_ypd_abr['position'].iloc[i] == results_ypd_abr['position'].iloc[i-1]:
#         curr_posit[2] += 1
#     else:
#         posit_list.append(curr_posit)
#         curr_posit = list(results_ypd_abr.iloc[i,:]) + [1]

# posit_list.append(curr_posit)

# posit_frame = pd.DataFrame(posit_list,columns=['position','name','weight'])\
#     .sort_values(['position','weight'],ascending=[True,False])

# labels_line = list(posit_frame['name'])+list(posit_frame['position'])
# labels_uni_line = list(dict.fromkeys(labels_line))
# labels_final = [labels_uni_line.index(x) for x in labels_line]
# weights_final = list(posit_frame['weight'])

######################################################
######################################################

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import json, urllib

dropdown_year = dcc.Dropdown(
        id='year',
        options=list(set(np.array(races['year']))),
        value=2021
      #  multi=True
    )

slider_pstn = dcc.Slider(
        id='pstn',
        min=0,
        max=results['grid'].max(),
        # marks={str(i): '{}'.format(str(i)) for i in
        #        [1990, 1995, 2000, 2005, 2010, 2014]},
        value=1,
        step=1
    )

dropdown_driver = dcc.Dropdown(
        id='drivID',
        options=list(set(np.array(results_driver['driverName'])))
      #  multi=True
    )

app = Dash(__name__)
server = app.server

app.layout = html.Div([

    html.H1('Sankey test'),

    html.Label('Year Choice'),
    dropdown_year,

    html.Br(),

    html.Label('Position Slider'),
    slider_pstn,

    html.Br(),

    html.Label('Driver Choice'),
    dropdown_driver,

    html.Br(),

    dcc.Graph(id="graph",figure='fig')
    #html.P("Opacity"),
    #dcc.Slider(id='slider', min=0, max=1, 
     #          value=0.5, step=0.1)
])

@app.callback(
    Output("graph", "fig"), 
    [Input("year", "value"),
    Input("pstn", "value"),
    Input("drivID", "value")])
def display_sankey(year,pstn,drivID):

    results_year = results_driver[results_driver['raceId']\
    .apply(lambda x: np.intersect1d(x,\
         races[races['year']==year]['raceId']).size > 0)]      

    results_year_pstn = results_year[results_year['grid']==pstn]

    results_year_pstn_driver = \
    results_year_pstn[results_year_pstn['driverId']==drivID]

    results_y = results_year[['driverId',\
    'driverName','raceId','grid','position','code','dob','nationality']]

    results_y_abr = results_y[['position','grid','driverName']].sort_values(['position','grid','driverName'])
    results_y_abr['driverGrid'] = \
    results_y_abr['driverName'] + ' - ' + results_y_abr['grid'].astype(str)

    results_y_abr.drop(columns=['grid','driverName'],inplace=True) 

    results_yp = results_year_pstn[['driverId',\
        'driverName','raceId','grid','position','code','dob','nationality']]
    results_yp_abr = results_yp[['position','driverName']].sort_values(['position','driverName'])
    
    results_ypd = results_year_pstn_driver[['driverId',\
        'driverName','raceId','grid','position','code','dob','nationality']]
    results_ypd_abr = results_ypd[['position','driverName']].sort_values('position')

    # year weights

    d_g_list = []

    curr_d_g = list(results_y_abr.iloc[0,:]) + [1]

    for i in range(1,len(results_y_abr['position'])):
        if results_y_abr['position'].iloc[i] == results_y_abr['position'].iloc[i-1]:
            if results_y_abr['driverGrid'].iloc[i] == results_y_abr['driverGrid'].iloc[i-1]:
                curr_d_g[2] += 1
            else:
                d_g_list.append(curr_d_g)
                curr_d_g = list(results_y_abr.iloc[i,:]) + [1]
        else:
            d_g_list.append(curr_d_g)
            curr_d_g = list(results_y_abr.iloc[i,:]) + [1]

    d_g_list.append(curr_d_g)

    d_g_frame = pd.DataFrame(d_g_list,columns=['position','name','weight'])\
        .sort_values(['position','weight'],ascending=[True,False])

    labels_d_g_line = list(d_g_frame['name'])+list(d_g_frame['position'])
    labels_d_g_uni_line = list(dict.fromkeys(labels_d_g_line))
    labels_d_g_final = [labels_d_g_uni_line.index(x) for x in labels_d_g_line]
    weights_d_g_final = list(d_g_frame['weight'])    

    # position weights

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

#weightsyear grid driver

    posit_list = []

    curr_posit = list(results_ypd_abr.iloc[0,:]) + [1]

    for i in range(1,len(results_ypd_abr['position'])):
        if results_ypd_abr['position'].iloc[i] == results_ypd_abr['position'].iloc[i-1]:
            curr_posit[2] += 1
        else:
            posit_list.append(curr_posit)
            curr_posit = list(results_ypd_abr.iloc[i,:]) + [1]

    posit_list.append(curr_posit)

    posit_frame = pd.DataFrame(posit_list,columns=['position','name','weight'])\
        .sort_values(['position','weight'],ascending=[True,False])

    labels_line = list(posit_frame['name'])+list(posit_frame['position'])
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

    fig.update_layout(title_text="Placings in "+str(year)+\
    " starting at position "+str(pstn), font_size=10)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)