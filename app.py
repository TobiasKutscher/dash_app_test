import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go


app = dash.Dash(__name__)

# read data
df = pd.read_csv('spotify_month.csv')
df = df.dropna()
# only keep cases where we have data for multiple months
df['to_delete'] = df['Track URL'] + df['Country']
df = df[df['to_delete'].duplicated(keep=False)]

colors = {
    'background': '#111111',
    'background2': '#FF0',
    'text': '#7FDBFF'
}

# add map codes
df_countries = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv')
df_countries = df_countries.loc[:, ['country', 'iso_alpha']]
df_countries = df_countries.groupby(['country']).first()
df = df.merge(df_countries, left_on='Country', right_index=True, how='left')


artist = sorted(df['Artist'].unique())

song = sorted(df['Track Name'].unique())


av_country = df['Country'].unique()

app.title = 'Spotify - Music Trends'

app.layout = html.Div([
    html.Div([
        html.Div(
            [
                html.Img(
                    src=app.get_asset_url("spotify-logo.png"),
                    style={
                        "height": "70px",
                        "width": "auto",
                    },
                ),
                html.P(
                    "Music Trends",
                    style={"margin-top": "0px", "color": "white", "font-size": "20px", "margin-left": "60px"}
                ),
            ],
            style={"text-align": "center"},
            className="top_left"
        ),
        html.Div([
            html.Div([
                html.P(
                    "Filter by country", className="filter_by"
                ),
                html.Div([
                    dcc.Dropdown(
                        id='country',
                        options=[{'label': i, 'value': i} for i in av_country],
                        value='Global')
                ],
                    className="filtering_dropdown"
                ),
                html.P(
                    "Filter by artist", className="filter_by"
                ),
                html.Div([
                    dcc.Dropdown(
                        id='artist',
                        options=[{'label': i, 'value': i} for i in artist])
                ],
                    className="filtering_dropdown"
                ),
                html.P(
                    "Filter by song", className="filter_by"
                ),
                html.Div([
                    dcc.Dropdown(
                        id='song',
                        options=[{'label': i, 'value': i} for i in song])
                ],
                    className="filtering_dropdown"
                ),
            ],
                style={"width": "90%", "margin": "auto", "padding": "10px", "text-align": "center"}),
        ],
            className="grid_item bottom_left"
        ),

        html.Div([
            html.Div([
                dcc.Graph(id='indicator-map')
            ],
                style={"width": "95%", "margin": "auto"}
            ),
        ],
            className="grid_item right"
        ),

    ],
        className="first_grid"
    ),

    html.Div([
        html.Div([
            dcc.Graph(id='function_graph')
        ],
            className="grid_item"
        ),
        html.Div([
            html.Div([
                dcc.Graph(id='indicator-graphic')
            ],
                style={"width": "95%", "margin": "auto"}
            ),
        ],
            className="grid_item"
        ),
    ],
        style={"display": "grid", "grid-template-columns": "60% 37.5%", "grid-column-gap": "2.5%", "padding": "1.75%",
               "height": "500px"}
    ),
])


@app.callback(
    Output('artist', 'options'),
    [Input('country', 'value')])
def set_artist_options(selected_country):
    return [{'label': i, 'value': i} for i in sorted(df[df['Country'] == selected_country]['Artist'].unique())]



@app.callback(
    Output('song', 'options'),
    [Input('country', 'value'),
     Input('artist', 'value')])
def set_song_options(selected_country, selected_artist):
    return [{'label': i, 'value': i} for i in sorted(df[(df['Country'] == selected_country) &
                                                        (df['Artist'] == selected_artist)]['Track Name'].unique())]


@app.callback(
    Output('song', 'value'),
    [Input('country', 'value'),
     Input('artist', 'value')])
def set_song_value(selected_country, selected_artist):
    if len(df[(df['Country'] == selected_country) &
              (df['Artist'] == selected_artist)]['Track Name'].unique()) == 1:
        print(df[(df['Country'] == selected_country) &
                 (df['Artist'] == selected_artist)]['Track Name'].unique()[0])
        return df[(df['Country'] == selected_country) &
                  (df['Artist'] == selected_artist)]['Track Name'].unique()[0]




@app.callback(Output('indicator-graphic', 'figure'),
              [Input('country', 'value'), Input('artist', 'value'), Input('song', 'value')])
def update_graph(country_filter, artists, songs):


    filtered_df = df[df['Country'] == country_filter]

    if artists is None and songs is None:
        filtered_df = filtered_df.groupby('month_year').agg({'Date': 'first', 'Streams': 'sum'})

    if artists is not None and songs is None:
        filtered_df = filtered_df[filtered_df['Artist'] == artists]
        filtered_df = filtered_df.groupby('month_year').agg({'Date': 'first', 'Streams': 'sum'})

    if artist is not None and songs is not None:
        filtered_df = filtered_df[filtered_df['Artist'] == artists]
        filtered_df = filtered_df[filtered_df['Track Name'] == songs]


    # make sure to sort the values
    filtered_df = filtered_df.sort_values(by=['Date'])

    data = [go.Scatter(dict(
        y=filtered_df['Streams'],
        x=filtered_df['Date'],
        mode='lines',
        line=dict(color='#1ED760', width=2))
    )]
    layout = dict(title=dict(text='Spotify', x=.5),
                  xaxis=dict(title='Date', gridcolor='LightGrey', showline=True, linewidth=1.1,
                             linecolor='rgb(89, 89, 89)', tickfont=dict(family='Arial', size=12)),
                  yaxis=dict(title='Streams', gridcolor='LightGrey', tickfont=dict(family='Arial', size=12)),
                  margin=dict(l=40, b=40, t=50, r=40),
                  legend=dict(x=1, y=0),
                  paper_bgcolor='rgb(0,0,0,0)',
                  plot_bgcolor='rgb(0,0,0,0)',
                  )
    fig = go.Figure(data=data, layout=layout)

    return fig


