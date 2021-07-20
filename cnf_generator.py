class CNF:

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

    def to_var(self, sign: int, local: int, visit: int, day: int, block: int) -> int:
        """
        Function to calculate the variable number corresponding to a match between
        two specific participants, selecting the local and visitant, in a specific day
        and block of the day. The sign will be used to specify if we want the variable
        negated or not
        """
        return sign * (1 + local + visit * self.base[1] + day * self.base[2] + block * self.base[3])

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
                            clause.append(self.to_var(1, i, j, d, b))
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
                            v = self.to_var(-1, i, j, d, b)
                            for d2 in range(self.days):
                                if d != d2:
                                    for b2 in range(self.blocks):
                                        self.clauses.append([v, self.to_var(-1, i, j, d2, b2)])

    def generate_one_per_day_clauses(self) -> None:
        """
        Function to generate clauses that specify that one competitor will compete at most once per day
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    for d in range(self.days):
                        for b in range(self.blocks):
                            v = self.to_var(-1, i, j, d, b)
                            for j2 in range(self.countP):
                                if j2 != i:
                                    for b2 in range(self.blocks):
                                        if b2 != b:
                                            self.clauses.append([v, self.to_var(-1, i, j2, d, b2)])
                                            self.clauses.append([v, self.to_var(-1, j2, i, d, b2)])

    def generate_non_type_rep_clauses(self) -> None:
        """
        Function to generate clauses that specify that a participant cannot play two consecutive 
        days as local or as visitant
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    for d in range(self.days):
                        for b in range(self.blocks):
                            v = self.to_var(-1, i, j, d, b)
                            for j2 in range(self.countP):
                                if i != j2 and j2 != j:
                                    for b2 in range(self.days):
                                        self.clauses.append([v, self.to_var(-1, i, j2, d+1, b2)])
                            for i2 in range(self.countP):
                                if i2 != j and i2 != i:
                                    for b2 in range(self.days):
                                        self.clauses.append([v, self.to_var(-1, i2, j, d+1, b2)])

    def generate_not_same_time_clauses(self) -> None:
        """
        Function to generate clauses that specify that not to games can happen at the same time
        """
        for i in range(self.countP):
            for j in range(self.countP):
                if i != j:
                    for d in range(self.days):
                        for b in range(self.blocks):
                            v = self.to_var(-1, i, j, d, b)
                            for i2 in range(self.countP):
                                for j2 in range(self.countP):
                                    if i != i2 or j != j2:
                                        self.clauses.append([v, self.to_var(-1, i2, j2, d, b)])

    def build(self):
        """ Function to generate all clauses """
        self.clauses = []

        maxvar = max(self.days, self.blocks, self.countP) + 1
        self.base = [1]
        for i in range(1, 4):
            self.base.append(self.base[i-1] * maxvar)
        
        self.generate_all_vs_all_clauses()
        self.generate_non_rep_clauses()
        self.generate_one_per_day_clauses()
        self.generate_non_type_rep_clauses()
        self.generate_not_same_time_clauses()

    def generate_model(self, filename: str) -> None:

        self.build()

        with open(filename, "w") as f:
            
            print(f"c {self.name}", file=f)
            max_var = self.to_var(1, self.countP, self.countP, self.days, self.blocks)
            print(f"p cnf {max_var} {len(self.clauses)}", file=f)
            for clause in self.clauses:
                print(" ".join(clause), end=" 0\n", file=f)
        
        