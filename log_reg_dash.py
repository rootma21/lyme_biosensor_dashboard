from lib2to3.pgen2.token import PERCENT
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

WIDTH = '105px'
PERCENT = '80%'

# create the app
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.LUX])
# --------------------------------------------------
# app layout
app.layout = html.Div([
    # header 1
    html.H1('Lyme Diagnosis Test Results',
            style={'text-align': 'center', 'margin-top': '20px'}),
    html.Hr(),
    dbc.Row(
        [
            dbc.Col(dcc.Graph(id="lyme"), md=8, style={"width": "65%"}),
        ],
        align="center",
    ),
    html.Div(id='sensitivity_container', children=[],
             style={"margin-left": "15px", 'margin-top': '15px'}),
    html.Div(id='specificity_container', children=[],
             style={"margin-left": "15px"}),

    html.Br(),

])

# --------------------------------------------------
# connect the Plotly graphs with Dash components


@app.callback(
    [Output(component_id='lyme', component_property='figure'),
     Output(component_id='sensitivity_container',
            component_property='children'),
     Output(component_id='specificity_container', component_property='children')],

    [Input(component_id='select_test', component_property='value'),
     ])
def update_graph(test_choice):

    # read csv's into df
    all_cdc_df = pd.read_csv('cdc_lyme_data.csv', skiprows=2)
    lyme_df = pd.read_csv('complete_lyme_data.csv')

    # remove the 0 to match ID's
    lyme_df.ID = lyme_df.ID.str.replace('#0', '#')

    # get the unique ID by combining code prefix and code number
    all_cdc_df['ID'] = all_cdc_df['Code Prefix'] + \
        '#' + all_cdc_df['Code Number'].astype(str)

    # use a copy of the df, with only a few of the columns
    cdc_df = all_cdc_df.filter(['ID',
                                '2-tier interpretation ',
                                'IgG WB interpretation',
                                'EIA interpretation',
                                'IgM WB Interpretation',
                                'Sample Group',
                                'Sample Category'], axis=1)

    # join them together
    df_lab = pd.merge(lyme_df, cdc_df, on='ID')

    # create figure
    fig = px.bar(df_lab, x='Test Results', color='Sample Group')

    results_dict = dict(df_lab['Test Results'].value_counts())
    fn = results_dict.get('False Negative', 0)
    tp = results_dict.get('True Positive', 0)
    tn = results_dict.get('True Negative', 0)
    fp = results_dict.get('False Positive', 0)

    # calculate
    sensitivity = tp/(tp+fn)
    specificity = tn/(tn+fp)

    # rounding
    sensitivity = round((sensitivity*100), 2)
    specificity = round((specificity*100), 2)

    # create containers for displays
    se_container = "Sensitivity Score: {}%".format(sensitivity)
    sp_container = "Specificity Score: {}%".format(specificity)

    return fig, se_container, sp_container


if __name__ == '__main__':
    app.run_server(debug=True)
