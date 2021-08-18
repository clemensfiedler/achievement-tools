"""Make graphs based on Mass Effect Legendary Edition."""

__author__ = "Clemens Fiedler"
__email__ = "clemens.mb.fiedler@gmail.com"


appid = 1328670
file_name = 'mass_effect.csv'

from datetime import datetime as dt
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.dates import DateFormatter
import matplotlib.ticker as mtick
sns.set_theme()

import re


# read dataset
data = pd.read_csv(file_name)
data_t = data.drop(columns = 'description').set_index('title').T
data_t.index = pd.to_datetime(data_t.index)
data_t = data_t.reset_index()
data_t = data_t.rename(columns={'index':'time'})


# get achievements by importance
col_sel = [data.columns[i] for i in [0,1,-1]]
data_last = data[col_sel].rename(columns={col_sel[-1]:'percentage'})
data_last = data_last.sort_values('percentage', ascending=False)

with pd.option_context(
    'display.max_rows', None, 'display.max_columns', None
    ):
    print(data_last)


def plot(to_plot, title):
    """Plot a list of achievements.

    Args
    ----
    - to_plot: dictionary
    keys are the variable name
    entry are a replacement string to be used in the graphs
    """
    # plot
    # Create new dataset
    data_sel = data_t.rename(columns=to_plot)[
        ['time'] + list(to_plot.values())
        ]
    data_sel = data_sel.melt(id_vars='time', var_name='Achievement')

    fig, ax = plt.subplots(figsize=(10,5))
    g = sns.lineplot(
        data=data_sel, x='time', y='value',
        hue='Achievement', ax=ax
        )

    # Define the date format
    date_form = DateFormatter("%b-%d %H:%M")

    ax.xaxis.set_major_formatter(date_form)
    plt.xticks(rotation=45, ha="right")

    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1, decimals=0))
    ax.set_ylim(0,)
    ax.set_title(title)
    ax.set_ylabel("players with achievement")
    plt.tight_layout()

    fig.savefig(re.sub("\s+", "_", title) + '.png')

    return


if __name__ == '__main__':

    ac_games = {
        'Medal of Honor': 'Mass Effect 1',
        'Against All Odds': 'Mass Effect 2',
        'Legend': 'Mass Effect 3'
    }

    ac_comp = {
        "Sentinel Ally":"Kaidan Alenko",
        "Soldier Ally": "Ashley Williams",
        "Krogan Ally": "Urdnot Wrex",
        "Turian Ally": "Garrus Vakarian",
        "Quarian Ally": "Tali'Zorah nar Rayya",
        "Asari Ally": "Liara T'Soni"
    }

    ac_me1 = {
        'Distinguished Service Medal': 'Eden Prime',
        'Spectre Inductee': 'Spectre',
        'Medal of Heroism': 'Feros',
        'Council Legion of Merit': 'Virmire',
        'Honorarium of Corporate Service': 'Noveria',
        'Meritorious Service Medal': 'Illos'
    }

    plot(ac_games, 'Finished Game')
    plot(ac_comp, 'Completed 5 missions with companion')
    plot(ac_me1, 'Finished main missions (ME1)')
