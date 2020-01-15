import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import ast

app = dash.Dash(__name__)
server = app.server
# When going on github we should put this line of code###
# server = app.server()

# read data
df = pd.read_csv("data/spotify_month.csv")
df = df.dropna()
# Only keep cases where we have data for multiple months
df["to_delete"] = df["Track URL"] + df["Country"]
df = df[df["to_delete"].duplicated(keep=False)]

# Add map codes
df_countries = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/gapminder_with_codes.csv")
df_countries = df_countries.loc[:, ["country", "iso_alpha"]]
df_countries = df_countries.groupby(["country"]).first()
df = df.merge(df_countries, left_on="Country", right_index=True, how="left")

artist = sorted(df["Artist"].unique())
song = sorted(df["Track Name"].unique())
av_country = sorted(df["Country"].unique())
months_years = sorted(df["month_year"].unique())
# Dictionaries to use for the year range slider
date_codes = {}
codes_marks = {}
month_dict = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct",
              11: "Nov", 12: "Dec"}

for i in range(len(months_years)):
    if months_years[i][5] == "0":  # January to September
        text = month_dict[int(months_years[i][6])]
    else:  # October to December
        text = month_dict[int(months_years[i][-2:])]
    text += ("-" + months_years[i][:4])
    date_codes[i] = months_years[i]
    codes_marks[i] = text

codes_date = {v: k for k, v in date_codes.items()}

# Building the app
app.title = "Spotify - Music Trends"

app.layout = html.Div([
    html.Div([
        html.Div(
            [
                html.A([
                    html.Img(
                        src=app.get_asset_url("spotify-logo.png"),
                        alt="Spotify's logo",
                        id="logo",
                    ),
                ],
                    href="https://www.spotify.com",
                    target="_blank",
                ),
                html.P(
                    "Music Trends",
                    id="app_title"
                ),
            ],
            className="top_left"
        ),
        html.Div([
            html.Div([
                html.P(
                    "Filter by country", className="filter_by"
                ),
                html.Div([
                    dcc.Dropdown(
                        id="country",
                        options=[{"label": i, "value": i} for i in av_country],
                        value="Global")
                ],
                    className="filtering_dropdown"
                ),
                html.P(
                    "Filter by month/year", className="filter_by"
                ),
                html.Div([
                    dcc.RangeSlider(
                        id="date_slider",
                        min=min(date_codes.keys()),
                        max=max(date_codes.keys()),
                        step=None,
                        marks={i: ({"label": codes_marks[i], "style":{"display": "none"}} if i not in [0, 12, 24]
                                   else {"label": codes_marks[i]}) for i in codes_marks},
                        value=[min(date_codes.keys()), max(date_codes.keys())],
                        allowCross=False,
                        pushable=1,
                    ),
                    html.Div(id="output_slider")
                ],
                ),
                html.P(
                    "Filter by artist", className="filter_by"
                ),
                html.Div([
                    dcc.Dropdown(
                        id="artist",
                        options=[{"label": i, "value": i} for i in artist])
                ],
                    className="filtering_dropdown"
                ),
                html.P(
                    "Filter by song", className="filter_by"
                ),
                html.Div([
                    dcc.Dropdown(
                        id="song",
                        options=[{"label": i, "value": i} for i in song]
                    )
                ],
                    className="filtering_dropdown"
                ),

            ]),
        ],
            className="grid_item bottom_left"
        ),

        html.Div([
            html.Div([
                dcc.Loading([
                dcc.Graph(id="indicator-map")],type='circle',color='#1ED760', id="map-loading")
            ],
                className="graph"
            ),
        ],
            className="grid_item right"
        ),

    ],
        className="first_grid"
    ),

    html.Div([
        html.Div([
            dcc.Loading([
            dcc.Graph(id="bar_chart"),
            html.P(
                "Songs", id="ylabel"
            )],type='circle',color='#1ED760', id="map-loading")
        ],
            className="grid_item"
        ),
        html.Div([
            html.Div([
                dcc.Graph(id="line_chart")
            ],
                className="graph"
            ),
        ],
            className="grid_item"
        ),
    ],
        className="second_grid"
    ),

    html.Div([

        html.Div([
            html.P(
                "x", id="close_text"
            ),
        ],
            className="popup_close_button"
        ),
        html.P(
            "No data available for this selection!", id="popup_text"
        ),

    ],
        id="popup_error"
    ),

    html.Footer([
        html.Label(["Data Visualization | Fall Semester 2019 | Abdallah Zaher, M20190684 | "
                    "Cristina Mousinho, M20190303 | Gabriel Santos, M20190925 | Tobias Kutscher, M20190188 | "
                    "Data from: ", html.A("Spotify | Charts",
                                          href="https://spotifycharts.com/regional", target="_blank")])

    ],
        className="footer"
    ),
])


