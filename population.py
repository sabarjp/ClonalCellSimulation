from random import normalvariate
from copy import deepcopy


class Population:
    """
    Represents a population of cells. The population can be iterated over to
    perform the simulation.
    """

    # The group of the cells.
    cell_collection = []
    current_tick = 1

    def __init__(self, inital_cell):
        # Add some clonal seed cells.
        for x in range(0, 10):
            self.cell_collection.append(deepcopy(inital_cell))

    def poison(self, amount_of_poison):
        """
        Applies poison to the population of cells in order to kill them. Cells
        which are resistant may not die.
        """
        for cell in self.cell_collection:
            # Vary the strength of the poison
            base_damage = 100 * normalvariate(1, 0.12)
            poison_strength_after_resistance = (
                amount_of_poison * 1.0) - (cell.drug_resistance *
                                           normalvariate(1, 0.12))

            # Determine the effectiveness of the poison
            if(poison_strength_after_resistance > 0):
                effectiveness = max(
                    (poison_strength_after_resistance / 2.0), 0.0)
            else:
                effectiveness = 0

            # print 'poison: bd:', base_damage, ' str: ',
            # poison_strength_after_resistance, ' effect: ', effectiveness, ' =
            # ', base_damage * effectiveness

            # Apply the poison to the cell
            cell.life = cell.life - (base_damage * effectiveness)

    def tick(self):
        """
        Simulates one tick of time over the whole collection.
        """

        # The cells that will exist in the next tick.
        new_cell_collection = []

        # Kill off anything that died.
        self.cell_collection[:] = [
            x for x in self.cell_collection if x.life > 0
            and not(x.is_signaling_apoptosis)]

        # Perform simulation.
        for cell in self.cell_collection:
            # Eat so the cell can divide
            cell.gain_energy()

            # Repair physical damage
            cell.gain_life()

            # Accumulate DNA damage from environment
            cell.damage(0.5)

            # Population limiter applies here
            if(len(self.cell_collection) < 100):
                # Time for dividing
                if(self.current_tick % cell.mitosis_rate == 0
                   and cell.has_energy_to_divide()
                   and cell.has_life_to_divide()):
                    cell.time_to_divide = True

                # Start repair and divide process
                if(cell.time_to_divide):
                    # Repair before dividing
                    cell.repair()

                    if(cell.can_divide):
                        new_cell = cell.divide()

                        if(new_cell):
                            new_cell_collection.append(new_cell)

            # Age the cell. Old cells will die.
            cell.age()

        self.cell_collection.extend(new_cell_collection)

        # Kill anything that died this tick
        self.cell_collection[:] = [
            x for x in self.cell_collection if x.life > 0
            and not(x.is_signaling_apoptosis)]

        self.current_tick = self.current_tick + 1

    def __str__(self):
        strbuf = []
        for cell in self.cell_collection:
            strbuf.append(cell.__repr__())
            strbuf.append('\n')
        return ''.join(strbuf)
