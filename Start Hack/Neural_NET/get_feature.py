import pandas as pd
import requests
import xml.etree.ElementTree as ET
from dateutil.parser import parse
import numpy as np

entso_e_token = 'd9281f86-65db-4158-b487-4eeb317c4f2e'
entso_e_url = 'https://transparency.entsoe.eu/api'
grid = {
    'France, RTE BZ / CA / MBA': '10YFR-RTE------C',
    'Denmark': '10Y1001A1001A65H',
    'Czech Republic, CEPS BZ / CA/ MBA': '10YCZ-CEPS-----N',
    'Poland, PSE SA BZ / BZA / CA / MBA': '10YPL-AREA-----S',
    # 'Norway, Norway MBA, Stattnet CA': '10YNO-0--------C',
    'Austria, APG CA / MBA': '10YAT-APG------L',
    'Luxembourg, CREOS CA': '10YLU-CEGEDEL-NQ',
    # 'Belgium, Elia BZ / CA / MBA': '10YBE----------2'
    'Netherlands, TenneT NL BZ / CA/ MBA': '10YNL----------L'
}
def get_germany_inflow(start_year, end_year):

    in_data = pd.DataFrame()
    for grid_elem in grid.keys():
        grid_elem_data = pd.DataFrame()
        for year in list(range(start_year, end_year+1)):
            params = {
                'securityToken': entso_e_token,
                'documentType': 'A11',
                'in_Domain': '10Y1001A1001A83F',
                'out_Domain': grid[grid_elem],
                'periodStart': '{}01010000'.format(year),
                'periodEnd': '{}01010000'.format(year+1)
            }

            r = requests.get(entso_e_url, params)
            root = ET.fromstring(r.content)

            code = '{urn:iec62325.351:tc57wg16:451-3:publicationdocument:7:0}'
            for ts in root.findall(code+'TimeSeries'):
                start = ts.find(code+'Period').find(code+'timeInterval').find(code+'start').text
                end = ts.find(code+'Period').find(code+'timeInterval').find(code+'end').text
                points = ts.find(code+'Period').findall(code+'Point')
                df = pd.DataFrame(
                    [int(pt.find(code+'quantity').text) for pt in points],
                    index=pd.date_range(start=parse(start), end=parse(end), freq='1H', closed='left'),
                    columns=[grid_elem]
                )
                grid_elem_data = pd.concat([grid_elem_data, df], axis=0, verify_integrity=True)

        in_data = pd.concat([in_data, grid_elem_data], axis=1, verify_integrity=True)

    return in_data

def DF_to_arrays(dataframe):
    dataframe = dataframe.fillna(0)
    dataframe1 = dataframe.copy(deep=True)
    input_array = dataframe1.to_numpy()
    return input_array

feature_array = DF_to_arrays(get_germany_inflow(2018, 2021))