# Setting filters' values, options, marks, (...)


@app.callback(
    Output("artist", "value"),
    [Input("country", "value")])
def clean_values(selected_artist):
    del selected_artist  # Avoids error: "Parameter 'selected_artist' value is not used"
    return None


@app.callback(
    Output("output_slider", "children"),
    [Input("date_slider", "value")])
def update_output(value):
    if value:
        return "From " + codes_marks[value[0]] + " to " + codes_marks[value[1]]


@app.callback(
    Output("date_slider", "marks"),
    [Input("country", "value")])
def set_date_options(selected_country):
    if selected_country:
        return {codes_date[j]: ({"label": codes_marks[codes_date[j]], "style": {"display": "none"}}
                                if codes_date[j] not in [0, 12, 24] else {"label": codes_marks[codes_date[j]]})
                for j in sorted(df[df["Country"] == selected_country]["month_year"].unique())}
    else:
        return {codes_date[j]: ({"label": codes_marks[codes_date[j]], "style": {"display": "none"}})
                for j in sorted(df[df["Country"] == "Global"]["month_year"].unique())}


@app.callback(
    Output("date_slider", "className"),
    [Input("country", "value")])
def set_date_options(selected_country):
    if not selected_country:
        return "no_show"


@app.callback(
    Output("popup_error", "className"),
    [Input("country", "value"),
     Input("date_slider", "value"),
     Input("artist", "value"),
     Input("song", "value"),
     Input("close_text", "n_clicks")])
def toggle_pop_up(selected_country, selected_date, selected_artist, selected_song, close_pop):
    if close_pop:
        return "no_show"

    if selected_date and selected_country and not selected_artist and not selected_song:
        date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
        if df.loc[(df["Country"] == selected_country) & (df["month_year"].isin(date_list))].empty:
            return "show"
    elif selected_date and selected_country and selected_artist and not selected_song:
        date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
        if df.loc[(df["Country"] == selected_country) & (df["Artist"] == selected_artist)
                  & (df["month_year"].isin(date_list))].empty:
            return "show"
    elif selected_date and selected_country and selected_artist and selected_song:
        date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
        if df.loc[(df["Country"] == selected_country) & (df["Artist"] == selected_artist)
                  & (df["Track Name"] == selected_song) & (df["month_year"].isin(date_list))].empty:
            return "show"


@app.callback(
    Output("date_slider", "value"),
    [Input("country", "value")])
def set_date_values(selected_country):
    if not selected_country:
        selected_country = "Global"
    return [codes_date[min(sorted(df[df["Country"] == selected_country]["month_year"].unique()))],
            codes_date[max(sorted(df[df["Country"] == selected_country]["month_year"].unique()))]]


@app.callback(
    Output("artist", "options"),
    [Input("country", "value"),
     Input("date_slider", "value")])
def set_artist_options(selected_country, selected_date):
    if selected_date:
        date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
        return [{"label": j, "value": j} for j in sorted(df[(df["Country"] == selected_country) &
                                                            (df["month_year"].isin(date_list))]["Artist"].unique())]
    else:
        return None


@app.callback(
    Output("song", "options"),
    [Input("country", "value"),
     Input("date_slider", "value"),
     Input("artist", "value")])
def set_song_options(selected_country, selected_date, selected_artist):
    if selected_date:
        date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
        return [{"label": j, "value": j} for j in sorted(df[(df["Country"] == selected_country) &
                                                            (df["Artist"] == selected_artist) &
                                                            (df["month_year"].isin(date_list))]["Track Name"].unique())]
    else:
        return None


@app.callback(
    Output("song", "value"),
    [Input("country", "value"),
     Input("date_slider", "value"),
     Input("artist", "value")])
def set_song_value(selected_country, selected_date, selected_artist):
    if selected_date:
        date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
        if len(df[(df["Country"] == selected_country) &
                  (df["Artist"] == selected_artist) & (df["month_year"].isin(date_list))]["Track Name"].unique()) == 1:
            return df[(df["Country"] == selected_country) &
                      (df["Artist"] == selected_artist) & (df["month_year"].isin(date_list))]["Track Name"].unique()[0]
    else:
        return None

# Making the choropleth map clickable

@app.callback(Output("country", "value"),
              [Input("choropleth_map", "clickData")])
def change(jason):
    import json
    try:
        c = ast.literal_eval(json.dumps(jason))["points"][0]["text"]
    except ValueError:
        c = "Global"
    return c


# Building the plots


@app.callback(Output("line_chart", "figure"),
              [Input("country", "value"), Input("artist", "value"), Input("song", "value"),
               Input("date_slider", "value")])
