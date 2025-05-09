import sys
from vns_mh import VNS
from vns_mh2 import VNS2
from schedule import Schedule

import json
import pandas as pd
from time import time
from copy import deepcopy

from calendar import monthrange

max_iter = 10
seed = 0

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
    202409 : 5,
    202410 : 5,
    202411 : 5,
    202412 : 5,
    202501 : 5,
    202502 : 5,
    202503 : 5,
    202504 : 5,
    202505 : 5,
    202506 : 5,
}

meses = list(month_min.keys())

columns = month_min.keys()
df = pd.DataFrame(columns=columns)

for mes in meses:
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
  
  people_dict = {}
  c = 0
  for p in people.keys():
      people_dict[p] = {
          "Priority": c,
          "Requests": people[p],
          "MaxShifts": 10,
      }
      c += 1
  start = time()
  greed = Schedule(people_dict, deepcopy(shifts))
  greed.generateSchedule()
  greedT = time() - start
  for j in [50]:
      start = time()
      vns = VNS(restrictions, seed)
      random = vns.randomSchedule()
      df.at[f"Cost(Random) - Seed: {seed} - k_max: {j} - max_iter{max_iter}", mes] = random
      cost = vns.vns(j, max_iter)
      end = time() - start
      df.at[f"Cost(VNS_R) - Seed: {seed} - k_max: {j} - max_iter{max_iter}", mes] = cost
      df.at[f"Duration - Seed: {seed} - k_max: {j} - max_iter{max_iter}", mes] = end   
      start = time()
      vns2 = VNS2(restrictions, greed, seed)
      df.at[f"Cost(Greed)", mes] = vns2.grdCost()
      cost = vns2.vns(j, max_iter)
      end = time() - start + greedT
      df.at[f"Cost(VNS_G) - Seed: {seed} - k_max: {j} - max_iter{max_iter}", mes] = cost
      df.at[f"Duration - Seed: {seed} - k_max: {j} - max_iter{max_iter}", mes] = end   
df.to_csv(f"results{max_iter}seed{seed}.csv")
