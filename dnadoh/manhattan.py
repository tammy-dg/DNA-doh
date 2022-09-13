"""Create a manhattan-type plot where it's p-value vs. position
"""

import argparse
from weakref import ref

import pandas as pd
import numpy as np

# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
import plotly.express as px

from dash import Dash, dcc, html, Input, Output
from scipy import stats

from assemble import assemble
from dnadoh_plot.plot_util import plot_manhattan


def main():
    """Generates a manhattan plot using plotly express and dash
    """
    options = parse_args()
    assembled_df = assemble(options)
    _, fig = plot_manhattan(assembled_df)

    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.H1("Manhattan Plot"),
            html.Div([
                dcc.Dropdown(
                    ['weight'],  # Add more phenotypes
                    'weight',
                    id='phenotype'
                ),
            ]),
            dcc.Graph(
                id='manhattan'
            ),
        ]
    )

    @app.callback(Output("manhattan", "figure"), Input("phenotype", "value"))
    def update_graph(phenotype):
        _, fig = plot_manhattan(df=assembled_df, pheno_col=phenotype)
        return fig

    app.run_server(debug=True)


def parse_args():
    """Parsing arguments
    """
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

# TESTING
# df = assemble("/Users/helenzhu/Documents/DNA-doh/temp/temp")
