from lib2to3.pgen2.token import PERCENT
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc

ANTIGEN_LIST = ['P100', 'P41', 'OspC', 'DbpA', 'BmpA',
                'DbpB', 'P45', 'P58', 'P66', 'VlsE', 'ErpL', 'OspD']
WIDTH = '105px'
PERCENT = '80%'

# create the app
app = dash.Dash(__name__, suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.LUX])

app.title = "Lyme Test Results Analysis"
# ------------------------------------------
# create the controls

controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label('Select Test to Display: ', id='t1'),
                dcc.Dropdown(id='select_test',
                             options=[
                                 {'label': 'TTT', 'value': '2-tier interpretation '},
                                 {'label': 'Lab Test', 'value': 'our_diag'},
                                 {'label': 'EIA', 'value': 'EIA interpretation'},
                                 {'label': 'IgM WB', 'value': 'IgM WB Interpretation'},
                                 {'label': 'IgG WB', 'value': 'IgG WB interpretation'}],
                             multi=False,
                             value='our_diag',
                             style={"width": PERCENT}
                             ),
            ]
        ),
        html.Div(
            [
                dbc.Label(
                    'Min # of Antigens to Signal Positive Sample: ', id='t2'),
                dcc.Slider(1, 12, 1,
                           value=3,
                           id='select_num_antigens',
                           ),
            ]
        ),
        html.Div(
            [
                dbc.Label('Choose Antigens to Include in Diagnosis: ', id='t3'),
                dcc.Checklist(
                    ANTIGEN_LIST,
                    ANTIGEN_LIST,
                    id='antigens_selected',
                    style={"width": PERCENT},
                    inline=True)],
        ),
    ],

    body=True,
)

# --------------------------------------------------
# app layout
app.layout = html.Div([
    html.H1('Lyme Diagnosis Test Results',
            style={'text-align': 'center', 'margin-top': '20px'}),
    html.Hr(),
    dbc.Row(
        [
            dbc.Col(controls, md=4, style={"margin-left": "5px"}),
            dbc.Col(dcc.Graph(id="lyme"), md=8, style={"width": "65%"}),
        ],
        align="center",
    ),
    html.H3('ROC Ratio Threshold',
            style={'text-align': 'center'}),
    dbc.Row(
        [
            dbc.Label('P100', id='a1', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('P41', id='a2', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('OspC', id='a3', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('DbpA', id='a4', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('BmpA', id='a5', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('DbpB', id='a6', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('P45', id='a7', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('P58', id='a8', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('P66', id='a9', style={
                      'text-align': 'center', "width": WIDTH}),
            dbc.Label('VlsE', id='a10', style={
                'text-align': 'center', "width": WIDTH}),
            dbc.Label('ErpL', id='a11', style={
                'text-align': 'center', "width": WIDTH}),
            dbc.Label('OspD', id='a12', style={
                'text-align': 'center', "width": WIDTH}),
        ],
        align="center",
    ),
    dbc.Row(
        [
            dcc.Input(2, id="P100", type="number", placeholder="P100",
                      debounce=True, style={'width': WIDTH, "margin-left": "15px"}),
            dcc.Input(1, id="P41", type="number", placeholder="P41",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(1, id="OspC", type="number", placeholder="OspC",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(2.01, id="DbpA", type="number", placeholder="DbpA",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(2.432, id="BmpA", type="number", placeholder="BmpA",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(1.9, id="DbpB", type="number", placeholder="DbpB",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(4, id="P45", type="number", placeholder="P45",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(5.49, id="P58", type="number", placeholder="P58",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(2.765, id="P66", type="number", placeholder="P66",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(1.7, id="VlsE", type="number", placeholder="VlsE",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(1.7, id="ErpL", type="number", placeholder="ErpL",
                      debounce=True, style={'width': WIDTH}),
            dcc.Input(3.172, id="OspD", type="number", placeholder="OspD",
                      debounce=True, style={'width': WIDTH}),
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
     Input(component_id='select_num_antigens', component_property='value'),
     Input(component_id='antigens_selected', component_property='value'),
     Input(component_id='P100', component_property='value'),
     Input(component_id='P41', component_property='value'),
     Input(component_id='OspC', component_property='value'),
     Input(component_id='DbpA', component_property='value'),
     Input(component_id='BmpA', component_property='value'),

     Input(component_id='DbpB', component_property='value'),
     Input(component_id='P45', component_property='value'),
     Input(component_id='P58', component_property='value'),
     Input(component_id='P66', component_property='value'),
     Input(component_id='VlsE', component_property='value'),
     Input(component_id='ErpL', component_property='value'),
     Input(component_id='OspD', component_property='value'),
     ])
def update_graph(test_choice, num_ant, ant_list, P100, P41, OspC, DbpA, BmpA,
                 DbpB, P45, P58, P66, VlsE, ErpL, OspD):
    print(num_ant)

    thresh_dict = {'P100': P100, 'P41': P41, 'OspC': OspC, 'DbpA': DbpA,
                   'BmpA': BmpA, 'DbpB': DbpB, 'P45': P45, 'P58': P58,
                   'P66': P66, 'VlsE': VlsE, 'ErpL': ErpL, 'OspD': OspD}

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

    if test_choice == 'our_diag':
        # if antigen is above defined threshold, set as 1, if not, then 0
        for ant in ant_list:
            print(ant_list)

            df_lab[f'{ant}_bin'] = (
                df_lab[ant] > thresh_dict[ant]).astype(int)

        # create ant_list_bin
        ant_list_bin = [f'{ant}_bin' for ant in ant_list]

        # get the sum of the antigen scores
        df_lab['sum_col'] = df_lab[ant_list_bin].sum(axis=1)

        # from the sum col, determine if pos or neg
        df_lab['our_diag'] = 'Neg'
        df_lab.loc[df_lab['sum_col'] >= num_ant, 'our_diag'] = 'Pos'

    # determine if the sample was correctly predicted
    conditions = [
        (df_lab['Sample Category'] == 'Lyme Disease') & (
            df_lab[test_choice] == 'Pos'),
        (df_lab['Sample Category'] == 'Control') & (
            df_lab[test_choice] == 'Neg'),
        (df_lab['Sample Category'] == 'Lyme Disease') & (
            df_lab[test_choice] == 'Neg'),
        (df_lab['Sample Category'] == 'Control') & (
            df_lab[test_choice] == 'Pos')]
    choices = ['True Positive', 'True Negative',
               'False Negative', 'False Positive']
    df_lab['Test Results'] = np.select(
        conditions, choices, default='No confirmed diagnosis')

    # create figure
    fig = px.bar(df_lab, x='Test Results', hover_data=['true_diag', 'ID', 'P100', 'P41', 'OspC', 'DbpA', 'BmpA', 'DbpB', 'P45',
                                                       'P58', 'P66', 'VlsE', 'ErpL', 'OspD', '2-tier interpretation ',
                                                       'IgG WB interpretation', 'EIA interpretation', 'IgM WB Interpretation',
                                                       'Sample Group', 'Sample Category'],
                 color='Sample Group')

    # get sensitivity and specificity scores
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
