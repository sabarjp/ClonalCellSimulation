from population import Population
from cell import Cell


# Create population for the simulation
p = Population(Cell(drug_resistance=2, can_divide=True))

# Start loop
while True:
    action = raw_input('Enter action (tick/kill/quit): ')

    if(action == 'tick'):
        number_of_ticks = int(raw_input('Enter number of ticks: '))

        for x in range(number_of_ticks):
            p.tick()

        print '---'
        print p
    elif(action == 'kill'):
        amount_of_poison = int(raw_input('Enter amount of poison: '))

        p.poison(amount_of_poison)
        p.tick()

        print '---'
        print p
    elif(action == 'quit'):
        break
    else:
        print 'Unknown command: ', action
