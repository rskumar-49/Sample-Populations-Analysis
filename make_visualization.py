from dash import Dash, dcc, html, dash_table, Input, Output
import sqlite3
import pandas as pd
from stat_analysis import *
from data_subset_analysis import *

DB_PATH = "data.db"

def make_table(table_name):
    return dash_table.DataTable(
        id=table_name,
        columns=[],
        data=[],
        page_current=0,
        page_size=15,
        page_action="custom",
        style_table={"height": "350px", "overflowY": "auto", "border": "1px solid #ddd"},
        style_cell={"textAlign": "left", "padding": "6px", "fontSize": "12px", "fontFamily": "Arial"},
        style_header={"fontWeight": "bold", "backgroundColor": "#f2f2f2"}
    )

app = Dash(__name__)

###################################
### Callbacks #####################
###################################

@app.callback(
    Output("graph", "figure"),
    Output("stats", "children"),
    Input("graph-picker", "value")
)
def update_graph(selected):
    fig, confidence = boxplots_histograms_confidences(selected)
    return fig, report_statistical_significance(*confidence)


@app.callback(
    Output("db-table", "data"),
    Output("db-table", "columns"),
    Input("db-table", "page_current"),
    Input("db-table", "page_size"),
)
def load_page(page_current, page_size):
    offset = (page_current or 0) * page_size
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM populations_samplewise LIMIT {page_size} OFFSET {offset}",
        conn
    )
    conn.close()
    columns = [{"name": c, "id": c} for c in df.columns]
    return df.to_dict("records"), columns

@app.callback(
    Output("db-table2", "data"),
    Output("db-table2", "columns"),
    Input("db-table2", "page_current"),
    Input("db-table2", "page_size"),
)
def load_page2(page_current, page_size):
    offset = (page_current or 0) * page_size
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT * FROM miraclib_pbmc_melanoma_day0_samples LIMIT {page_size} OFFSET {offset}",
        conn
    )
    conn.close()
    columns = [{"name": c, "id": c} for c in df.columns]
    return df.to_dict("records"), columns

@app.callback(
    Output("small-table", "data"),
    Output("small-table", "columns"),
    Input("subset-picker", "value")
)
def load_table3(subset_picker):
    df = subset_breakdown(subset_picker)

    cols = [{"name": c, "id": c} for c in df.columns]
    return df.to_dict("records"), cols



app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "padding": "20px",
        "backgroundColor": "#f7f7f7"
    },
    children=[

        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "15px",
                "borderRadius": "10px",
                "marginBottom": "15px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
            },
            children=[
                html.H1("Samples and Responses Dashboard", style={"margin": "0"}),
            ]
        ),

        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "10px",
                "borderRadius": "10px",
                "marginBottom": "15px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
            },
            children=[
                html.H2("Part 2: Inital Analysis"),
                html.H3("Proportions of Samples by Cell Population"),
                make_table("db-table")
            ]
        ),

        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "10px",
                "borderRadius": "10px",
                "marginBottom": "15px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
            },
            children=[
                html.H2("Part 3: Statistical Analysis"),
                dcc.Dropdown(
                    id="graph-picker",
                    options=[
                        {"label": "B Cell", "value": "b_cell"},
                        {"label": "CD8 T-Cell", "value": "cd8_t_cell"},
                        {"label": "CD4 T-Cell", "value": "cd4_t_cell"},
                        {"label": "NK Cell", "value": "nk_cell"},
                        {"label": "Monocyte", "value": "monocyte"},
                    ],
                    placeholder="Select a population"
                ),
                dcc.Graph(
                    id="graph",
                    style={"height": "60vh"}
                ),
            ]
        ),

        html.Ul(
            style={
                "lineHeight": "1.8",
                "fontSize": "14px"
            },
            children=[
                html.Li("Note that with all the histograms of population proportions being roughly normal and of roughly similar variances, we can do t-tests for statistical significance."),
                html.Li(id="stats"),
            ]
        ),


        html.Div(
            style={
                "backgroundColor": "white",
                "padding": "10px",
                "borderRadius": "10px",
                "boxShadow": "0 2px 6px rgba(0,0,0,0.1)"
            },
            children=[
                html.H2("Part 4: Subset Analysis"),
                html.H3("Sample Numbers of PBMC Cells from Melanoma Patients Treated with Miraclib at Baseline"),
                make_table("db-table2"),
                html.H3("Subset Breakdown for PBMC Melanoma Patients Treated with Miraclib at Baseline"),
                dcc.Dropdown(
                    id="subset-picker",
                    options=[
                        {"label": "Project", "value": "sub.project"},
                        {"label": "Response", "value": "samp.response"},
                        {"label": "Sex", "value": "sub.sex"},
                    ],
                    placeholder="Select a characteristic from which to form subsets"
                ),
                dash_table.DataTable(
                    id="small-table",
                    columns=[],
                    data=[]
                )
            ]
        )
    ]
)

if __name__ == "__main__":
    app.run(debug=True)