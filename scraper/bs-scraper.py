# !usr/bin/env python3

import argparse
import json
from typing import Dict, List

import pandas as pd
import requests
from bs4 import BeautifulSoup, element

def args():
    """
    Argument Parser to take in command line arguements
    """
    parser = argparse.ArgumentParser(description='Run MOHFW in mutliple file save modes')
    parser.add_argument('-t', '--type', help='Type of outfile', type=str, required=True)
    parser.add_argument('-fn', '--filename', help='Name of the output file', type=str, required=False)
    return parser.parse_args()

def _get_page(url: str) -> bytes:
    """
    Makes a GET request to the specified url 
    and returns HTML content as bytes
    """
    try:
        page = requests.get(url)
        if not page.status_code == 200:
            raise Exception(f"Failed trying to load {url}")
        else:
            return page.content
    except Exception as e:
        print(f"The following exception occured while parsing {e}")

def _get_information(url: str) -> List[dict]:
    """
    Requests the page using _get_page method,
    creates a soup, parses soup and returns a list of dictionaries
    """
    content = _get_page(url= url)
    soup = BeautifulSoup(content, 'html5lib')
    tables = soup.find_all('table')
    cases_table = tables[-1]
    c_t_rows = cases_table.find_all('tr')
    c_t_header = [e.text for e in c_t_rows[0].find_all('th')]
    info = []
    rows_not_required = [0,28,29]
    for i, row in enumerate(c_t_rows):
        if i not in rows_not_required : 
            info.append(_parse_row(row=row, header=c_t_header))
        else:
            pass
    return info

def _parse_row(row: element.Tag, header: list) -> List[object]:
    """
    Parses individual rows from table and returns a dictionary
    """
    info_list = [item.text for item in row.find_all('td')]
    info = dict(zip(header, info_list))
    return info


def _export(info: list, how:str, filename:str):
    """
    Exports the data into specified fileformat
    """
    try:
        how = how.lower()
        supported = ["csv", "json"]
        method_map = {"csv": _to_csv,
                   "json": _to_json,
                  }
        if how not in supported:
            raise Exception(f"The format {how} is not yet supported")
        else: 
           save = method_map.get(how)
           save(info = info, filename=filename )
    except Exception as e:
        print(f"The following exception occured while processing the export \n {e}")

def _fname(type:str, filename:str)->str:
    """
    """
    if filename:
        return filename
    elif not filename and type == "csv":
        return "data.csv"
    elif not filename and type == "json":
        return "data.json"

def _to_csv(info: list, filename:str):
    """
    """
    fname = _fname(type='csv', filename=filename)
    df = pd.DataFrame(data=info)
    df.to_csv(fname, index=False)

def _to_json(info: list, filename:str):
    """
    """
    fname = _fname(type='json', filename=filename)
    with open(fname, 'w') as file:
        file.write(json.dumps(info, indent=4))

def main():
    type = args().type
    filename = args().filename
    information = _get_information(url='https://www.mohfw.gov.in/')
    _export(info = information, how=type, filename=filename)

if __name__ == '__main__':
    main()