@app.callback(
    Output("indicator-map", "figure"),
    [Input('artist', 'value'), Input('song', 'value'), Input('country', 'value')])
def update_figure(selected_artist, selected_song, selected_country):
    dff = df.copy()

    if selected_artist is None and selected_song is None:
        dff = dff.groupby(['iso_alpha', 'Country']).sum().reset_index()

    if selected_artist is not None and selected_song is None:
        dff = dff[dff['Artist'] == selected_artist]
        dff = dff.groupby(['iso_alpha', 'Country']).sum().reset_index()

    if selected_artist is not None and selected_song is not None:
        dff = df[df['Artist'] == selected_artist]
        dff = dff[dff['Track Name'] == selected_song]
        dff = dff.groupby(['iso_alpha', 'Country']).sum().reset_index()

    def title(a, s):
        if a is None and s is None:
            return 'Global streams of all songs'
        if a is not None and s is None:
            return 'Global streams of ' + str(a)
        if a is not None and s is not None:
            return 'Global streams of '+'"'+str(s)+'"'+' by '+str(a)

    trace = go.Choropleth(locations=dff['iso_alpha'], z=dff['Streams'], text=dff['Country'], autocolorscale=False,
                          colorscale=[[0.0, "rgb(211, 248, 224)"],
                                      [0.1111111111111111, "rgb(167, 241, 193)"],
                                      [0.2222222222222222, "rgb(123, 234, 162)"],
                                      [0.3333333333333333, "rgb(79, 227, 131)"],
                                      [0.4444444444444444, "rgb(34, 221, 100)"],
                                      [0.5555555555555556, "rgb(29, 185, 84)"],  # Spotify color
                                      [0.6666666666666666, "rgb(24, 154, 70)"],
                                      [0.7777777777777778, "rgb(17, 110, 50)"],
                                      [0.8888888888888888, "rgb(10, 66, 30)"],
                                      [1.0, "rgb(7, 44, 20)"]],
                          marker={'line': {'color': 'rgb(180,180,180)', 'width': 0.5}},
                          colorbar={"thickness": 10, "len": 0.8, "x": 0.9, "y": 0.5,
                                    'title': {"text": 'Number of streams', "side": "bottom"}})
    return {"data": [trace],
            "layout": go.Layout(title=title(selected_artist, selected_song), height=450,
                                margin=dict(l=10, b=5, t=70, r=10),
                                geo={'showframe': False, 'showcoastlines': False, 'projection': {'type': "miller"}})}

@app.callback(Output('function_graph', 'figure'),
              [Input('country', 'value')], [State('artist', 'value'), State('song', 'value')])
def updatebargraph(selected_country, selected_artist, selected_song):

    if selected_artist is None and selected_song is None:
        dff = pd.DataFrame(df.groupby(['Country', 'Artist'])['Streams'].sum().reset_index())
        dff = dff[dff['Country'] == selected_country]

    if selected_artist is not None and selected_song is None:
        dff = dff[dff['Artist'] == selected_artist]
        dff = dff.groupby(['Country', 'Artist'])['Streams'].sum().reset_index()

    if selected_artist is not None and selected_song is not None:
        dff = df[df['Artist'] == selected_artist]
        dff = dff[dff['Track Name'] == selected_song]
        dff = dff.groupby(['Country', 'Artist'])['Streams'].sum().reset_index()


    dff = dff.sort_values(by=['Streams'], ascending=False)
    trace = go.Bar(
        x=dff['Streams'].head(10),
        y=dff['Artist'],
        orientation='h',
        marker=dict(
            color='rgb(29, 185, 84)',
            line=dict(
                color='rgb(29, 185, 84)',
                width=10)
        ),
        width=.05
    )
    data = [trace]
    layout = dict(title=dict(text='Spotify', x=.5),
                  xaxis=dict(title='Number of streams', gridcolor='LightGrey', showline=True, linewidth=1.1,
                             linecolor='rgb(89, 89, 89)', tickfont=dict(family='Arial', size=12)),
                  yaxis=dict(title='Songs', gridcolor='LightGrey', tickfont=dict(family='Arial', size=12),
                             autorange="reversed", automargin=True),
                  margin=dict(l=40, b=40, t=50, r=40),
                  paper_bgcolor='rgb(0,0,0,0)',
                  plot_bgcolor='rgb(0,0,0,0)',
                  )
    fig = go.Figure(data=data, layout=layout)
    return fig

    #
    # if selected_artist is not None and selected_song is None:
    #     dff = dff[dff['Artist'] == selected_artist]
    #     dff = dff.groupby(['iso_alpha', 'Country']).sum().reset_index()
    #
    # if selected_artist is not None and selected_song is not None:
    #     dff = df[df['Artist'] == selected_artist]
    #     dff = dff[dff['Track Name'] == selected_song]
    #     dff = dff.groupby(['iso_alpha', 'Country']).sum().reset_index()


if __name__ == '__main__':
    app.run_server(debug=True)
