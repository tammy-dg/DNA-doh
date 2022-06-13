import argparse

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

from statannot import add_stat_annotation

from assemble import assemble

# https://github.com/webermarcolivier/statannot/blob/master/example/example.ipynb

def get_unique_locations(df: pd.DataFrame):
    """Get unique locations with an alternate base"""
    locations = df["location"].drop_duplicates().dropna().to_list()
    return locations

def _get_pids(df: pd.DataFrame) -> set:
    pids = set(df["pid"].drop_duplicates().to_list())
    return pids


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
    assert len(reference) == 1, f"There is more than one reference base at position f{location}!"
    reference = reference.pop()

    # the subset will only contain individuals with an alternate base
    # to include individuals with the reference base,
    # we need to figure out who those are and add them back in
    all_pids = _get_pids(df)
    subset_pids = _get_pids(subset_df)
    leftover_pids = all_pids.difference(subset_pids)
    # build info to concatenate back
    data = df[["pid", "age", "gsex", "weight"]].drop_duplicates()
    data = data[data["pid"].isin(leftover_pids)]
    data = data.assign(
        location=[location] * len(data),
        reference=[reference] * len(data),
        alternate=["reference"] * len(data)
    )
    # concatenate to subset df now
    concat_df = pd.concat([subset_df, data], axis=0).sort_values(by=["pid"])
    
    # plot
    fig = px.box(concat_df, y=y_variable, x="alternate", color="alternate")
    fig.show()



def main():
    options = parse_args()
    print('test!')
    assembled_df = assemble(options.input_stem)

    locations = get_unique_locations(assembled_df)

    print(assembled_df)
    print(locations)

    for location in locations:
        plot_boxplot(assembled_df, "weight", location)

# test_results = add_stat_annotation(
#     ax,
#     data=df,
#     x="alternate",
#     y="weight",
#     box_pairs=[("C", "reference (T)"), ("G", "reference (T)"), ("A", "reference (T)")],
#     test="Mann-Whitney",
#     comparisons_correction=None,
#     text_format="star",
#     loc="outside",
#     verbose=2,
# )

# plt.show()

def parse_args():
    parser = argparse.ArgumentParser()
    # nothing here for now
    parser.add_argument(
        "--input_stem", type=str, default=None, help="Path/file stem of synthesized data"
    )
    options = parser.parse_args()
    return options

if __name__ == "__main__":
    main()
