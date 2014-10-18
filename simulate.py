from random import randint, uniform, normalvariate
from copy import deepcopy

class Cell:
    ERRORS_PER_TICK = 122000

    MUTATION_LETHAL_PER_1000 = 396
    MUTATION_NON_LETHAL_BAD_PER_1000 = 312
    MUTATION_NEUTRAL_PER_1000 = 271
    MUTATION_ADVANTAGEOUS_PER_1000 = 21

    ENERGY_NEEDED_TO_DIVIDE = 4.0
    AVERAGE_ENERGY_PER_TICK = 1.0

    # inherited
    drug_resistance = 0
    mitosis_rate = 0
    dynasty_mutations = 0
    max_time_to_live = 0
    repair_success = 0
    p53_effectiveness = 0

    lifetime_errors = 0
    new_errors = 0
    life = 0
    time_to_live = 0
    time_to_divide = False
    can_divide = True
    generational_number = 1
    excess_energy = 0
    is_signaling_apoptosis = False

    def __init__(self,
                 drug_resistance=0,
                 mitosis_rate=5,
                 life=100,
                 repair_success=0.99999,
                 can_divide=True,
                 max_time_to_live=10,
                 p53_effectiveness=0.95):
        self.drug_resistance = drug_resistance
        self.mitosis_rate = mitosis_rate
        self.life = life
        self.repair_success = repair_success
        self.can_divide = can_divide
        self.max_time_to_live = max_time_to_live
        self.time_to_live = max_time_to_live
        self.p53_effectiveness = p53_effectiveness

    def __repr__(self):
        return ('Cell(dr=%s, mr=%s, err=%s, mut=%s, L=%s,'
                'rep=%s, p53=%s, ttl=%s, g=%s)') % (
                self.drug_resistance,
                self.mitosis_rate,
                self.new_errors,
                self.dynasty_mutations,
                self.life,
                self.repair_success,
                self.p53_effectiveness,
                self.time_to_live,
                self.generational_number)

    def gain_energy(self):
        self.excess_energy = (self.excess_energy +
                             max(normalvariate(
                                    self.AVERAGE_ENERGY_PER_TICK, 
                                    self.AVERAGE_ENERGY_PER_TICK / 4.0), 0.0))

    def has_energy_to_divide(self):
        return self.excess_energy >= self.ENERGY_NEEDED_TO_DIVIDE

    def age(self, time_elapsed=1):
        self.time_to_live = self.time_to_live - time_elapsed

        if(self.time_to_live <= 0):
            self.kill()

    def kill(self):
        self.life = 0

    def mutate_lethal(self):
        self.kill()

    def mutate_non_lethal_bad(self):
        dice_roll = randint(1,1000)

        if(dice_roll < 250):
            self.drug_resistance = max(self.drug_resistance -
                                       randint(1, 15), 0)
        elif(dice_roll < 500):
            self.mitosis_rate = (self.mitosis_rate +
                                randint(1,2))
        elif(dice_roll < 750):
            self.life = max(self.life - randint(1, 33), 0)
        elif(dice_roll < 900):
            self.repair_success = max(self.repair_success -
                                      uniform(0.0001, 0.0050), 0)
        elif(dice_roll < 960):
            self.max_time_to_live = max(self.max_time_to_live -
                                        randint(1, 3), 1)
        elif(dice_roll < 999):
            self.can_divide = False
        else:
            self.p53_effectiveness = max(self.p53_effectiveness -
                                         uniform(0.01, 1.0), 0)

    def mutate_neutral(self):
        pass

    def mutate_good(self):
        dice_roll = randint(1,1000)

        if(dice_roll < 250):
            self.drug_resistance = (self.drug_resistance +
                                   randint(1, 15))
        elif(dice_roll < 500):
            self.mitosis_rate = max(self.mitosis_rate -
                                    randint(1, 2), 1)
        elif(dice_roll < 750):
            self.life = min(max(self.life + randint(1, 15), 0), 150)
        elif(dice_roll < 810):
            self.max_time_to_live = max(self.max_time_to_live +
                                        randint(1, 2), 0)
        elif(dice_roll < 999):
            self.repair_success = min(max(self.repair_success +
                                          uniform(0.0001, 0.0050), 0.0), 
                                  0.99999)
        else:
            self.p53_effectiveness = max(self.p53_effectiveness +
                                         uniform(0.01, 0.05), 0)

    def damage(self):
        dna_errors_max = int(max(normalvariate(self.ERRORS_PER_TICK,
                                               self.ERRORS_PER_TICK / 4), 0))

        self.lifetime_errors = self.lifetime_errors + dna_errors_max
        self.new_errors = dna_errors_max

    def repair(self):
        expected_errors = ((1.0 - self.repair_success) *
                          self.new_errors)
        self.new_errors = int(max(normalvariate(expected_errors,
                                                expected_errors / 4), 0.0))

        # There need to be errors and the p53 gene needs 
        # to be working for repair
        if(self.new_errors > 0 and uniform(0.0, 1.0) <=
                                   self.p53_effectiveness * self.new_errors):
            dice_roll = randint(1,1000)

            if(dice_roll < 900):
                # Try another repair cycle, hold the cell here
                self.can_divide = False
            else:
                # Trigger suicide
                self.is_signaling_apoptosis = True
        else:
            self.can_divide = True

    def mutate(self):
        dna_mutations_expected_value = self.new_errors
        dna_mutations = int(max(normalvariate(dna_mutations_expected_value,
                                              dna_mutations_expected_value /
                                              4), 0.0))

        self.dynasty_mutations = self.dynasty_mutations + dna_mutations

        for x in range(0, dna_mutations):
            dice_roll = randint(1,1000)

            if(dice_roll < self.MUTATION_LETHAL_PER_1000):
                # lethal result
                self.mutate_lethal()
            elif(dice_roll < self.MUTATION_LETHAL_PER_1000 +
                             self.MUTATION_NON_LETHAL_BAD_PER_1000):
                # non-lethal, but bad result
                self.mutate_non_lethal_bad()
            elif(dice_roll < self.MUTATION_LETHAL_PER_1000 +
                             self.MUTATION_NON_LETHAL_BAD_PER_1000 +
                             self.MUTATION_NEUTRAL_PER_1000):
                # neutral result
                self.mutate_neutral()
            elif(dice_roll < self.MUTATION_LETHAL_PER_1000 +
                             self.MUTATION_NON_LETHAL_BAD_PER_1000 +
                             self.MUTATION_NEUTRAL_PER_1000 +
                             self.MUTATION_ADVANTAGEOUS_PER_1000):
                # good result
                self.mutate_good()

        self.is_expressing_p53 = (self.p53_effectiveness * 
                                  self.dynasty_mutations) > 1
        self.new_errors = 0

    def divide(self):
        if(self.has_energy_to_divide()):
            self.excess_energy = (self.excess_energy -
                                 self.ENERGY_NEEDED_TO_DIVIDE)

            new_cell = Cell(drug_resistance = self.drug_resistance,
                            mitosis_rate = self.mitosis_rate,
                            repair_success = self.repair_success,
                            max_time_to_live = self.max_time_to_live,
                            p53_effectiveness = self.p53_effectiveness,
                            can_divide = True)

            new_cell.generational_number = self.generational_number + 1
            new_cell.dynasty_mutations = self.dynasty_mutations

            new_cell.mutate()
            self.mutate()

            return new_cell
        else:
            return None

