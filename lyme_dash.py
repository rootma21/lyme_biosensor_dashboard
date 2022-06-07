import dash
from dash import dcc, html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = dash.Dash(__name__)

# ------------------------------------------
# Import and clean data
# read in the two csv's
all_cdc_df = pd.read_csv('cdc_lyme_data.csv', skiprows=2)
lyme_df = pd.read_csv('lyme_data_1.csv')

# get the unique ID by combining code prefix and code number
all_cdc_df['ID'] = all_cdc_df['Code Prefix'] + \
    '#' + all_cdc_df['Code Number'].astype(str)

# use a copy of the df, with only a few of the columns
cdc_df = all_cdc_df.filter(['ID', '2-tier interpretation ',
                            'IgG WB interpretation',
                            'EIA interpretation',
                            'IgM WB Interpretation',
                            'Sample Group',
                            'Sample Category'], axis=1)

# join them together
df = pd.concat([lyme_df, cdc_df], axis=1, join='inner')

# --------------------------------------------------
# app layout
app.layout = html.Div([
    html.H1('Lyme Diagnosis Test Results',
            style={'text-align': 'center'}),
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

    dcc.Slider(1, 12, 1,
               value=3,
               id='select_num_antigens'
               ),
    dcc.Checklist(
        ['P100', 'P41', 'OspC', 'DbpA', 'BmpA',
         'DbpB', 'P45', 'P58', 'P66', 'VlsE', 'ErpL', 'OspD'],
        ['P100', 'OspC', 'DbpA', 'BmpA',
         'DbpB', 'P45', 'P58', 'P66', 'VlsE', 'ErpL', 'OspD'],
        id='antigens_selected',
        style={'width': '100%'},
        inline=True
    ),
    dcc.Input(2, id="P100", type="number", placeholder="P100",
              debounce=True, style={'width': '45px'}),

    dcc.Input(1, id="P41", type="number", placeholder="P41",
              debounce=True, style={'width': '45px'}),
    dcc.Input(1, id="OspC", type="number", placeholder="OspC",
              debounce=True, style={'width': '45px'}),
    dcc.Input(2.01, id="DbpA", type="number",
              placeholder="DbpA", debounce=True, style={'width': '50px'}),
    dcc.Input(2.432, id="BmpA", type="number",
              placeholder="BmpA", debounce=True, style={'width': '50px'}),

    html.Div(id='output_container', children=[]),

    html.Br(),
    dcc.Graph(id="lyme", figure={})
])

# --------------------------------------------------
# connect the Plotly graphs with Dash components


@ app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='lyme', component_property='figure')],
    [Input(component_id='select_test', component_property='value'),
     Input(component_id='select_num_antigens', component_property='value'),
     Input(component_id='antigens_selected', component_property='value'),
     Input(component_id='P100', component_property='value'),
     Input(component_id='P41', component_property='value'),
     Input(component_id='OspC', component_property='value'),
     Input(component_id='DbpA', component_property='value'),
     Input(component_id='BmpA', component_property='value'),

     ]
)
def update_graph(test_choice, num_ant, ant_list, p100, p41, ospc, dbpa, bmpa):
    """print('test_choice: ', test_choice)
    print(type(test_choice))
    print('num_ant: ', num_ant)
    print(type(num_ant))
    print('ant_list: ', ant_list)
    print(type(ant_list))
    print('P100 value: ', p100)
    print(type(p100))"""

    # perform test
    if test_choice == 'our_diag':
        all_cdc_df = pd.read_csv('cdc_lyme_data.csv', skiprows=2)
        lyme_df = pd.read_csv('lyme_data_1.csv')

        # some data cleaning
        all_cdc_df.drop(['No.'], axis=1, inplace=True)
        # get the unique ID by combining code prefix and code number
        all_cdc_df['ID'] = all_cdc_df['Code Prefix'] + \
            '#' + all_cdc_df['Code Number'].astype(str)

        # use a copy of the df, with only a few of the columns
        cdc_df = all_cdc_df.filter(['ID', '2-tier interpretation ',
                                    'IgG WB interpretation',
                                   'EIA interpretation',
                                    'IgM WB Interpretation',
                                    'Sample Group',
                                    'Sample Category'], axis=1)
        thresh_dict = {'P100': float(p100), 'P41': p41, 'OspC': ospc, 'DbpA': dbpa,
                       'BmpA': bmpa, 'DbpB': 1.9, 'P45': 4, 'P58': 5.49,
                       'P66': 2.765, 'VlsE': 1.7, 'ErpL': 1.7, 'OspD': 3.172}

        # join them together
        df_lab = pd.concat([lyme_df, cdc_df], axis=1, join='inner')

        # if antigen is above defined threshold, set as 1, if not, then 0
        for ant in ant_list:
            df_lab[ant] = (df_lab[ant] > thresh_dict[ant]).astype(int)

        # get the sum of the antigen scores
        df_lab['sum_col'] = df_lab[ant_list].sum(axis=1)

        # from the sum col, determine if pos or neg
        df_lab[test_choice] = 'Neg'
        df_lab.loc[df_lab['sum_col'] > num_ant, test_choice] = 'Pos'

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

        # get sensitivity
        results_dict = dict(df_lab['Test Results'].value_counts())
        fn = results_dict.get('False Negative', 0)
        tp = results_dict.get('True Positive', 0)
        sensitivity = tp/(tp+fn)
        sensitivity = round(sensitivity, 3)

        container = "Senstivity Score: {}%".format(sensitivity*100)

        fig = px.bar(df_lab, x='Test Results', color='Sample Group')

        return container, fig

    else:

        conditions = [
            (df['Sample Category'] == 'Lyme Disease') & (
                df[test_choice] == 'Pos'),
            (df['Sample Category'] == 'Control') & (
                df[test_choice] == 'Neg'),
            (df['Sample Category'] == 'Lyme Disease') & (
                df[test_choice] == 'Neg'),
            (df['Sample Category'] == 'Control') & (
                df[test_choice] == 'Pos')]

        choices = ['True Positive', 'True Negative',
                   'False Negative', 'False Positive']
        df['Test Results'] = np.select(
            conditions, choices, default='No confirmed diagnosis')

        fig = px.bar(df, x='Test Results', color='Sample Group')

        # get sensitivity
        results_dict = dict(df['Test Results'].value_counts())
        fn = results_dict.get('False Negative', 0)
        tp = results_dict.get('True Positive', 0)
        sensitivity = tp/(tp+fn)
        sensitivity = round(sensitivity, 3)
        container = "Senstivity Score: {}%".format(sensitivity*100)

        return container, fig


if __name__ == '__main__':
    app.run_server(debug=True)
