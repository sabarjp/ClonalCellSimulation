from random import randint, uniform, normalvariate


class Cell:
    """
    Represents a cell in a clonal colony. A cell has the following key
    properties:

    It can divide into two copies.
    It accumulates errors in its DNA.
    It needs energy to live.
    It needs energy to divide.
    """

    # The number of DNA errors on a cell per time tick.
    ERRORS_PER_TICK = 122000

    # Mutations out of a thousand that are lethal.
    MUTATION_LETHAL_PER_1000 = 396

    # Mutations out of a thousand that are not lethal, but poor.
    MUTATION_NON_LETHAL_BAD_PER_1000 = 312

    # Mutations out of a thousand that do nothing.
    MUTATION_NEUTRAL_PER_1000 = 271

    # Mutations out of a thousand that have an advantage.
    MUTATION_ADVANTAGEOUS_PER_1000 = 21

    ENERGY_NEEDED_TO_DIVIDE = 4.0
    LIFE_NEEDED_TO_DIVIDE = 30

    # Represents intake of food.
    AVERAGE_ENERGY_PER_TICK = 1.0

    # Represents ability to heal damage.
    AVERAGE_LIFE_PER_TICK = 0.2

    def __init__(self, drug_resistance=3, mitosis_rate=5, life=100,
                 repair_success=0.99999, can_divide=True, max_time_to_live=10,
                 tumor_suppression=0.95):
        #
        # GENETIC DATA
        #
        # These attributes are inherited by the daughter cells after
        # a division.
        self.drug_resistance = drug_resistance
        self.max_time_to_live = max_time_to_live
        self.repair_success = repair_success
        self.tumor_suppression = tumor_suppression

        # Rate of cellular division (not inherited).
        self.mitosis_rate = mitosis_rate

        # Representation of physical fitness. Death at zero.
        self.life = life

        # Whether this cell is capable of dividing.
        self.can_divide = can_divide

        # Ticks until death of old age (not inherited).
        self.time_to_live = max_time_to_live

        # The total number of mutations that have been accumulated in this
        # cell's lineage.
        self.dynasty_mutations = 0

        # The number of members in this cell's lineage.
        self.generational_number = 1

        # The number of DNA errors this cell has accumulated in it's life time.
        self.lifetime_errors = 0

        self.excess_energy = 0
        self.new_errors = 0

        # Signal that it is time to begin division.
        self.time_to_divide = False

        # Whether this cell is signalling cell suicide.
        self.is_signaling_apoptosis = False

    def __repr__(self):
        return """Cell(dr=%s, mr=%s, err=%s, mut=%s,
                  L=%s, rep=%s, ts=%s, ttl=%s, g=%s)""" % (
            self.drug_resistance, self.mitosis_rate,
            self.new_errors, self.dynasty_mutations, self.life,
            self.repair_success, self.tumor_suppression, self.time_to_live,
            self.generational_number)

    def gain_energy(self):
        """
        Causes the cell to simulate the intake of food. Food is put
        into an excess energy reserve.
        """
        self.excess_energy = self.excess_energy + \
            max(normalvariate(
                Cell.AVERAGE_ENERGY_PER_TICK,
                Cell.AVERAGE_ENERGY_PER_TICK / 4.0), 0.0)

    def gain_life(self):
        """
        Repairs physical damage to the cell.
        Causes the cell to gain some life. The cell cannot go over 150 health.
        """
        self.life = min(self.life +
                        max(normalvariate(
                            Cell.AVERAGE_LIFE_PER_TICK,
                            Cell.AVERAGE_LIFE_PER_TICK / 4.0),
                            0.0),
                        150)

    def has_energy_to_divide(self):
        """
        Returns true if the cell has the energy to divide.
        """
        return self.excess_energy >= Cell.ENERGY_NEEDED_TO_DIVIDE

    def has_life_to_divide(self):
        """
        Returns true if the cell has the life to divide.
        """
        return self.life > Cell.LIFE_NEEDED_TO_DIVIDE

    def age(self, time_elapsed=1):
        """
        Causes the cell to age by the amount specified.
        """
        self.time_to_live = self.time_to_live - time_elapsed

        if(self.time_to_live <= 0):
            self.kill()

    def kill(self):
        """
        Sets the health of the cell to zero, which will trigger death.
        """
        self.life = 0

    def mutate_lethal(self):
        """
        Performs a lethal mutation, killing the cell.
        """
        self.kill()

    def mutate_non_lethal_bad(self):
        """
        Performs a non-lethal mutation that is harmful to the cell.
        The effect is random. Attributes that are inherited may be affected,
        along with attributes that are not.

        Non-lethal mutations have a very high chance of preventing the cell
        from dividing.
        """
        dice_roll = randint(1, 1000)

        if(dice_roll < 250):
            self.drug_resistance = max(
                self.drug_resistance - randint(1, 15), 0)
        elif(dice_roll < 500):
            self.mitosis_rate = self.mitosis_rate + randint(1, 2)
        elif(dice_roll < 750):
            self.life = max(self.life - randint(1, int(self.life) + 1), 0)
        elif(dice_roll < 900):
            self.repair_success = max(
                self.repair_success - uniform(0.0001, 0.0050), 0)
        elif(dice_roll < 960):
            self.max_time_to_live = max(
                self.max_time_to_live - randint(1, 3), 1)
        elif(dice_roll < 999):
            self.can_divide = False
        else:
            self.tumor_suppression = max(
                self.tumor_suppression - uniform(0.01, 1.0), 0)

    def mutate_neutral(self):
        """
        Performs a mutation that has no effect.
        """
        pass

    def mutate_good(self):
        """
        Performs a mutation that has a beneficial effect on the cell. This
        effect may affect inherited attributes or non-inherited attributes.
        """
        dice_roll = randint(1, 1000)

        if(dice_roll < 250):
            self.drug_resistance = self.drug_resistance + randint(1, 15)
        elif(dice_roll < 500):
            self.mitosis_rate = max(self.mitosis_rate - randint(1, 2), 1)
        elif(dice_roll < 750):
            self.life = min(max(self.life + randint(1, 15), 0), 150)
        elif(dice_roll < 810):
            self.max_time_to_live = max(
                self.max_time_to_live + randint(1, 2), 0)
        elif(dice_roll < 999):
            self.repair_success = min(
                max(self.repair_success + uniform(0.0001, 0.0050), 0.0),
                0.99999)
        else:
            self.tumor_suppression = min(
                self.tumor_suppression + uniform(0.01, 0.3), 2.0)

    def damage(self, multiplier=1.0):
        """
        Increases the number of DNA errors in the cell.
        """
        errors_after_mult = Cell.ERRORS_PER_TICK * multiplier
        dna_errors_max = int(
            max(normalvariate(errors_after_mult,
                              errors_after_mult / 4), 0))

        self.lifetime_errors = self.lifetime_errors + dna_errors_max
        self.new_errors += dna_errors_max

    def damage_from_division(self):
        """
        Increases the number of DNA errors as a result of division.
        This is more error prone than random environmental damage.
        """
        self.damage(4.0)

    def repair(self):
        """
        Attempts to repair errors in the cell. Simulating each repair
        would be computationally expensive, so we use statistical
        approximation.
        """

        # Determine the number of errors that exist after a repair.
        expected_errors = (1.0 - self.repair_success) * self.new_errors
        self.new_errors = int(
            max(normalvariate(expected_errors, expected_errors / 4), 0.0))

        # There need to be errors and the tumor supressor gene needs to be
        # active in order for repairs to proceed.
        if(self.new_errors > 0 and
           uniform(0.0, 1.0) <= (self.tumor_suppression ** self.new_errors)):
            dice_roll = randint(1, 1000)

            if(dice_roll < 900):
                # Attempt to repair for an additional tick
                self.can_divide = False
            else:
                # Kill self, cell is damaged beyond repair
                self.is_signaling_apoptosis = True
        else:
            # There are either no errors or tumor suppression failed
            self.can_divide = True

    def mutate(self):
        """
        Randomly mutates the genome of the cell. Mutations may be lethal,
        harmful, helpful, or do nothing.

        The number of mutations depends on the number of unrepaired DNA errors.
        """

        # Vary the number of mutations
        dna_mutations_expected_value = self.new_errors
        dna_mutations = int(max(normalvariate(
            dna_mutations_expected_value,
            dna_mutations_expected_value / 4), 0.0))

        self.dynasty_mutations = self.dynasty_mutations + dna_mutations

        for x in range(0, dna_mutations):
            dice_roll = randint(1, 1000)

            if(dice_roll < Cell.MUTATION_LETHAL_PER_1000):
                # lethal result
                self.mutate_lethal()
            elif(dice_roll < Cell.MUTATION_LETHAL_PER_1000 +
                 Cell.MUTATION_NON_LETHAL_BAD_PER_1000):
                # non-lethal, but harmful result
                self.mutate_non_lethal_bad()
            elif(dice_roll < Cell.MUTATION_LETHAL_PER_1000 +
                 Cell.MUTATION_NON_LETHAL_BAD_PER_1000 +
                 Cell.MUTATION_NEUTRAL_PER_1000):
                # neutral result
                self.mutate_neutral()
            elif(dice_roll < Cell.MUTATION_LETHAL_PER_1000 +
                 Cell.MUTATION_NON_LETHAL_BAD_PER_1000 +
                 Cell.MUTATION_NEUTRAL_PER_1000 +
                 Cell.MUTATION_ADVANTAGEOUS_PER_1000):
                # good result
                self.mutate_good()

        # Prior mutations are now considered normal.
        self.new_errors = 0

    def divide(self):
        """
        Divides the cell so that two daughter cells exist afterwards.
        """

        # The cell requires a store of energy and must be fit enough to divide.
        # This acts as strong selection against mutation since most mutations
        # affect fitness in a negative manner.  Without this, cells tend to go
        # wild.
        if(self.has_energy_to_divide() and self.has_life_to_divide()):
            # Reduce energy and life in order to divide. The life goes
            # to the new cell and the energy is lost.
            self.excess_energy = self.excess_energy - \
                Cell.ENERGY_NEEDED_TO_DIVIDE
            self.life = self.life - Cell.LIFE_NEEDED_TO_DIVIDE

            # Create the new cell and inherit attributes
            new_cell = Cell(drug_resistance=self.drug_resistance,
                            repair_success=self.repair_success,
                            max_time_to_live=self.max_time_to_live,
                            tumor_suppression=self.tumor_suppression,
                            can_divide=True)

            # Set the lineage information for the new cell
            new_cell.generational_number = self.generational_number + 1
            new_cell.dynasty_mutations = self.dynasty_mutations

            # Immediately damage both cells from the division
            new_cell.damage_from_division()
            self.damage_from_division()

            return new_cell
        else:
            return None