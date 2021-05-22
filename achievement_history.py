"""achievement_history.py: Download the global achievement statistics."""

__author__ = "Clemens Fiedler"
__email__ = "clemens.mb.fiedler@gmail.com"

# imports
from datetime import datetime as dt
import pandas as pd
from apscheduler.schedulers.blocking import BlockingScheduler
from achievement_tools import get_achievement_stats
import os


def get_time_now():
    """Get current time and return as formatted string."""
    date_format = "%Y-%m-%d-%H:%M:%S"

    return dt.now().strftime(date_format)


def initialize_data_file(appid, file_name):
    """Create the initial csv file."""
    new_data = get_achievement_stats(appid)
    data_frame = pd.DataFrame.from_dict(new_data)
    del data_frame['percentage']

    print("Creating new file for appid: {})".format(appid))
    data_frame.to_csv(file_name, index=False)

    return


def update(appid, file_name):
    """Load the old datafile and updates it with new information.

    1. load old datafile
    2. download new statistics and update old datafile with new information
    3. save updated datafile to disk

    Args:
        appid: steam app identification number
        file_name: name of file used to store information
    Returns:
        the updated datafile
    """
    # TODO create new file if old one exists

    if not os.path.exists(file_name):
        initialize_data_file(appid, file_name)

    # read old dataset
    data_old = pd.read_csv(file_name)

    # get time
    time = dt.now().strftime("%Y-%m-%d-%H%M%S")

    # load new data
    new_raw = get_achievement_stats(appid)
    data_new = pd.DataFrame.from_dict(new_raw)[['title', 'percentage']]
    data_new = data_new.rename(columns={'percentage': time})
    data_out = data_old.merge(data_new, on='title', how='left')

    if len(data_out) != len(data_old):
        raise ImportError("Something went wrong.")
    else:
        data_out.to_csv(file_name, index=False)
    return data_out


if __name__ == "__main__":
    appid = 1328670
    file_name = 'mass_effect.csv'

    def task():
        """Print time and update file."""
        print('updating file ' + get_time_now())
        _ = update(appid, file_name)
        return

    task()
    scheduler = BlockingScheduler()
    scheduler.add_job(task, 'interval', hours=1)

    print('starting scheduled task at ' + get_time_now())
    print('appid: {}'.format(appid))
    scheduler.start()


