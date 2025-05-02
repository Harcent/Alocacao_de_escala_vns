import numpy as np
from rnd_h import RND

class  VNS(RND):
    def __init__(self, restrictions, seed=0):
    # Initialize the VNS class
        super().__init__(restrictions, seed)
        self.possibleWorkDays = None
        self.notPossible = np.array([[1 for t in self.allShifts]for p in self.P])
        self.xRnd = None
    
    def getPersonById(self, id: int) -> str:
    # Find a person's name by their id
        for p in self.P:
            if self.peopleIndex[p] == id: return p    
    
    def updatePossibleWorkDays(self, person: int) -> None:
    # Update the possible work days for a person
        intersect = np.bitwise_and(self.R[person], self.x[person])
        self.possibleWorkDays[person] = np.bitwise_xor(self.R[person], intersect)
        self.possibleWorkDays[person] = np.bitwise_and(self.possibleWorkDays[person], self.notPossible[person])  
        indices = np.where(self.possibleWorkDays[person] == 1)[0]
        for shift in indices:
            self.x[person, shift] = 1
            if not self.maxConsecutiveShifts() and not self.consecutiveRestTime(): 
                self.possibleWorkDays[person, shift] = 0
            self.x[person, shift] = 0
        self.remainingRequests = np.sum(self.possibleWorkDays)
    
    def removeImpossibleShifts(self) -> None:
    # Update the possible work days for all people    
        for p in range(self.peopleNumber):
            self.updatePossibleWorkDays(p)
    
    def resetVns(self) -> None:
    # Reset the variables for the vsn algorithm
        self.removeImpossibleShifts()
        self.requests = np.copy(self.possibleWorkDays)
        self.remainingShifts = np.sum(self.availableShifts)
        self.minimum = {p: 0 for p in self.P}
        self.maximum = {p: 0 for p in self.P}
        self.updateMinMax()
        self.randomOrder()
    
    def removeShifts(self, id: int) -> None:      
    # Remove a shift from a person    
        days = np.where(self.x[id] == 1)[0]
        if days.size == 0: return
        remove = np.random.choice(days)
        self.x[id][remove] = 0
        self.availableShifts[remove] += 1
        self.updatePossibleWorkDays(id)
        return remove
    
    def addShifts(self) -> None: 
    # Add back a shift to a person               
        self.resetVns()
        self.fillRemaining()
    
    def vns(self, kmax: int, max_iter: int) -> None:
    # Run the vns algorithm    
        self.xRnd = np.copy(self.x)
        intersect = np.bitwise_and(self.R, self.x)
        self.possibleWorkDays = np.bitwise_xor(self.R, intersect)  
        self.removeImpossibleShifts()
        k = 1
        best_x = np.copy(self.x)
        best_cost = self.cost()
        for _ in range(max_iter):
            while k <= kmax:
                self.x = np.copy(best_x)
                for _ in range(k):
                    id = np.random.choice(np.arange(self.peopleNumber))
                    self.removeShifts(id)
                self.addShifts()
                self.updateY()
                new = self.cost()
                if new < best_cost:
                    #print(f"New best: {new}")
                    best_x = np.copy(self.x)
                    best_cost = new
                    k = 1
                    continue
                k += 2
        self.x = np.copy(best_x)
        self.updateY()
        #self.display()
        #self.compare()
        return best_cost
    
    def compare(self) -> None:
    # Display  the difference between the original and the new schedule    
        intersect = np.bitwise_and(self.x, self.xRnd)
        x = np.bitwise_xor(self.x, intersect)
        xrnd = np.bitwise_xor(self.xRnd, intersect)
     
        for p in self.P:
            schedule = np.where(x[self.peopleIndex[p]] == 1)[0]
            schedule = [self.allShifts[s] for s in schedule]
            print(f'+{p:<9} :', *schedule, len(schedule))
            schedule = np.where(xrnd[self.peopleIndex[p]] == 1)[0]
            schedule = [self.allShifts[s] for s in schedule]
            print(f'-{p:<9} :', *schedule, len(schedule))