def update_line_chart(country_filter, artists, songs, year_filter):
    if not country_filter:
        country_filter = "Global"
    if not year_filter:
        year_filter = [min(date_codes.keys()), max(date_codes.keys())]

    date_list = [date_codes[x] for x in range(year_filter[0], year_filter[1] + 1)]
    filtered_df = df[(df["Country"] == country_filter) & (df["month_year"].isin(date_list))]

    if artists is None and songs is None:
        filtered_df = filtered_df.groupby("month_year").agg({"Date": "first", "Streams": "sum"})

    if artists is not None and songs is None:
        filtered_df = filtered_df[filtered_df["Artist"] == artists]
        filtered_df = filtered_df.groupby("month_year").agg({"Date": "first", "Streams": "sum"})

    if artist is not None and songs is not None:
        filtered_df = filtered_df[filtered_df["Artist"] == artists]
        filtered_df = filtered_df[filtered_df["Track Name"] == songs]

    # make sure to sort the values
    filtered_df = filtered_df.sort_values(by=["Date"])

    def title(c, a, s, d):
        if c == "Global":
            c = "the world"
        top = 60
        text_date = "<br> between " + codes_marks[d[0]] + " and " + codes_marks[d[1]]
        if a is None and s is None:
            title_text = "Streams in " + str(c) + text_date
            return title_text, top
        elif a is not None and s is None:
            title_text = "Streams of " + str(a) + " in " + str(c) + text_date
            return title_text, top
        elif a is not None and s is not None and c is not None:
            if len(s) > 70:
                blank_indices = [j for j, x in enumerate(s) if x == " "]
                part_1 = min(blank_indices, key=lambda x: abs(x - len(s) / 3))
                part_2 = min(blank_indices, key=lambda x: abs(x - 2*len(s) / 3))
                s = s[:part_1] + "<br>" + s[part_1 + 1:part_2] + "<br>" + s[part_2 + 1:]
                top = 100
            elif len(s) > 35:
                blank_indices = [j for j, x in enumerate(s) if x == " "]
                middle = min(blank_indices, key=lambda x: abs(x - len(s) / 2))
                s = s[:middle] + "<br>" + s[middle + 1:]
                top = 85
            title_text = "Streams of " + '"' + str(s) + '"' + "<br>" + " by " + str(a) + " in " + str(c) + text_date
            return title_text, top

    data = [go.Scatter(dict(
        y=filtered_df["Streams"],
        x=filtered_df["Date"],
        mode="lines",
        line=dict(color="#1ED760", width=2))
    )]
    layout = dict(title=dict(text=title(country_filter, artists, songs, year_filter)[0], x=.5, y=.95,
                             font={"size": 14}),
                  xaxis=dict(title="Date", gridcolor="LightGrey", showline=True, linewidth=1.1,
                             linecolor="rgb(89, 89, 89)", tickfont=dict(family="Arial", size=12)),
                  yaxis=dict(title="Streams", gridcolor="LightGrey", tickfont=dict(family="Arial", size=12)),
                  margin=dict(l=40, b=40, t=title(country_filter, artists, songs, year_filter)[1], r=40),
                  legend=dict(x=1, y=1),
                  paper_bgcolor="rgb(0,0,0,0)",
                  plot_bgcolor="rgb(0,0,0,0)",
                  height=450,
                  )
    fig = go.Figure(data=data, layout=layout)

    return fig


@app.callback(
    Output("choropleth_map", "figure"),
    [Input("artist", "value"), Input("song", "value"), Input("date_slider", "value")])
def update_choropleth_map(selected_artist, selected_song, selected_date):
    dff = df.copy()
    if not selected_date:
        selected_date = [min(date_codes.keys()), max(date_codes.keys())]

    date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]
    dff = dff[dff["month_year"].isin(date_list)]

    if selected_artist is None and selected_song is None:
        dff = dff.groupby(["iso_alpha", "Country"]).sum().reset_index()

    if selected_artist is not None and selected_song is None:
        dff = dff[dff["Artist"] == selected_artist]
        dff = dff.groupby(["iso_alpha", "Country"]).sum().reset_index()

    if selected_artist is not None and selected_song is not None:
        dff = df[df["Artist"] == selected_artist]
        dff = dff[dff["Track Name"] == selected_song]
        dff = dff.groupby(["iso_alpha", "Country"]).sum().reset_index()

    def title(a, s, d):
        text_date = "<br> between " + codes_marks[d[0]] + " and " + codes_marks[d[1]]
        if a is None and s is None:
            return "Global streams of all songs" + text_date
        if a is not None and s is None:
            return "Global streams of " + str(a) + text_date
        if a is not None and s is not None:
            return "Global streams of" + "<br>" + '"' + str(s) + '"' + "<br>" + " by " + str(a) + text_date[4:]

    trace = go.Choropleth(locations=dff["iso_alpha"], z=dff["Streams"], text=dff["Country"], autocolorscale=False,
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
                          marker={"line": {"color": "white", "width": 0.7}},
                          colorbar={"thickness": 36, "len": 0.8, "outlinewidth": 0,
                                    "title": {"text": "Number of <br> streams", "side": "bottom"}})
    return {"data": [trace],
            "layout": go.Layout(title=dict(text=title(selected_artist, selected_song, selected_date),
                                           font={"size": 14}), height=450, margin=dict(l=0, b=0, t=80, r=100),
                                geo={"showframe": False, "showcoastlines": False,
                                     "projection": {"type": "equirectangular"}})}


