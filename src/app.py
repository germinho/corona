import datetime
import os
import yaml

import numpy as np
import pandas as pd
from scipy.integrate import ode, solve_ivp
from scipy.optimize import minimize

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output


import plotly.graph_objs as go

# Lecture du fichier d'environnement
ENV_FILE = '../env.yaml'
with open(ENV_FILE) as f:
    params = yaml.load(f, Loader=yaml.FullLoader)

# Initialisation des chemins vers les fichiers
ROOT_DIR = os.path.dirname(os.path.abspath(ENV_FILE))
WORDPOP_FILE = os.path.join(ROOT_DIR,
                         params['directories']['processed'],
                         params['files']['word_pop'])
DATA_FILE = os.path.join(ROOT_DIR,
                         params['directories']['processed'],
                         params['files']['all_data'])

# Lecture du fichier de données
epidemie_df = (pd.read_csv(DATA_FILE, parse_dates=['Last Update'])
               .assign(day=lambda _df: _df['Last Update'].dt.date)
               .drop_duplicates(subset=['Country/Region', 'Province/State', 'day'])
               [lambda df: df['day'] <= datetime.date(2020, 4, 2)]
              )
print(epidemie_df['Country/Region'] == 'US')

countries = [{'label': c, 'value': c} for c in sorted(epidemie_df['Country/Region'].unique())]

app = dash.Dash('Corona Virus Explorer',external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    dcc.Interval(id='refresh', interval=200),
    html.H2(['Corona Virus Explorer'], style={'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Div([
                html.H4(
                    "Total: ",
                    id="title_total"
                ),
                html.P(
                    id="Counter",
                ),
            ],
            className="count_container"
            ),
            html.Div([
                # html.P(
                #     "Filter by construction date (or select range in histogram):",
                #     className="control_label",
                #     ),
                # dcc.DatePickerRange(
                #     id = 'datepicker-input',
                #     display_format='DD/MM/YYYY',
                # ),
                dbc.RadioItems(
                    id='radioitems-input',
                    options=[
                            {'label': 'Confirmed', 'value': 'Confirmed'},
                            {'label': 'Deaths', 'value': 'Deaths'},
                            {'label': 'Recovered', 'value': 'Recovered'},
                            {'label': 'Active', 'value': 'Active'}
                        ],
                    value='Confirmed',
                    labelStyle={'display': 'inline-block'}
                ),
                html.P(" "),
                dcc.Dropdown(
                    id="countries",
                    options=countries,
                    multi=True,
                    className="dcc_control",
                    placeholder="Select a country",
                ),
            ],
            className="option_container"
            ),
        ],
        className="side_container four columns",
        ),
        html.Div([
            dcc.Tabs([
                dcc.Tab(label='Time', children=[
                    html.Div([
                        dcc.Graph(id='graph1')
                    ]),   
                ]),
                dcc.Tab(label='Map', children=[
                    dcc.Graph(id='map1'),
                    dcc.Slider(
                        id='map_day',
                        min=0,
                        max=(epidemie_df['day'].max() - epidemie_df['day'].min()).days,
                        value=0,
                        updatemode='drag',
                        tooltip = { 
                            'always_visible': True
                        }
                    ),
                ]),

                #TODO add optimizer and beta/gamma selector: (one lead could be using form)
                #
                # Problems encounter:
                #           - @app.callback() seems to take 3 arg max and won't refresh correctly the graph when beta/gamma changes
                #
                dcc.Tab(label='Model',children=[
           		  dcc.Graph(id='graph2'),
                  html.Div([
                    html.Div([
                        html.P("Enter Beta value: "),
                        dcc.Input(id='Beta',placeholder='1.1e-08',value='',type="number"),
                    ],
                    className='inputControl',
                    ),
                    html.Div([
                        html.P("Enter Gama value: "),
                        dcc.Input(id='Gamma',placeholder='0.05',value='',type="number"),
                    ],
                    className='inputControl',
                    ),
                  ]),
                html.Div([
                    html.Div([
                        dbc.Button('Use Optimizer', id = 'buttonOptimizer')
                    ],
                    className='inputControl'
                    ),
                  ]),
                  html.P("Select the country: "),
          		  dcc.Dropdown(id='countryModel',options=countries,className="dcc_control",value='South Korea')
                ]),
            ]),
        ],
        className="main_container eight columns",
        ),
    ],
    className="MainLayout",
    ),
])


