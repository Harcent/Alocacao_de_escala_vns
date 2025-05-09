''' 
  Class to generate a schedule for a group of people based on their preferences and the available shifts.
  Attributes:
    people (dict): A dictionary with the people's names as keys and their restrictions as values.
      Restrictions are a dictionary with the following
        Priority (int): The person's priority.
        MaxShifts (int): The maximum number of shifts the person can work.
        Requests (set): A set of shifts the person wants to work.
    vacant (list): A list of available shifts.
'''
class Schedule:
  
  def __init__(self, people, vacancies):
    self.people = people
    self.vacancies = vacancies
    self.schedule = {p: [] for p in people}
    self.consecutive_counter = {p: {r: 0 for r in sorted(people[p]["Requests"], key=lambda x: (int(x[:-1]), x[-1]))} for p in people}
    self.allShifts = {f"{i}{j}" for i in range(1, 32) for j in ['M', 'T', 'N']}
    self.allShifts = sorted(self.allShifts, key=shift_sort_key)

# Heuristica de geração de escala
  def generateSchedule(self):
    people = sorted(self.people.keys(), key=lambda p: self.people[p]["Priority"])
    request_indices = {p: 0 for p in people}
    count = 0
    while count < len(people):
      for p in people:
        if not self.vacancies:
          break
        while request_indices[p] < len(self.people[p]["Requests"]):
          shift = self.people[p]["Requests"][request_indices[p]]
          if shift in self.vacancies and not self.conflict(self.schedule[p], shift, p):
            self.schedule[p].append(shift)
            self.vacancies.remove(shift)
            request_indices[p] += 1
            break
          request_indices[p] += 1
        else:
          request_indices[p] = len(self.people[p]["Requests"])
      count = sum([1 if request_indices[p] == len(self.people[p]["Requests"]) else 0 for p in people])

# Checagem de restrições        
  def conflict(self, schedule, new_shift, p):
    if len(schedule) == self.people[p]["MaxShifts"]:
      return True
    matches = {shiftPeriod: f"{int(new_shift[:-1])}{shiftPeriod}" in schedule for shiftPeriod in ['D', 'T', 'M']}
    shiftPeriod = new_shift[-1]
    if matches['D'] and (shiftPeriod == 'M' or shiftPeriod == 'T'):
      return True
    elif (matches['T'] or matches['M']) and shiftPeriod == 'D':
      return True
    return self.consecutiveLimit(new_shift, p)
  
  def consecutiveLimit(self, new_shift, p):
    new_date, new_shiftPeriod = int(new_shift[:-1]), new_shift[-1]
    consecutives = []
    for shift, count in self.consecutive_counter[p].items():
      date, shiftPeriod = int(shift[:-1]), shift[-1]
      if (date == new_date and shiftPeriod != new_shiftPeriod) or \
         (date == new_date + 1 and shiftPeriod == 'D' and new_shiftPeriod == 'N') or \
         (date == new_date - 1 and shiftPeriod == 'N' and new_shiftPeriod == 'D'):
          if count == 1:
            self.consecutive_counter[p][new_shift] = -1
            return True
          if shift in self.schedule[p]:
            consecutives.append(shift)
    if len(consecutives) == 2:
      self.consecutive_counter[p][new_shift] = -1
      return True
    for shift in consecutives:
      self.consecutive_counter[p][shift] += 1
    self.consecutive_counter[p][new_shift] = len(consecutives)
    return False

# Funções de exibição   
  def displaySchedule(self):
    shift_weight = {'M': 1, 'T': 1, 'N': 2, 'D': 2}

    for p in self.schedule:
        order = sorted(self.schedule[p], key=shift_sort_key)
        # Weighted count
        count = sum(shift_weight.get(shift[-1], 0) for shift in self.schedule[p]) / 2
        num = f"<{int(count)}>" if count.is_integer() else f"<{count}>"
        display = []
        for shift in order:
          day, turn = shift[:-1], shift[-1]
          if turn == "T" and f"{day}M" in display:
            display.remove(f"{day}M")
            display.append(f"{day}D")
          elif turn == "N" and f"{day}D" in display:
            display.remove(f"{day}D")
            display.append(f"{day}P")
          else:
            display.append(shift)
          
            
        print(f"{p:<10}{num:>4}:", *display)
          
    vac_count = sum(shift_weight.get(shift[-1], 0) for shift in self.vacancies) / 2
    v = f"<{int(vac_count)}>" if vac_count.is_integer() else f"<{vac_count}>"
    print(f"Vacancias {v:>4}:", *self.vacancies)
    
  def displayAtribution(self):
    print("Atribution:")
    for p in self.schedule:
      print(f"{p:<10}:", *self.schedule[p])
      negative = False
      for key, value in self.consecutive_counter[p].items():
        if value == -1:
          negative = True
          print(f"{key}", end=" ")
      if negative:
        print("")
        
  def displayPerson(self, person):
    print(f"Name: {person}")
    print(f"Priority: {self.people[person]['Priority']}")
    print(f"MaxShifts: {self.people[person]['MaxShifts']}")
    print(f"Requests: ", *self.people[person]['Requests'], sep=", ")
    print(f"Schedule: ", *self.schedule[person], sep=", ")
    print(f"CC: {self.consecutive_counter[person]}")
       
# Custom sort function
def shift_sort_key(shift):
    num = int(shift[:-1])          # Extract number part
    suffix = shift[-1]             # Extract letter (M, T, D, N)
    order = {'M': 1, 'T': 2, 'D' : 3,'N': 4}
    return (num, order[suffix])