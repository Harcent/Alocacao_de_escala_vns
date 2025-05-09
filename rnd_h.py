'''
  restictions (dict): A dictionary with the following keys
        People (dict): A dictionary with the people's names as keys and their requests as values. 
            Requests (list): A list of shifts the person can work.
        Shifts (list): A list of available shifts.
        MaxPeoplePerShift (int): The maximum number of people that can work in a shift.
        MinShifts (int): The minimum number of shifts a person can work.
        MaxShifts (int): The maximum number of shifts a person can work.
        MaxConsecutiveShifts (int): The maximum number of consecutive shifts a person can work.
        ConsecutiveRestTime (int): The minimum rest time after achieving a MaxConsectiveShifts.
        MonthDays (int): The number of days in the month.
'''
import numpy as np
import copy

class RND:
    def __init__(self, restrictions: dict, seed=0) -> None:
        # Initialize the RND class
        # Deep copy the restrictions to avoid modifying the original data
        restrictions = copy.deepcopy(restrictions)
        
        # Set the random seed for reproducibility
        np.random.seed(seed)
        
        # Initialize people and shifts
        self.P = np.array(list(restrictions['People'].keys()))
        self.allShifts = np.array([f"{i}{j}" for i in range(1, restrictions["MonthDays"] + 1) for j in ['D', 'N']])
        
        self.T = np.array(list(dict.fromkeys(restrictions['Shifts']))) if 'Shifts' in restrictions else self.allShifts
        
        # Initialize other attributes
        self.N = restrictions['MaxPeoplePerShift']
        self.m = restrictions['MinShifts']
        self.M = restrictions['MaxShifts']
        self.C = restrictions['MaxConsecutiveShifts']
        self.D = restrictions['ConsecutiveRestTime']
        
        # Initialize x and y arrays
        self.x = np.zeros((len(self.P), len(self.allShifts)), dtype=int)
        self.y = np.zeros((len(self.allShifts)), dtype=int)
        
        # Create index mappings
        self.peopleIndex = {p: i for i, p in enumerate(self.P)}
        self.shiftIndex = {s: i for i, s in enumerate(self.allShifts)}
        
        # Initialize the R array
        R = restrictions['People']
        self.R = np.zeros((len(self.P), len(self.allShifts)), dtype=int)
        rows = np.array([self.peopleIndex[p] for p in self.P for s in R[p]])
        cols = np.array([self.shiftIndex[s] for p in self.P for s in R[p]])
        self.R[rows, cols] = 1
        
        # Initialize possible requests
        self.requests = np.copy(self.R)
        
        # Initialize the minimum and maximum shifts counters
        self.minimum = {p: 0 for p in self.P}
        self.maximum = {p: 0 for p in self.P}
        
        # Auxiliary variables
        self.peopleNumber = len(self.P)
        self.remainingRequests = np.count_nonzero(self.R)
        self.shifts = restrictions['Shifts'] if 'Shifts' in restrictions else None
        if self.shifts:
            self.availableShifts = np.zeros(len(self.allShifts), dtype=int)
            shifts, shiftCounts = np.unique(self.shifts, return_counts=True) 
            for shift, count in zip(shifts, shiftCounts):
                self.availableShifts[self.shiftIndex[shift]] = count 
        else:
            self.availableShifts = np.full(len(self.allShifts) , self.N)
        self.remainingShifts = np.sum(self.availableShifts)
        
    def randomOrder(self) -> None:
    # Randomly shuffle the order of the people
        np.random.shuffle(self.P)
    
    def assignShifts(self, person: str) -> None:
    # Assign shifts to people while checking the constraints
        self.remainingRequests -= 1
        t = np.random.choice(np.where(self.requests[self.peopleIndex[person]] == 1)[0])
        self.requests[self.peopleIndex[person], t] = 0
        canAssign = self.availableShifts[t] > 0
        if canAssign:
            self.x[self.peopleIndex[person], t] = 1
            if not self.maxConsecutiveShifts() and not self.consecutiveRestTime():
                self.x[self.peopleIndex[person], t] = 0
                return
            self.availableShifts[t] -= 1
            self.remainingShifts -= 1
    
    def garanteeMinimum(self) -> None:
    # Generate a random starting schedule that tries to satidfy the minimum shifts constraint
        stop = {p : 0 for p in self.P}
        while sum(stop.values()) < self.peopleNumber:
            for p in self.P:
                if self.minimum[p] < 1 and np.sum(self.requests[self.peopleIndex[p]]) > 0:
                    self.assignShifts(p)
                else:
                    stop[p] = 1
            #self.updateStop(stop)
            self.updateMinMax()
    
    def fillRemaining(self) -> None: 
    # Continues the schedule generation from where garanteeMinimum left off
        stop = {p : 0 for p in self.P}
        while sum(stop.values()) < self.peopleNumber:
            for p in self.P:
                if self.maximum[p] < 1 and np.sum(self.requests[self.peopleIndex[p]]) > 0:
                    self.assignShifts(p)
                else:
                    stop[p] = 1
            #self.updateStop(stop)
            self.updateMinMax()
    
    def updateStop(self, stop: dict) -> None:
    # Updates the stop condition for the assigment of shifts
    # Checks if there are no more requests or shifts available
        if self.remainingRequests < 1 or self.remainingShifts < 1:
            [stop.update({p: 1}) for p in self.P]
    
    def updateMinMax(self) -> None:
    # Updates the minimum and maximum shifts counters for each person
        [self.minimum.update({p: 1}) for p in self.P if sum(self.x[self.peopleIndex[p]][self.shiftIndex[t]] for t in self.T) >= self.m]
        [self.maximum.update({p: 1}) for p in self.P if sum(self.x[self.peopleIndex[p]][self.shiftIndex[t]] for t in self.T) == self.M] 
       
    def minShifts(self) -> bool:
    # Checks if the minimum shifts constraint is satisfied    
        return all(sum(self.x[self.peopleIndex[p]][self.shiftIndex[t]] for t in self.T) >= self.m for p in self.P)
    
    def maxConsecutiveShifts(self) -> bool:
    # Checks if the maximum consecutive shifts constraint is satisfied      
        return all(
            all(
                sum(self.x[p][self.shiftIndex[t]] for t in self.allShifts[i:i + self.C + 1]) <= self.C
                for i in range(len(self.allShifts) - self.C - 1)
            )
            for p in range(self.peopleNumber)
        )
    
    def consecutiveRestTime(self) -> bool:
    # Checks if the consecutive rest time constraint is satisfied    
         return all(
            not (
                sum(self.x[p][self.shiftIndex[self.allShifts[i+j]]] for j in range(self.C)) == self.C and
                any(self.x[p][self.shiftIndex[self.allShifts[i+self.C+k]]] == 1 for k in range(self.D))
            )
            for p in range(self.peopleNumber)
            for i in range(len(self.allShifts) - self.C - self.D)
        )  
    
    def resetSolution(self) -> None:
    # Resets the solution to the initial state
        self.x = np.zeros((len(self.P), len(self.allShifts)), dtype=int)
        self.requests = np.copy(self.R)
        self.remainingRequests = np.count_nonzero(self.R)
        self.remainingShifts = np.sum(self.availableShifts)
        if self.shifts:
            self.availableShifts = np.zeros(len(self.allShifts), dtype=int)
            shifts, shiftCounts = np.unique(self.shifts, return_counts=True) 
            for shift, count in zip(shifts, shiftCounts):
                self.availableShifts[self.shiftIndex[shift]] = count 
        else:
            self.availableShifts = np.full(len(self.allShifts) , self.N)
        self.minimum = {p: 0 for p in self.P}
        self.maximum = {p: 0 for p in self.P}
    
    def randomSchedule(self) -> None:
    # Generates a random schedule that satisfies the constraints
        # while True:
        #     self.garanteeMinimum()
        #     if self.minShifts():
        #         break
        #     self.resetSolution()
        #     self.randomOrder()
        self.fillRemaining()
        self.updateY()
        return self.cost()
        #self.display()

    def updateY(self) -> None:
    # Updates the y array    
        for t in self.allShifts:
            self.y[self.shiftIndex[t]] = 1 if sum(self.x[p][self.shiftIndex[t]] for p in range(self.peopleNumber)) >= 1 else 0
    
    def cost(self) -> int:
    # Returns the cost of the solution
        return sum(
            self.N + self.N * (1 - self.y[self.shiftIndex[t]]) - sum(self.x[p][self.shiftIndex[t]] for p in range(self.peopleNumber))
            for t in self.allShifts
        )
     
    def display(self) -> None: 
    # Displays the schedule   
        for p in self.P:
            schedule = np.where(self.x[self.peopleIndex[p]] == 1)[0]
            schedule = [self.allShifts[s] for s in schedule]
            print(f'{p:<9} :', *schedule, len(schedule))
        print(self.cost())