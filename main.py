import sys
from vns_mh import VNS

import json
import pandas as pd
from time import time

from calendar import monthrange

max_iter = int(sys.argv[1])

def json_to_dict(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)

    result = {}
    for item in data:
        if isinstance(item, dict):
            nome = item["nome"]
            dias = item["dias"].split()
            result[nome] = dias

    return result

def cat_shifts_month(month):
    with open("./Dados/month_data.json", "r") as file:
        data = json.load(file)

    return data[month]

def get_days_in_month(month):
    year = int(str(month)[:4])
    month_number = int(str(month)[4:])

    return monthrange(year, month_number)[1]

month_min = {
    202401 : 4,
    202402 : 5,
    202403 : 2,
    202404 : 1,
    202405 : 5,
    202406 : 5,
    202407 : 5,
    202408 : 5,
}

columns = month_min.keys()
df = pd.DataFrame(columns=columns)
for i in range(9,10):
  for mes in range(202401, 202408):
    people = json_to_dict(f"./Dados/{mes}.json")
    shifts = cat_shifts_month(str(mes))
    df.at["People", mes] = len(people.keys())
    df.at["Shifts", mes] = len(shifts)
    df.at["MinShifts", mes] = month_min[mes]

    restrictions = {
        "People": people,
        "Shifts": shifts,
        "MaxPeoplePerShift": 2,
        "MinShifts": month_min[mes],
        "MaxShifts": 10,
        "MaxConsecutiveShifts": 1,
        "ConsecutiveRestTime": 6,
        "MonthDays": get_days_in_month(mes),
    }

    for j in [10,20,30,40]:
        start = time()
        vns = VNS(restrictions, i)
        random = vns.randomSchedule()
        df.at[f"Cost(Random) - Seed: {i} - k_max: {j} - max_iter{max_iter}", mes] = random
        cost = vns.vns(j, max_iter)
        end = time() - start
        df.at[f"Cost(VNS) - Seed: {i} - k_max: {j} - max_iter{max_iter}", mes] = cost
        df.at[f"Duration - Seed: {i} - k_max: {j} - max_iter{max_iter}", mes] = end   
  df.to_csv(f"results{max_iter}seed{i}.csv")