@app.callback(Output("bar_chart", "figure"),
              [Input("country", "value"), Input("artist", "value"), Input("song", "value"),
               Input("date_slider", "value")])
def update_bar_chart(selected_country, selected_artist, selected_song, selected_date):
    dff = df.copy()
    if not selected_country:
        selected_country = "Global"
    if not selected_date:
        selected_date = [min(date_codes.keys()), max(date_codes.keys())]

    date_list = [date_codes[x] for x in range(selected_date[0], selected_date[1] + 1)]

    bar_color = "rgb(29, 185, 84)"
    noartist = True
    left = 120
    if selected_artist is None:
        dff = dff[(dff["Country"] == selected_country) & (dff["month_year"].isin(date_list))]
        dff = dff.groupby(["Country", "Artist"])["Streams"].sum().reset_index()

    if selected_artist is not None:
        dff = dff[(dff["Artist"] == selected_artist) & (dff["Country"] == selected_country) &
                  (dff["month_year"].isin(date_list))]
        dff = dff.groupby(["Country", "Artist", "Track Name"])["Streams"].sum().reset_index()
        noartist = False
        if selected_song is not None:
            dff = dff.sort_values(by=["Streams"], ascending=False)
            if dff.shape[0] > 1:
                bar_color = ["rgb(29, 185, 84)"]*(dff.shape[0]-1)
                bar_color.insert(dff["Track Name"].tolist().index(selected_song), "rgb(89, 89, 89)")
            else:
                bar_color = "rgb(89, 89, 89)"

    dff = dff.sort_values(by=["Streams"], ascending=False)

    def title(c, a, d):
        text_date = "<br> between " + codes_marks[d[0]] + " and " + codes_marks[d[1]]
        if a is None and c is not None:
            if c == "Global":
                return "Top 10 artists in the world" + text_date
            elif c[-1] == "s" or c[-1] == "z" or c[-2:] == "ch":
                return str(c) + "'" + " top 10 artists" + text_date
            else:
                return str(c) + "'s" + " top 10 artists" + text_date
        if a is not None and c is not None:
            if a[-1] == "s" or a[-1] == "z" or a[-2:] == "ch":
                a += "'"
            else:
                a += "'s"

            if c[-1] == "s" or c == "United Kingdom" or ("Republic" in c):
                c = "the " + c

            if c == "Global":
                c = "the world"

            return str(a) + " song streams in " + str(c) + text_date

    if noartist:
        lenghts = [len(x) for x in dff["Artist"].head(10)]
        if any([j > 50 for j in lenghts]):
            left = 225
        trace = go.Bar(
            x=dff["Streams"].head(10),
            y=dff["Artist"],
            orientation="h",
            marker=dict(
                color="rgb(29, 185, 84)",
                line=dict(
                    color="rgb(29, 185, 84)",
                    width=10)
            ),
            width=.05
        )
    else:
        lenghts = [len(x) for x in dff["Track Name"]]
        if any([j > 50 for j in lenghts]):
            left = 225
        trace = go.Bar(
            x=dff["Streams"],
            y=dff["Track Name"],
            orientation="h",
            marker=dict(
                color=bar_color,
                line=dict(
                    color=bar_color,
                    width=10)
            ),
            width=.05
        )
    data = [trace]
    layout = dict(title=dict(text=title(selected_country, selected_artist, selected_date), x=.5, font={"size": 14}),
                  xaxis=dict(title="Number of streams", gridcolor="LightGrey", showline=True,
                             linecolor="rgb(89, 89, 89)", tickfont=dict(family="Arial", size=12)),
                  yaxis=dict(gridcolor="LightGrey", tickfont=dict(family="Arial", size=10),
                             autorange="reversed"),
                  margin=dict(l=left, b=40, t=50, r=100),
                  paper_bgcolor="rgb(0,0,0,0)",
                  plot_bgcolor="rgb(0,0,0,0)",
                  )
    fig = go.Figure(data=data, layout=layout)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