class Population:
    cell_collection = []
    current_tick = 1

    def __init__(self, inital_cell):
        # add some clonal seed cells
        for x in range(0,10):
            self.cell_collection.append(deepcopy(inital_cell))

    def tick(self):
        new_cell_collection = []

        for cell in self.cell_collection:
            # eat
            cell.gain_energy()

            # accumulate damage
            cell.damage()

            # population control
            if(len(self.cell_collection) < 100):
                # time for dividing
                if(self.current_tick % cell.mitosis_rate == 0 and 
                   cell.has_energy_to_divide()):
                    cell.time_to_divide = True

                # start repair and divide process
                if(cell.time_to_divide):
                    # repair
                    cell.repair()

                    if(cell.can_divide):
                        new_cell = cell.divide()

                        if(new_cell):
                            new_cell_collection.append(new_cell)

            # age
            cell.age()

        self.cell_collection.extend(new_cell_collection)

        # die
        self.cell_collection[:] = [x for x in self.cell_collection if \
                                   x.life > 0 and 
                                   not(x.is_signaling_apoptosis)]

        self.current_tick = self.current_tick + 1

    def __str__(self):
        strbuf = []
        for cell in self.cell_collection:
            strbuf.append(cell.__repr__())
            strbuf.append('\n')
        return ''.join(strbuf)

# create population
p = Population(Cell(drug_resistance = 2, can_divide = True))

# begin division
for x in range(0,10000):
    p.tick()

# show results
print('----')
print(p)