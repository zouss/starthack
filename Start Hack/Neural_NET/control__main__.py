from torchtest import predict, data_loader
import csv 
from datetime import datetime, timedelta
from threading import Timer
from Classifier import Classifier_
from Data import status_info

x = datetime.today()
y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0) + timedelta(days=1)
delta_t = y-x

secs = delta_t.total_seconds()

def connect_csv_daily():
    try:
        boolean, status = predict(data_loader, Classifier_(), status_info)
        with open("Neural_NET/save.csv", "a") as csvfile:
            file_writer = csv.writer(csvfile)
            file_writer.writerow([str(boolean), str(status)])
        print("Saved!")
 
    except AssertionError:
        print("Error Occured! Please check!")
        pass
    except Exception as e:
        raise e

t = Timer(secs, connect_csv_daily())
t.start()
connect_csv_daily()
