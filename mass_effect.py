appid = 1328670
file_name = 'mass_effect.csv'

from datetime import datetime as dt
import pandas as pd

from scrape_personal_achievements import get_achievement_stats
from apscheduler.schedulers.blocking import BlockingScheduler


def initizalize_data_file(appid, file_name):
    """Create the initial csv file."""
    new_data = get_achievement_stats(appid)
    data_frame = pd.DataFrame.from_dict(new_data)
    del data_frame['percentage']
    del data_frame['profiles']

    data_frame.to_csv(file_name, index=False)


def update(appid, file_name):
    """Loads the old datafile and updates it with new information.

    Args
    ----
    appid: steam app identifcation number
    file_name: name of file used to store information
    """
    # TODO create new file if old one exists
    if False:
        initizalize_data_file(appid, file_name)

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
        raise ImportError("new data does not match old data!")
    else:
        data_out.to_csv(file_name, index=False)
    return data_out

#
#data = update(appid, file_name)

def task():
    print('updating file ' + dt.now().strftime("%Y-%m-%d-%H%M%S"))
    update(1328670, 'mass_effect.csv')
    return


task()
scheduler = BlockingScheduler()
scheduler.add_job(task, 'interval', hours=1)

print('starting scheduled task at ' + dt.now().isoformat())
scheduler.start()