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

from assemble import assemble

BASES = ["A", "C", "G", "T"]


def get_unique_locations(df: pd.DataFrame) -> list:
    """Get unique locations with an alternate base"""
    return df["location"].drop_duplicates().dropna().to_list()


def _get_pids(df: pd.DataFrame) -> set:
    return set(df["pid"].drop_duplicates().to_list())


def plot_boxplot(df: pd.DataFrame, y_variable: str, location: int) -> None:
    """
    Creates boxplots of continuous variable 'y' on the y-axis
    for each reference base.
    """
    # subset dataframe to the location
    subset_df = df[df["location"] == location]

    # get the reference base
    reference = set(subset_df["reference"].to_list())

    # there should only be one
    assert (
        len(reference) == 1
    ), f"There is more than one reference base at position f{location}!"
    reference = reference.pop()

    # the subset will only contain individuals with an alternate base
    # to include individuals with the reference base,
    # we need to figure out who those are and add them back in
    all_pids = _get_pids(df)
    subset_pids = _get_pids(subset_df)
    leftover_pids = all_pids.difference(subset_pids)

    # build df of info for pids that have the reference base at this position
    # drop duplicates due to joining of phenotypic + variant data
    data = df[["pid", "age", "gsex", "weight"]].drop_duplicates()
    data = data[data["pid"].isin(leftover_pids)]
    data = data.assign(
        location=[location] * len(data),
        reference=[reference] * len(data),
        alternate=["reference"] * len(data),
    )

    # concatenate to the df with the pids with the reference base to the 
    # originally subset df so that we get one df with all pids
    concat_df = pd.concat([subset_df, data], axis=0).sort_values(by=["pid"])

    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{"type": "table"}, {"type": "xy"}]],
        column_widths=[0.5, 1.5],
        horizontal_spacing=0.05,
    )

    bases = ["reference"] + [x for x in BASES if x != reference]

    stats_df = {"base": [], "p-value": []}

    for x in bases:
        fig.add_trace(
            go.Box(
                y=concat_df[concat_df["alternate"] == x][y_variable],
                name=x,
                boxpoints="outliers",
            ),
            row=1,
            col=2,
        )

        # do a t-test with each base with reference
        if x != "reference":
            pvalue = stats.ttest_ind(
                concat_df[concat_df["alternate"] == "reference"][y_variable],
                concat_df[concat_df["alternate"] == x][y_variable],
            )[1]

            stats_df["base"].append(x)
            stats_df["p-value"].append(round(pvalue, 3))

    fig.update_yaxes(title_text=y_variable, row=1, col=2)
    fig.update_xaxes(title_text="base", row=1, col=2)

    fig.add_trace(
        go.Table(
            header=dict(values=["base", "p-value"]),
            cells=dict(values=[stats_df[k] for k in stats_df.keys()]),
        ),
        row=1,
        col=1,
    )

    fig.update_layout(height=600, margin=dict(l=100, r=20, t=20, b=20))

    return fig


def main():
    options = parse_args()
    assembled_df = assemble(options)

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
    parser.add_argument(
        "--input_stem",
        type=str,
        default=None,
        help="Path/file stem of synthesized data",
        required=True,
    )
    parser.add_argument(
        "--isolate_households",
        type=int,
        default=True,
        help="0 or 1 boolean - enforce only one individual per household ID"
    )
    parser.add_argument(
        "--seed", 
        type=int,
        default=None,
        help="RNG seed"
    )
    parser.add_argument(
        "--write-csv",
        type=int,
        default=True,
        help="0 or 1 boolean - write results to csv"
    )
    options = parser.parse_args()
    assert options.input_stem is not None, "must specify an input path/file stem"
    return options


if __name__ == "__main__":
    main()
