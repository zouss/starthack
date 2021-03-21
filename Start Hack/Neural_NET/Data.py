import wapi
from Label import LabelDataset
import numpy as np
from datetime import datetime
import pytz

tz_CET = pytz.timezone("Etc/GMT-1")
datetime_Germany = datetime.now(tz_CET)

time = datetime_Germany.strftime("%Y-%m-%dT%H:00Z")

def get_mean(data):
    # Mean delta price to label up or down price
    sigma_delta = 0
    for i in range(len(data)-1):
        delta = abs((data[i+1] - data[i]) / data[i])
        sigma_delta += delta
    mean_delta = sigma_delta / (len(data) - 1)
    return mean_delta

# Price dataset 
def get_label(time):  # Tune diff_const 
    # Load data
    config_file_path = 'Neural_NET//configfile.ini'
    session = wapi.Session(config_file=config_file_path)
    curve = session.get_curve(name='pri de spot €/mwh cet h a')
    ts = curve.get_data(data_from='2018-01-01T00:00Z', data_to=time)#'2021-03-21T00:00Z')
    pdseries = ts.to_pandas()
    class_lst = pdseries.tolist()
    class_lst = [i+0.0001 for i in class_lst] # eliminate zerodiv error

    mean_delta = get_mean(class_lst)


    set_label = LabelDataset(class_lst, mean_delta)

    labels = set_label.label_classify()


    print(f"Static : {labels.count([0])}")
    print(f"Change : {labels.count([1])}\n")
    return np.array(labels)


label_array = get_label(time)

def get_stat(time):  # Tune diff_const 
    # Load data
    config_file_path = 'Neural_NET//configfile.ini'
    session = wapi.Session(config_file=config_file_path)
    curve = session.get_curve(name='pri de spot €/mwh cet h a')
    ts = curve.get_data(data_from='2018-01-01T00:00Z', data_to=time)#'2021-03-21T00:00Z')
    pdseries = ts.to_pandas()
    class_lst = pdseries.tolist()
    class_lst = [i+0.0001 for i in class_lst] # eliminate zerodiv error

    mean_delta = get_mean(class_lst)

    set_label = LabelDataset(class_lst, mean_delta)

    status, up, down = set_label.up_or_down()
    
    return status
status_info = get_stat(time)
