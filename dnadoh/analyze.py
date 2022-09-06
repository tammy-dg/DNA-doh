"""
Creates a dashboard of one plot per genome position 
with boxplots of the measurement of weight per base at that position.
Also performs t-tests of each alternative base to the reference base.
"""

import argparse

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import Dash, dcc, html, Input, Output
from scipy import stats
from dnadoh_plot.plot_util import plot_boxplot

from assemble import assemble

BASES = ["A", "C", "G", "T"]


def get_unique_locations(df: pd.DataFrame) -> list:
    """Get unique locations with an alternate base"""
    return df["location"].drop_duplicates().dropna().to_list()


def _get_pids(df: pd.DataFrame) -> set:
    return set(df["pid"].drop_duplicates().to_list())


def main():
    options = parse_args()
    assembled_df = assemble(options.input_stem)

    locations = get_unique_locations(assembled_df)
    locations = sorted(locations)

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            "Position:",
                            dcc.Dropdown(
                                options=sorted(x for x in assembled_df["location"].dropna().unique()),
                                id="variant-select",
                                value=locations[0],  # arbitrarily show the first position
                            ),
                        ],
                        style={"width": "10%", "margin-left": "100px", "margin-bottom": "0px", "margin-top": "50px", "display": "inline-block"},
                    ),
                    html.Div(
                        [dcc.Graph(id="variant")],
                        style={"width": "75%"}
                    )
                ]
            ),
        ]
    )

    @app.callback(Output("variant", "figure"), Input("variant-select", "value"))
    def update_graph(location):
        fig = plot_boxplot(assembled_df, "weight", location)
        return fig

    app.run_server(debug=True)


def parse_args():
    parser = argparse.ArgumentParser()
    # nothing here for now
    parser.add_argument(
        "--input_stem",
        type=str,
        default=None,
        help="Path/file stem of synthesized data",
        required=True,
    )
    options = parser.parse_args()
    return options


if __name__ == "__main__":
    main()