#For the counter
@app.callback(Output("Counter", "children"),    
    [
        Input('countries','value'),
        Input('radioitems-input', 'value'),  
    ]
)
def update_CounterBar(countries,variable):
    graphs_df = []
    number = 0
    if countries != [] and type(countries) is list:
        for e_country in countries:
                graphs_df.append(epidemie_df[epidemie_df['Country/Region'] == e_country]
                    .groupby(['Country/Region', 'day'])
                    .agg({variable: 'sum'})
                    .reset_index()
                )
                print(graphs_df)
                   
    graph_df = epidemie_df.groupby('day').agg({variable: 'sum'}).reset_index()
    if countries != [] and type(countries) is list:
        for graph in graphs_df:
            graph.groupby('day').agg({variable:sum}).tail(1)[variable]
            number=number+int(graph[variable].tail(1))
        
    else:
        number = graph_df[variable]
        number = int(number.tail(1))

    return f"{number:,d}"


#For the title "Total[...]"
@app.callback(Output("title_total", "children"),    
    [
        Input('radioitems-input', 'value'),
    ]
)
def update_statusBar(variable):
    return "Total "+variable




# For the model graph
@app.callback(
    Output('graph2', 'figure'),
    [
        Input('countryModel','value'),
    ]
)
def update_model(variable):
    # print(type(beta) == float and type(gamma) == float)
    # if type(beta) == float and type(gamma) == float:
    #     beta = np.float(beta) 
    #     gamma = np.float(gamma)
    # else:

    #Default Parameters for South Korea
    gamma = 0.05
    beta = 1.1e-08
    
    pop_df = pd.read_csv(os.path.join(WORDPOP_FILE))
    pop_df.columns = ['Country Name', 'Country Code','Pop']
    pop_df=pop_df.drop(columns=['Country Code'])

    def get_country(country):
        return (epidemie_df[epidemie_df['Country/Region'] == country]
                .groupby(['Country/Region', 'day'])
                .agg({'Confirmed': 'sum', 'Deaths': 'sum', 'Recovered': 'sum','Active':'sum'})
                .reset_index()
            )
    pd.DataFrame.get_country = get_country
    country_df = get_country(variable)
    def get_pop(country):
        return int(pop_df.loc[pop_df['Country Name']== country,['Pop']]['Pop'])

    active_cases = country_df['Active']
    total_population = get_pop(variable)
    nb_steps = len(active_cases)
    def SIR(t,y):
        S = y[0]
        I = y[1]
        R = y[2]
        return([-beta*S*I, beta*S*I-gamma*I, gamma*I])
    sol = solve_ivp(SIR,[0,nb_steps-1],[total_population,1,0],t_eval=np.arange(0, nb_steps, 1))
    traces1 = go.Scatter(
        x=sol.t,
        y=sol.y[0],
        name='Susceptible'
    )
    traces2= go.Scatter (
        x=np.arange(0,len(country_df)),
        y=country_df['Active'],
        yaxis='y2',
        mode= 'lines+markers',
        marker_color = 'rgb(0, 0, 0)',
        name='True Active'
    )
    traces3 = go.Scatter(
        x=sol.t,
        y=sol.y[1],
        marker_color = 'rgb(200, 0, 0)',
        name='Infected'
    )
    traces4 = go.Scatter(
        x=sol.t,
        y=sol.y[2],
        marker_color = 'rgb(0, 139, 0)',
        name='Recovered'
    )

    figure = {
            'data': [
                traces1, traces4,traces3,traces2
            ],
            'layout': go.Layout(
                title=variable +' Modeling',
                legend = dict(
                    x = 1.1,
                    bordercolor = 'black',
                    borderwidth = 0.1
                ),
                yaxis=dict(
                    title='Population'
                ),
                yaxis2=dict(
                    title='True Active',
                    titlefont=dict(
                        color='rgb(0, 0, 0)'
                    ),
                    tickfont=dict(
                        color='rgb(0, 0, 0)'
                    ),
                    overlaying='y',
                    side='right'
                )
            )
        }
    return figure

