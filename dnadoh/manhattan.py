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


def plot_manhattan(df: pd.DataFrame, pheno_col:str = "weight"):
    """Create a manhattanplot
    """

    # Generating stats per position
    all_loc = df[['location', 'reference', 'alternate']].drop_duplicates()

    # Initializing results
    results_df = []
    for _, row in all_loc.iterrows():

        # Subset data
        subset_df = df[df['location'] == row['location']]
        alt_df = subset_df.loc[
            subset_df['alternate'] == row['alternate'],
            ['pid', pheno_col]
        ].drop_duplicates()
        ref_df = df.loc[
            ~df['pid'].isin(subset_df['pid']),
            ['pid', pheno_col]
        ].drop_duplicates()

        # Checking for sufficient sample size
        if alt_df.shape[0] <= 1 or ref_df.shape[0] <= 1:
            continue

        # Computing stats
        effect_size = np.mean(ref_df[pheno_col]) / np.mean(alt_df[pheno_col])
        p_value = stats.ttest_ind(
            alt_df[pheno_col],
            ref_df[pheno_col],
        )[1]

        # Adding stats to results
        results_df.append({
            'loc': row['location'],
            'ref': row['reference'],
            'alt': row['alternate'],
            'effect_size': effect_size,
            'p-value': p_value
        })

    results_df = pd.DataFrame(results_df)
    results_df['log10-p-value'] = -np.log10(results_df['p-value'])
    results_df['ref_alt'] = results_df['ref'] + "->" + results_df['alt']

    # Making a figure
    fig = px.scatter(
        results_df,
        x="loc",
        y="log10-p-value",
        color="ref_alt",
        size='effect_size')
    # fig.update_layout(legend_title_text='Ref -> Alt')
    fig.update_xaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_yaxes(showline=True, linewidth=2, linecolor='black', mirror=True)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='grey')
    fig.update_layout({
        'legend_title_text': 'Ref->Alt',
        'plot_bgcolor': 'rgba(0,0,0,0)'
    })
    return results_df, fig


def main():
    """Generates a manhattan plot using plotly express and dash
    """
    options = parse_args()
    assembled_df = assemble(options.input_stem)
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
