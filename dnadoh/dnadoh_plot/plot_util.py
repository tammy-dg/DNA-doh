"""Plotting utils"""

import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
from scipy import stats

# this file serves to keep all the plotting functionality in one place
# the idea is to separate the figure creation process from the dash framework


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

    BASES = ["A", "C", "G", "T"]

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
    
# TODO: add ecdf plotting functionality


def _to_html(fig):
    return pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn",
        include_mathjax="cdn",
        config={
            "showLink": True,
            "toImageButtonOptions": {
                "format": "svg",
                "width": 750,
                "height": 600,
            },
        },
    )