# For the time Graph 
@app.callback(
    Output('graph1', 'figure'),
    [
        Input('countries','value'),
        Input('radioitems-input', 'value'),        
    ]
)
def update_graph(countries, variable):
    graphs_df = []
    if countries != [] and type(countries) is list:
        for e_country in countries:
                graphs_df.append(epidemie_df[epidemie_df['Country/Region'] == e_country]
                    .groupby(['Country/Region', 'day'])
                    .agg({variable: 'sum'})
                    .reset_index()
                )
                print(graphs_df)
                   
    graph_df = epidemie_df.groupby('day').agg({variable: 'sum'}).reset_index()
    traces = []
    count = 0
    if countries != [] and type(countries) is list:
        for graph in graphs_df:
            graph.groupby('day').agg({variable:sum}).tail(1)[variable]
            traces.append(dict(
                x=graph['day'],
                y=graph[variable],
                type='line',
                name=countries[count]
            ))
            count = count+1
    else:
        traces.append(dict(
            x=graph_df['day'],
            y=graph_df[variable],
            type='line',
            name='Total'
        ))
    return {
        'data':traces
    }    

#For the world map
@app.callback(
    Output('map1', 'figure'),
    [
        Input('map_day', 'value'),
        Input('radioitems-input', 'value'),
    ]
)
def update_map(map_day,variable):
    day = epidemie_df['day'].unique()[map_day]
    map_df = (epidemie_df[epidemie_df['day'] == day]
              .groupby(['Combined_Key'])
              .agg({variable: 'sum', 'Latitude': 'mean', 'Longitude': 'mean'})
              .reset_index()
             )
    print(epidemie_df['Combined_Key'])
    return {
        'data': [
            dict(
                type='scattergeo',
                lon=map_df['Longitude'],
                lat=map_df['Latitude'],
                text=map_df.apply(lambda r: r['Combined_Key'] + ' (' + str(r[variable]) + ')', axis=1),
                mode='markers',
                marker=dict(
                    size=np.maximum(2.5*np.log(map_df[variable]), 5),
                    color = '#550202fa'
                ),
            )
        ],
        'layout': dict(
            title=str(day),
            titlefont=dict(size=25,color="#ffffff"),
            autosize=True,
            automargin=True,
            margin=dict(l=30, r=30, b=20, t=80),
            hovermode="closest",
            plot_bgcolor="rgba(85, 2, 2, 0.98)",
            paper_bgcolor="rgba(58, 54, 54, 0.301)",
            geo=dict(
                    scope= "world",
                    showland = True,
                    landcolor = "rgb(212, 212, 212)",
                    subunitcolor = "rgba(85, 2, 2, 0.98)",
                    countrycolor = "rgba(58, 54, 54, 0.745)",
                    showlakes = True,
                    lakecolor = "rgb(255, 255, 255)",
                    showsubunits = True,
                    showcountries = True,
                    resolution = 50,
                    # lonaxis = dict(
                    #     showgrid = False,
                    #     gridwidth = 0.5,
                    #     range= [ -140.0, -55.0 ],
                    #     dtick = 5
                    # ),
                    # lataxis = dict (
                    #     showgrid = False,
                    #     gridwidth = 0.5,
                    #     range= [ 20.0, 60.0 ],
                    #     dtick = 5
                    # )
            )
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)