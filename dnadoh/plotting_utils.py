from scipy import stats
import plotly.express as px
import plotly.graph_objects as go


def add_pvalue_annotation(df, fig, base, y_range, symbol=''):
    """
    arguments:
    bases --- a list of two different days e.g. ['A','reference']
    y_range --- a list of y_range in the form [y_min, y_max] in paper units
    """
    pvalue = stats.ttest_ind(
        df[df['reference']=="reference"].weight,
        df[df['reference']==base].weight)[1]
    # print(pvalue)
    if pvalue >= 0.05:
        symbol = 'ns'
    if pvalue < 0.05:
        symbol = '*'
    fig.add_shape(type="line",
        xref="x", yref="paper",
        x0="reference", y0=y_range[0], x1="reference", y1=y_range[1],
        line=dict(
            color="black",
            width=2,
        )
    )
    fig.add_shape(type="line",
        xref="x", yref="paper",
        x0=base, y0=y_range[1], x1=base, y1=y_range[1],
        line=dict(
            color="black",
            width=2,
        )
    )
    fig.add_shape(type="line",
        xref="x", yref="paper",
        x0=base, y0=y_range[1], x1=base, y1=y_range[0],
        line=dict(
            color="black",
            width=2,
        )
    )
    ## add text at the correct x, y coordinates
    ## for bars, there is a direct mapping from the bar number to 0, 1, 2...
    bar_xcoord_map = {x: idx for idx, x in enumerate(["reference", "C", "G", "A"])}
    fig.add_annotation(dict(font=dict(color="black",size=14),
        x=(bar_xcoord_map["reference"] + bar_xcoord_map[base])/2,
        y=y_range[1]*1.03,
        showarrow=False,
        text=symbol,
        textangle=0,
        xref="x",
        yref="paper"
    ))
