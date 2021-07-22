from typing import Tuple, List

class SAT:

    def __init__ (self, name: str, days: int, blocks: int, countP: int):
        """
        Constructor that stores all initial information and calculates basic values
        that will be use to construct all the clauses that will model the problem
        :param self: Object
        :param days: Number of days allowed
        :param blocks: Number of blocks allowed per day
        :param participants: Number of participants of the tournament
        """
        self.days = days
        self.blocks = blocks
        self.countP = countP
        self.name = name

    def to_var(self, local: int, visit: int, day: int, block: int) -> int:
        """
        Function to calculate the variable number corresponding to a match between
        two specific participants, selecting the local and visitant, in a specific day
        and block of the day. 
        :param local: Int representing local participant
        :param visit: Int representing visitant participant
        :param day: Int representing match day starting on "start_date"
        :param block: Int representing day block for the match
        :returns: SAT variable
        """
        return 1 + local + visit * self.base[1] + day * self.base[2] + block * self.base[3]

    def from_var(self, var: int) -> Tuple:
        """
        Given a logical variable we compute the corresponding match
        :param var: Variable that represents a match
        :returns: Tuple with elements describing the match
        """
        var -= 1
        base = self.base[1]

        local = var % base
        var //= base

        visit = var % base
        var //= base

        day = var % base
        var //= base

        block = var % base

        return (local, visit, day, block)

    def from_vars(self, vars: List[int]) -> List[Tuple]:
        """
        Given a list of logical variables (could be negated) we compute the corresponding matches
        :param vars: List of variables to compute corresponding matches
        :returns: List of tuples describing matches
        """
        return [self.from_var(var) for var in vars]

        
    def generate_all_vs_all_clauses(self) -> None:
        """
        Function to generate clauses that specify that two competitors should play at least once,
        for all pairs of competitors (considering local and visitant arrangements)
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    clause = []
                    for d in range(self.days):
                        for b in range(self.blocks):
                            clause.append(self.to_var(i, j, d, b))
                    self.clauses.append(clause)

    def generate_non_rep_clauses(self) -> None:
        """
        Function to generate clauses that specify that two competitors should play at most once,
        for all pairs of competitors (considering local and visitant arragements)
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    for d in range(self.days):
                        for b in range(self.blocks):
                            v = -self.to_var(i, j, d, b)
                            for d2 in range(d+1, self.days):
                                    for b2 in range(self.blocks):
                                        self.clauses.append([v, -self.to_var(i, j, d2, b2)])

    def generate_one_per_day_clauses(self) -> None:
        """
        Function to generate clauses that specify that one competitor will compete at most once per day
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    for d in range(self.days):
                        for b in range(self.blocks):
                            v = -self.to_var(i, j, d, b)
                            for b2 in range(self.blocks):
                                if b2 != b:
                                    for j2 in range(j+1, self.countP):
                                        self.clauses.append([v, -self.to_var(i, j2, d, b2)])
                                        self.clauses.append([v, -self.to_var(j2, i, d, b2)])
                                    for i2 in range(i+1, self.countP):
                                        self.clauses.append([v, -self.to_var(i2, j, d, b2)])
                                        self.clauses.append([v, -self.to_var(j, i2, d, b2)])
                                    self.clauses.append([v, -self.to_var(j, i, d, b2)])


    def generate_non_type_rep_clauses(self) -> None:
        """
        Function to generate clauses that specify that a participant cannot play two consecutive 
        days as local or as visitant
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    for d in range(self.days-1):
                        for b in range(self.blocks):
                            v = -self.to_var(i, j, d, b)
                            for j2 in range(self.countP):
                                if i != j2 and j2 != j:
                                    for b2 in range(self.days):
                                        self.clauses.append([v, -self.to_var(i, j2, d+1, b2)])
                            for i2 in range(self.countP):
                                if i2 != j and i2 != i:
                                    for b2 in range(self.days):
                                        self.clauses.append([v, -self.to_var(i2, j, d+1, b2)])

    def generate_not_same_time_clauses(self) -> None:
        """
        Function to generate clauses that specify that not to games can happen at the same time
        """
        for d in range(self.days):
            for b in range(self.blocks):
                for i in range(self.countP):
                    for j in range(self.countP):
                        if i != j:
                            v = -self.to_var(i, j, d, b)
                            for i2 in range(i, self.countP):
                                j2_lb = j+1 if i2 == i else 0
                                for j2 in range(j2_lb, self.countP):
                                    if (i != i2 or j != j2) and i2 != j2:
                                        self.clauses.append([v, -self.to_var(i2, j2, d, b)])

    def build(self):
        """ Function to generate all clauses """
        self.clauses = []

        maxvar = max(self.days, self.blocks, self.countP)
        self.base = [ maxvar ** i for i in range(4) ]
        
        self.generate_all_vs_all_clauses()
        self.generate_non_rep_clauses()
        self.generate_one_per_day_clauses()
        self.generate_non_type_rep_clauses()
        self.generate_not_same_time_clauses()

    def generate_model(self, filename: str) -> None:
        """
        Function to create the file that will contain the SAT model of the problem in cnf form
        :param filename: Path of file to create
        """
        self.build()

        with open(filename, "w") as f:
            print(f"c {self.name}", file=f)
            max_var = self.to_var(self.countP-2, self.countP-1, self.days-1, self.blocks-1)
            print(f"p cnf {max_var} {len(self.clauses)}", file=f)            
            for clause in self.clauses:
                print(" ".join([str(var) for var in clause]), end=" 0\n", file=f)