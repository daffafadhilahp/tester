import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import locale

# Baca data CSV
df = pd.read_csv('covid_19_indonesia_time_series_all.csv')

# Ubah kolom tanggal menjadi format datetime dan kemudian ke format numerik
df['Date'] = pd.to_datetime(df['Date'])
df['Date_numeric'] = df['Date'].apply(lambda x: x.timestamp())

# Buat aplikasi Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Set locale ke bahasa Indonesia
locale.setlocale(locale.LC_ALL, 'id_ID')

# Layout aplikasi
app.layout = dbc.Container(
    fluid=True,
    className="p-5",
    children=[
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Visualisasi Data COVID-19 Indonesia", className="display-4 mb-4"),
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    dbc.CardGroup(
                                        [
                                            dbc.Label("Tanggal yang Dipilih", className="text-muted"),
                                            dcc.DatePickerSingle(
                                                id='date-picker',
                                                min_date_allowed=df['Date'].min(),
                                                max_date_allowed=df['Date'].max(),
                                                initial_visible_month=df['Date'].max(),
                                                date=df['Date'].max(),
                                                className="form-control"
                                            )
                                        ]
                                    ),
                                    html.Hr(className="my-4"),
                                    dbc.CardGroup(
                                        [
                                            dbc.Label("Lokasi yang Dipilih", className="text-muted"),
                                            dcc.Dropdown(
                                                id='location-dropdown',
                                                options=[{'label': location, 'value': location} for location in sorted(df['Location'].unique())],
                                                multi=True,
                                                className="form-select"
                                            )
                                        ]
                                    ),
                                    html.Hr(className="my-4"),
                                    dbc.CardGroup(
                                        [
                                            dbc.Label("Kasus yang Dipilih", className="text-muted"),
                                            dcc.Dropdown(
                                                id='case-dropdown',
                                                options=[
                                                    {'label': 'Kasus Positif', 'value': 'Total Cases'},
                                                    {'label': 'Kasus Sembuh', 'value': 'Total Recovered'},
                                                    {'label': 'Kasus Meninggal', 'value': 'Total Deaths'}
                                                ],
                                                value='Total Cases',
                                                clearable=False,
                                                className="form-select"
                                            )
                                        ]
                                    )
                                ]
                            ),
                            className="shadow-sm p-4"
                        )
                    ],
                    lg=3
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            dbc.CardBody(dcc.Graph(id='covid-line-graph', className="graph")),
                            className="shadow-sm mb-4"
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            dbc.CardBody(dcc.Graph(id='covid-bar-graph', className="graph")),
                                            className="shadow-sm mb-4"
                                        )
                                    ],
                                    md=6
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            dbc.CardBody(dcc.Graph(id='covid-pie-chart', className="graph")),
                                            className="shadow-sm mb-4"
                                        )
                                    ],
                                    md=6
                                )
                            ],
                            className="g-4"
                        )
                    ],
                    lg=9
                )
            ],
            className="g-4"
        )
    ]
)

# Callback untuk grafik garis
@app.callback(
    Output('covid-line-graph', 'figure'),
    Output('covid-line-graph', 'config'),
    Input('date-picker', 'date'),
    Input('location-dropdown', 'value'),
    Input('case-dropdown', 'value')
)
def update_line_graph(selected_date, selected_locations, selected_case):
    if selected_locations is None:
        selected_locations = []
    
    filtered_df = df[df['Location'].isin(selected_locations)]
    filtered_df = filtered_df[filtered_df['Date'] == selected_date]

    fig = go.Figure()
    config = {'displayModeBar': False}

    for location in selected_locations:
        location_df = filtered_df[filtered_df['Location'] == location]
        fig.add_trace(
            go.Scatter(
                x=location_df['Location'],
                y=location_df[selected_case],
                mode='lines+markers',
                name=location,
                text=location_df[selected_case],
                hovertemplate='<b>%{x}</b><br><br>' +
                              'Total Kasus: %{text}',
            )
        )

    fig.update_layout(
        xaxis_title='Lokasi',
        yaxis_title='Jumlah Kasus',
        title=f'Jumlah {selected_case} per Lokasi\nTanggal: {selected_date}',
        template='plotly_dark'
    )

    # Format angka pada sumbu y menjadi bahasa Indonesia
    fig.update_yaxes(tickformat=',.0f')

    return fig, config



# Callback untuk grafik batang
@app.callback(
    Output('covid-bar-graph', 'figure'),
    Input('date-picker', 'date'),
    Input('location-dropdown', 'value'),
    Input('case-dropdown', 'value')
)
def update_bar_graph(selected_date, selected_locations, selected_case):
    if selected_locations is None:
        selected_locations = []
    
    filtered_df = df[df['Location'].isin(selected_locations)]
    filtered_df = filtered_df[filtered_df['Date'] == selected_date]

    fig = go.Figure()

    for location in selected_locations:
        location_df = filtered_df[filtered_df['Location'] == location]
        fig.add_trace(
            go.Bar(
                x=location_df['Location'],
                y=location_df[selected_case],
                name=location,
                text=location_df[selected_case],
                hovertemplate='<b>%{x}</b><br><br>' +
                              'Total Kasus: %{text}',
            )
        )

    fig.update_layout(
        xaxis_title='Lokasi',
        yaxis_title='Jumlah Kasus',
        title=f'Jumlah {selected_case} per Lokasi\nTanggal: {selected_date}',
        template='plotly_dark'
    )

    # Format angka pada sumbu y menjadi bahasa Indonesia
    fig.update_yaxes(tickformat=',.0f')

    return fig

# Callback untuk pie chart
@app.callback(
    Output('covid-pie-chart', 'figure'),
    Output('covid-pie-chart', 'config'),
    Input('date-picker', 'date'),
    Input('location-dropdown', 'value'),
    Input('case-dropdown', 'value')
)
def update_pie_chart(selected_date, selected_locations, selected_case):
    if selected_locations is None:
        selected_locations = []
    
    filtered_df = df[df['Location'].isin(selected_locations)]
    filtered_df = filtered_df[filtered_df['Date'] == selected_date]

    fig = px.pie(
        filtered_df,
        values=selected_case,
        names='Location',
        title=f'Jumlah {selected_case} per Lokasi\nTanggal: {selected_date}',
        template='plotly_dark'
    )
    
    fig.update_traces(
        marker=dict(
            colors=px.colors.qualitative.Set3[:len(selected_locations)]
        )
    )
    
    config = {'displayModeBar': False}
    
    return fig, config

# Jalankan aplikasi
if __name__ == '__main__':
    app.run_server(debug=True)
