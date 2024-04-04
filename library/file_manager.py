import csv
import json
import os

def read_cvs(filename:str):
    data = list()
    with open(filename, 'r', newline='', encoding='utf-8-sig') as csvfile:
        csvreader = csv.DictReader(csvfile,delimiter=";")
        for row in csvreader:
            data.append(row)
    return data

def read_json(filename:str):
    data = list()
    if not os.path.exists(filename):
        return data
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_json(filename:str, data:list):
    if filename==None:
        print("No file was indicated.")
        return data
    with open(filename,'w',encoding='utf-8') as fp:
        j_o = json.dumps(data,indent=4)
        fp.write(j_o)
    return []