import dash
from dash import dcc, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

ANTIGEN_LIST = ['P100', 'P41', 'OspC', 'DbpA', 'BmpA',
                'DbpB', 'P45', 'P58', 'P66', 'VlsE', 'ErpL', 'OspD']
WIDTH = '49px'

# create the app
app = dash.Dash(__name__)
# ------------------------------------------


# --------------------------------------------------
# app layout
app.layout = html.Div([
    html.H1('Lyme Diagnosis Test Results',
            style={'text-align': 'center'}),

    # dropdown to select specific test
    dcc.Dropdown(id='select_test',
                 options=[
                     {'label': 'TTT', 'value': '2-tier interpretation '},
                     {'label': 'Lab Test', 'value': 'our_diag'},
                     {'label': 'EIA', 'value': 'EIA interpretation'},
                     {'label': 'IgM WB', 'value': 'IgM WB Interpretation'},
                     {'label': 'IgG WB', 'value': 'IgG WB interpretation'}],
                 multi=False,
                 value='our_diag',
                 style={'width': '30%'}
                 ),

    # slider allows user to choose how many antigens must be above threshold
    dcc.Slider(1, 12, 1,
               value=3,
               id='select_num_antigens'
               ),

    # checklist to select which antigens to include
    dcc.Checklist(
        ANTIGEN_LIST,
        ANTIGEN_LIST,
        id='antigens_selected',
        style={'width': '100%'},
        inline=True
    ),
    dcc.Input(2, id="P100", type="number", placeholder="P100",
              debounce=True, style={'width': WIDTH}),
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


    html.Div(id='sensitivity_container', children=[]),
    html.Div(id='specificity_container', children=[]),

    html.Br(),

    dcc.Graph(id="lyme", figure={})
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

    thresh_dict = {'P100': P100, 'P41': P41, 'OspC': OspC, 'DbpA': DbpA,
                   'BmpA': BmpA, 'DbpB': DbpB, 'P45': P45, 'P58': P58,
                   'P66': P66, 'VlsE': VlsE, 'ErpL': ErpL, 'OspD': OspD}

    all_cdc_df = pd.read_csv('cdc_lyme_data.csv', skiprows=2)
    lyme_df = pd.read_csv('complete_lyme_data.csv')

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
    df_lab = pd.concat([lyme_df, cdc_df], axis=1, join='inner')

    if test_choice == 'our_diag':
        # if antigen is above defined threshold, set as 1, if not, then 0
        for ant in ant_list:
            df_lab[ant] = (df_lab[ant] > thresh_dict[ant]).astype(int)

        # get the sum of the antigen scores
        df_lab['sum_col'] = df_lab[ant_list].sum(axis=1)

        # from the sum col, determine if pos or neg
        df_lab['our_diag'] = 'Neg'
        df_lab.loc[df_lab['sum_col'] > num_ant, 'our_diag'] = 'Pos'

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
    fig = px.bar(df_lab, x='Test Results', color='Sample Group')

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
    sensitivity = round(sensitivity, 3)
    specificity = round(specificity, 3)

    # create containers for displays
    se_container = "Sensitivity Score: {}%".format(sensitivity*100)
    sp_container = "Specificity Score: {}%".format(specificity*100)

    return fig, se_container, sp_container


if __name__ == '__main__':
    app.run_server(debug=True)
