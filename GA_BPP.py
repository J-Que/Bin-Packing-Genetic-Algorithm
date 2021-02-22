import datetime
import json
import matplotlib.pyplot as plt
import os
import pandas
import random
import time
    
class Box(): 
    def __init__(self, number, height, length, area=0, left=0, top=0, gap=False): # box attrinutes
        self.number = number
        self.height = height
        self.length = length
        self.area = area
        self.left = left
        self.top = top
        self.gap = gap

    def __eq__(self, other): return (self.__class__ == other.__class__ and self.number == other.number) # determine if two boxes are equal

    def __hash__(self): return hash(self.number) # get the has value of the boxes number

class Bin(): 
    def __init__(self, length): self.length = length #set the length of the bin

    def define_limit(self, boxes): self.limit = int(sum([box.area for box in boxes])/self.length) # define the limit of the bin height

    def plot(self, phenotype,  title, gap):
        _, gantt = plt.subplots()
        gantt.set_title('Optimal Packing ' + str(phenotype.fitness), fontweight='bold')
        gantt.set_ylim(0, phenotype.height)
        gantt.set_xlim(0, self.length)
        gantt.set_xlabel('Bin Length', fontweight='bold')
        gantt.set_ylabel('Bin Height', fontweight='bold')
        gantt.set_yticks(list(range(0, phenotype.height, 5)))
        gantt.set_xticks(list(range(0, self.length, 5)))

        if gap == 'no':
            colors = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
            for box in phenotype.genome:
                gantt.broken_barh([(box.left, box.length)], (box.top - box.height, box.height), edgecolor='black', facecolors=(random.choice(colors)))
                gantt.text(box.left + box.length/2 - .25, box.top - box.height + box.height/2 - .25, str(box.number), color='black', fontweight='bold')
        else:
            colors = ['tab:blue','tab:orange','tab:green', 'tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
            for box in phenotype.genome:
                if box.gap == False: gantt.broken_barh([(box.left, box.length)], (box.top - box.height, box.height), edgecolor='black', facecolors=(random.choice(colors)))
                else: gantt.broken_barh([(box.left, box.length)], (box.top - box.height, box.height), edgecolor='black', facecolors=('tab:red'))
                gantt.text(box.left + box.length/2 - .25, box.top - box.height + box.height/2 - .25, str(box.number), color='black', fontweight='bold')

        plt.savefig(os.path.dirname(__file__) + "/Plots/Bin Packed run" + str(title) + "optimal " + str(phenotype.fitness) + ".png")
        plt.show()
        gantt.cla()

class Genotype():
    def __init__(self, genome, generation, fitness=0, packed_height=0): # phenotype atttributes
        self.genome = genome
        self.generation = generation
        self.fitness = fitness
        self.height = packed_height

    def __lt__(self, other): return self.fitness < other.fitness

    def __eq__(self, other): return (self.__class__ == other.__class__ and self.genome == other.genome)

    def __hash__(self): return hash(tuple([box.number for box in self.genome]))

def load_boxes(problem_set, flip):
    df = pandas.read_csv(os.path.dirname(__file__) + '/Problem Sets.csv') # open the csv file
    nums, height, length = list(df['Number' + '_' + str(problem_set)]), list(df['Height' + '_' + str(problem_set)]), list(df['Length' + '_' + str(problem_set)]) # load the boxes data

    if flip == 'height': return [Box(nums[i], max(height[i], length[i]), min(height[i], length[i]), height[i] * length[i]) for i in range(len(nums))] # create the boxes
    elif flip == 'length': return [Box(nums[i], min(height[i], length[i]), max(height[i], length[i]), height[i] * length[i]) for i in range(len(nums))]
    else: return [Box(nums[i], height[i], length[i], height[i] * length[i]) for i in range(len(nums))]

def sort_boxes(boxes, sorting):
    if sorting == 'increasing height': boxes.sort(key=lambda box: box.height, reverse=False)
    elif sorting == 'decreasing height': boxes.sort(key=lambda box: box.height, reverse=True)
    elif sorting == 'increasing length': boxes.sort(key=lambda box: box.length, reverse=False)
    elif sorting == 'decreasing length': boxes.sort(key=lambda box: box.length, reverse=True)

def replace_duplicates(phenotype, boxes):
    missing, genome = list(set(boxes) - set([box for box in phenotype.genome])), []
    for box in phenotype.genome:
        if box not in genome: genome.append(box)
        else: genome.append(missing.pop(0))

    phenotype.genome = genome   
    return phenotype

def clean_population(parents, offsprings):
    cleaned_population = list(set(parents + offsprings))
    cleaned_population.sort(key=lambda x: x.fitness)
    if len(cleaned_population) < len(parents):
        for _ in range(len(parents) - len(cleaned_population.copy())):
            cleaned_population.append(min(cleaned_population))
    return  cleaned_population[:len(parents)]

def export_results(parameters, generation_fitnesses, optimal, time):
    genome = {}
    for box in optimal.genome: genome[box.number] = {'length':box.length, 'height':box.height, 'left':box.left, 'top':box.top}

    results = {'date':datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),\
               'run order':parameters['run order'],\
               'population size':parameters['population size'],\
               'max generations':parameters['max generations'],\
               'min generations':parameters['min generations'],\
               'termination factor':parameters['termination factor'],\
               'packing algorithm':parameters['packing algorithm'],\
               'crossover operator':parameters['crossover operator'],\
               'mutation operator':parameters['mutation operator'],\
               'selection operator':parameters['selection operator'],\
               'bin length':parameters['bin length'],\
               'flip':parameters['flip'],\
               'sort':parameters['sort'],\
               'gap fill':'no',\
               'cleaning frequency':'no',\
               'problem set':parameters['boxes initialization'],\
               'execution time':"%s seconds" % time,\
               'optimal fitness value':optimal.fitness,\
               'origin generation': optimal.generation,\
               'optimal sequence':genome,\
               'generational fitness values':generation_fitnesses}

    with open(os.path.dirname(__file__) + '/JSON/run ' + str(parameters['run order']) + '.json', 'w') as file: json.dump(results, file, indent=5)

def plot_results(optimal_fitnesses, title):
    line = plt.subplot()
    line.set_title('Fitness Value over Generations', fontweight='bold')
    line.set_xlabel('Generation', fontweight='bold') 
    line.set_ylabel('Fitness Value', fontweight='bold')

    plt.plot(range(1, len(optimal_fitnesses) + 1), optimal_fitnesses)
    plt.savefig(os.path.dirname(__file__) + "/Plots/Fitness_Over_Generations_" + str(title) + ".png")
    plt.show()
    plt.cla()

def local_parameters():
    parameters = {'run order': 'test'}
    parameters['population size'] = 10
    parameters['max generations'] = 100
    parameters['min generations'] = 20
    parameters['termination factor'] = 5
    parameters['packing algorithm'] = 'bottom lower'
    parameters['fitness operator'] = 'area above'
    parameters['crossover operator'] = '1-point'
    parameters['mutation operator'] = '2-point swap'
    parameters['selection operator'] = 'elitist'
    parameters['flip'] = 'height'
    parameters['sort'] = 'decreasing height'
    parameters['gap fill'] = 'yes'
    parameters['cleaning frequency'] = None
    parameters['bin length'] = 50
    parameters['boxes initialization'] = 7
    parameters['export results'] = 'no'
    parameters['print results'] = 'yes'
    parameters['plot results'] = 'yes'
    parameters['plot bin'] = 'yes'
    return parameters

def main(parameters):
    start = time.time()

    if parameters['packing algorithm'] == 'bottom left' and parameters['gap fill'] == 'no':
        def pack(phenotype, bin):
            box, row_length, packing_height, current_row, lower_row = 0, 0, 0, [], [Box('initial', 1, bin.length, 0, 0, 0)]
            while box < len(phenotype.genome):
                if row_length + phenotype.genome[box].length <= bin.length:
                    for _ in range(len(lower_row)):
                        if row_length + phenotype.genome[box].length <= lower_row[0].left + lower_row[0].length:
                            phenotype.genome[box].left, phenotype.genome[box].top, row_length, box = row_length, packing_height + phenotype.genome[box].height, row_length + phenotype.genome[box].length, box + 1
                            current_row.append(phenotype.genome[box - 1])
                            break
                        elif row_length < lower_row[0].left + lower_row[0].length:
                            lower_row.pop(0)
                            packing_height = max(packing_height, lower_row[0].top)
                        else:
                            lower_row.pop(0)
                            packing_height = lower_row[0].top
                else:
                    current_row.append(Box('space filler', 0, lower_row[0].left + lower_row[0].length - row_length, 0, row_length, lower_row[0].top))
                    lower_row, current_row = current_row + lower_row[1:], []
                    row_length, packing_height = 0, lower_row[0].top     
            phenotype.height = max([i.top for i in phenotype.genome])
            return phenotype
    elif parameters['packing algorithm'] == 'bottom left' and parameters['gap fill'] == 'yes':
        def pack(phenotype, bin):
            box, row_length, packing_height, current_row, lower_row, original_sequence = 0, 0, 0, [], [Box('initial', 1, bin.length, 0, 0, 0)], phenotype.genome.copy()
            while box < len(phenotype.genome):
                if row_length + phenotype.genome[box].length <= bin.length:
                    for _ in range(len(lower_row)):
                        if row_length + phenotype.genome[box].length <= lower_row[0].left + lower_row[0].length:
                            phenotype.genome[box].left, phenotype.genome[box].top, row_length, box = row_length, packing_height + phenotype.genome[box].height, row_length + phenotype.genome[box].length, box + 1
                            current_row.append(phenotype.genome[box - 1])
                            break
                        elif row_length < lower_row[0].left + lower_row[0].length:
                            lower_row.pop(0)
                            packing_height = max(packing_height, lower_row[0].top)
                        else:
                            lower_row.pop(0)
                            packing_height = lower_row[0].top
                    packing_height = lower_row[0].top
                else:
                    while packing_height != None:
                        if row_length < bin.length:    
                            fill_area, gap_box, packing_height = 0, None, lower_row[0].top
                            for i in phenotype.genome[box:]:
                                if i.area > fill_area and i.length <= bin.length - row_length:
                                    fill_area, gap_box = i.area, phenotype.genome.index(i)
                            if gap_box != None:                    
                                for _ in range(len(lower_row)):
                                    if row_length + phenotype.genome[gap_box].length <= lower_row[0].left + lower_row[0].length:
                                        phenotype.genome[gap_box].top, phenotype.genome[gap_box].left = packing_height + phenotype.genome[gap_box].height, row_length
                                        box, row_length, phenotype.genome[gap_box].gap = box + 1, row_length + phenotype.genome[gap_box].length, True
                                        current_row.append(phenotype.genome[gap_box])
                                        phenotype.genome.insert(box - 1, phenotype.genome.pop(gap_box))
                                        break
                                    elif row_length < lower_row[0].left + lower_row[0].length:
                                        lower_row.pop(0)
                                        packing_height = max(packing_height, lower_row[0].top)
                                    else:
                                        lower_row.pop(0)
                                        packing_height = lower_row[0].top
                            else:
                                packing_height = None
                        else:
                            packing_height = None

                    current_row.append(Box('space filler', 0, lower_row[0].left + lower_row[0].length - row_length, 0, row_length, lower_row[0].top))
                    lower_row, current_row = current_row + lower_row[1:], []
                    row_length, packing_height = 0, lower_row[0].top     
            
            phenotype.height, phenotype.genome = max([i.top for i in phenotype.genome]), original_sequence
            return phenotype
    elif parameters['packing algorithm'] == 'bottom lower' and parameters['gap fill'] == 'no':
        def pack(phenotype, bin):
            packed, row_length, current_row, lower_row = 0, 0, [], [Box('initial', 0, bin.length, 0, 0, 0)]
            while packed < len(phenotype.genome):
                left_corner, right_corner, packing_height = lower_row[0].top, lower_row[-1].top, min(lower_row[0].top, lower_row[-1].top) 
                if left_corner <= right_corner:
                    for box in phenotype.genome[packed:]:
                        packing_height = lower_row[0].top
                        if row_length + box.length <= bin.length:
                            for _ in range(len(lower_row)):
                                if row_length + box.length <= lower_row[0].left + lower_row[0].length:
                                    box.left, box.top, row_length, packed = row_length, packing_height + box.height, row_length + box.length, packed + 1
                                    current_row.append(box)
                                    break
                                elif row_length < lower_row[0].left + lower_row[0].length:
                                    lower_row.pop(0)
                                    packing_height = max(packing_height, lower_row[0].top)
                                else:
                                    lower_row.pop(0)
                                    packing_height = lower_row[0].top
                        else:
                            current_row.append(Box('space filler ' + str(lower_row[0].number), lower_row[0].height, lower_row[0].left + lower_row[0].length - row_length, 0, row_length, lower_row[0].top))
                            lower_row, current_row, row_length = current_row + lower_row[1:], [], 0
                            break
                else:
                    for box in phenotype.genome[packed:]:
                        packing_height = lower_row[-1].top
                        if row_length + box.length <= bin.length:
                            for _ in reversed(range(len(lower_row))):
                                if bin.length - row_length - box.length >= lower_row[-1].left:
                                    box.top, box.left, row_length, packed = packing_height + box.height, bin.length - row_length - box.length, row_length + box.length, packed + 1
                                    current_row.insert(0, box)
                                    break
                                elif bin.length - row_length > lower_row[-1].left:
                                    lower_row.pop(-1)
                                    packing_height = max(packing_height, lower_row[-1].top)
                                else:
                                    lower_row.pop(-1)
                                    packing_height = lower_row[-1].top
                        else:
                            current_row.insert(0, Box('space filler ' + str(lower_row[-1]), lower_row[-1].height, bin.length - row_length - lower_row[-1].left, 0, lower_row[-1].left, lower_row[0].top))
                            lower_row, current_row, row_length = lower_row[:-1] + current_row, [], 0
                            break 

            phenotype.height = max([i.top for i in phenotype.genome])
            return phenotype
    elif parameters['packing algorithm'] == 'bottom lower' and parameters['gap fill'] == 'yes':
        def pack(phenotype, bin):
            #phenotype.height = 60
            packed, row_length, current_row, lower_row, original_sequence = 0, 0, [], [Box('initial', 0, bin.length, 0, 0, 0)], phenotype.genome.copy()
            while packed < len(phenotype.genome):
                left_corner, right_corner, packing_height = lower_row[0].top, lower_row[-1].top, min(lower_row[0].top, lower_row[-1].top) 
                if left_corner <= right_corner:
                    for box in phenotype.genome[packed:]:
                        packing_height = lower_row[0].top
                        if row_length + box.length <= bin.length:
                            for _ in range(len(lower_row)):
                                if row_length + box.length <= lower_row[0].left + lower_row[0].length:
                                    box.left, box.top, row_length, packed = row_length, packing_height + box.height, row_length + box.length, packed + 1
                                    #bin.plot(phenotype, 'test', 'yes')
                                    current_row.append(box)
                                    break
                                elif row_length < lower_row[0].left + lower_row[0].length:
                                    lower_row.pop(0)
                                    packing_height = max(packing_height, lower_row[0].top)
                                else:
                                    lower_row.pop(0)
                                    packing_height = lower_row[0].top
                        else:
                            while packing_height != None:
                                if row_length < bin.length:    
                                    fill_area, gap_box, packing_height = 0, None, lower_row[0].top
                                    for i in phenotype.genome[packed:]:
                                        if i.area > fill_area and i.length <= bin.length - row_length:
                                            fill_area, gap_box = i.area, phenotype.genome.index(i)
                                    if gap_box != None:                    
                                        for _ in range(len(lower_row)):
                                            if row_length + phenotype.genome[gap_box].length <= lower_row[0].left + lower_row[0].length:
                                                phenotype.genome[gap_box].top, phenotype.genome[gap_box].left = packing_height + phenotype.genome[gap_box].height, row_length
                                                packed, row_length, phenotype.genome[gap_box].gap = packed + 1, row_length + phenotype.genome[gap_box].length, True
                                                #.plot(phenotype, 'test', 'yes')
                                                current_row.append(phenotype.genome[gap_box])
                                                break
                                            elif row_length < lower_row[0].left + lower_row[0].length:
                                                lower_row.pop(0)
                                                packing_height = max(packing_height, lower_row[0].top)
                                            else:
                                                lower_row.pop(0)
                                                packing_height = lower_row[0].top 
                                        phenotype.genome.insert(packed - 1, phenotype.genome.pop(gap_box))
                                    else:
                                        packing_height = None
                                else:
                                    packing_height = None
                            current_row.append(Box('space filler ' + str(lower_row[0].number), lower_row[0].height, lower_row[0].left + lower_row[0].length - row_length, 0, row_length, lower_row[0].top))
                            lower_row, current_row, row_length = current_row + lower_row[1:], [], 0
                            break
                else:
                    for box in phenotype.genome[packed:]:
                        packing_height = lower_row[-1].top
                        if row_length + box.length <= bin.length:
                            for _ in reversed(range(len(lower_row))):
                                if bin.length - row_length - box.length >= lower_row[-1].left:
                                    box.top, box.left, row_length, packed = packing_height + box.height, bin.length - row_length - box.length, row_length + box.length, packed + 1
                                    #bin.plot(phenotype, 'test', 'yes')
                                    current_row.insert(0, box)
                                    break
                                elif bin.length - row_length > lower_row[-1].left:
                                    lower_row.pop(-1)
                                    packing_height = max(packing_height, lower_row[-1].top)
                                else:
                                    lower_row.pop(-1)
                                    packing_height = lower_row[-1].top
                        else:
                            while packing_height != None:   
                                if row_length < bin.length:    
                                    fill_area, gap_box, packing_height = 0, None, lower_row[-1].top
                                    for i in phenotype.genome[packed:]:
                                        if i.area > fill_area and i.length <= bin.length - row_length:
                                            fill_area, gap_box = i.area, phenotype.genome.index(i)
                                    if gap_box != None:                    
                                        for _ in reversed(range(len(lower_row))):
                                            if bin.length - row_length - phenotype.genome[gap_box].length >= lower_row[-1].left:
                                                phenotype.genome[gap_box].top, phenotype.genome[gap_box].left = packing_height + phenotype.genome[gap_box].height, bin.length - row_length - phenotype.genome[gap_box].length, 
                                                packed, row_length, phenotype.genome[gap_box].gap = packed + 1, row_length + phenotype.genome[gap_box].length, True
                                                #bin.plot(phenotype, 'test', 'yes')
                                                current_row.insert(0, phenotype.genome[gap_box])
                                                break
                                            elif bin.length - row_length > lower_row[-1].left:
                                                lower_row.pop(-1)
                                                packing_height = max(packing_height, lower_row[-1].top)
                                            else:
                                                lower_row.pop(-1)
                                                packing_height = lower_row[-1].top 
                                        phenotype.genome.insert(packed - 1, phenotype.genome.pop(gap_box))
                                    else:
                                        packing_height = None
                                else:
                                    packing_height = None
                            current_row.insert(0, Box('space filler ' + str(lower_row[-1]), lower_row[-1].height, bin.length - row_length - lower_row[-1].left, 0, lower_row[-1].left, lower_row[0].top))
                            lower_row, current_row, row_length = lower_row[:-1] + current_row, [], 0
                            break 

            phenotype.height, phenotype.genome = max([i.top for i in phenotype.genome]), original_sequence
            return phenotype
    
    if parameters['fitness operator'] == 'area above':
        def fitness(phenotype, bin):
            area_above = 0
            for box in reversed(phenotype.genome[int(len(phenotype.genome)/2):]):
                if box.top > bin.limit:
                    if box.top - box.height < bin.limit:
                        x  = area_above
                        area_above = area_above + ((box.top - bin.limit) * box.length)
                    else: 
                        area_above = area_above + box.area

            return area_above
    if parameters['fitness operator'] == 'packed height':
        def fitness(phenotype, bin):
            return phenotype.height
    
    if parameters['crossover operator'] == '1-point':
        def crossover(parents, boxes, generation):
            offsprings = []
            random.shuffle(parents)
            for _ in range(int(len(parents)/2)):
                parent1, parent2 = parents.pop(), parents.pop()
                crosspoint = random.randint(1, len(boxes) - 2)

                offspring1 = Genotype(parent1.genome[:crosspoint] + parent2.genome[crosspoint:], generation)
                offspring2 = Genotype(parent2.genome[:crosspoint] + parent1.genome[crosspoint:], generation)

                offsprings.append(replace_duplicates(offspring1, boxes))
                offsprings.append(replace_duplicates(offspring2, boxes))
            
            return offsprings
    elif parameters['crossover operator'] == '2-point':
        def crossover(parents, boxes, generation):
            offsprings = []
            random.shuffle(parents)
            for _ in range(int(len(parents)/2)):
                parent1, parent2 = parents.pop(), parents.pop()
                crosspoint1, crosspoint2 = random.randint(1, len(boxes) - 2), random.randint(1, len(boxes) - 2)

                offspring1 = Genotype(parent1.genome[:min(crosspoint1, crosspoint2)] + parent2.genome[min(crosspoint1, crosspoint2):max(crosspoint1, crosspoint2)] + parent1.genome[max(crosspoint1, crosspoint2):], generation)
                offspring2 = Genotype(parent2.genome[:min(crosspoint1, crosspoint2)] + parent1.genome[min(crosspoint1, crosspoint2):max(crosspoint1, crosspoint2)] + parent2.genome[max(crosspoint1, crosspoint2):], generation)

                offsprings.append(replace_duplicates(offspring1, boxes))
                offsprings.append(replace_duplicates(offspring2, boxes))

            return offsprings
    elif parameters['crossover operator'] == 'uniform':
        def crossover(parents, boxes, generation):
            offsprings = []
            random.shuffle(parents)
            for _ in range(int(len(parents)/2)):
                parent1, parent2 =  parents.pop(), parents.pop()
                offspring1, offspring2 = Genotype([],generation), Genotype([], generation)

                for box in range(len(parent1.genome)):
                    bit = [parent1.genome[box], parent2.genome[box]]

                    offspring1.genome.append(bit.pop(random.choice([0, 1]))) 
                    offspring2.genome.append(bit[0])

                offsprings.append(replace_duplicates(offspring1, boxes))
                offsprings.append(replace_duplicates(offspring2, boxes))

            return offsprings

    if parameters['mutation operator'] == '2-point swap':
        def mutate(offsprings):
            for phenotype in offsprings:
                a, b = random.randint(0, len(phenotype.genome) - 1), random.randint(0, len(phenotype.genome) - 1) 
                phenotype.genome[a], phenotype.genome[b] = phenotype.genome[b], phenotype.genome[a]
            return offsprings
    elif parameters['mutation operator'] == 'scramble':
        def mutate(offsprings):
            scramble_out = int(len(offsprings[0].genome)/10)
            for phenotype in offsprings:
                scramble_point = random.randint(0, len(phenotype.genome) - scramble_out)
                scramble_subset = phenotype.genome[scramble_point:scramble_point + scramble_out]
                random.shuffle(scramble_subset)
                phenotype.genome[scramble_point:scramble_point + scramble_out] = scramble_subset

            return offsprings
    elif parameters['mutation operator'] == 'insertion':
        def mutate(offsprings):
            for phenotype in offsprings:
                phenotype.genome.insert(random.randint(0, len(phenotype.genome)), phenotype.genome.pop(random.randint(0, len(phenotype.genome) - 1)))
            return offsprings

    if parameters['selection operator'] == 'elitist':
        def select(population):
            population.sort(key=lambda x: x.fitness)
            return population[:int(len(population)/2)]
    elif parameters['selection operator'] == 'tournament':
        def select(population):
            selection = []
            random.shuffle(population)
            while len(population) > 0:
                phenotype1, phenotype2 = population.pop(), population.pop()
                selection.append(min(phenotype1, phenotype2))

            return selection
    elif parameters['selection operator'] == 'roulette': 
        def select(population):
            sum_of_fitness, weights = 0, []
            for phenotype in population:
                sum_of_fitness = sum_of_fitness + phenotype.fitness
                weights.append(sum_of_fitness/phenotype.fitness)
            return random.choices(population, weights=weights, k=int(len(population)/2))

    if parameters['cleaning frequency'] == None:
        def clean_and_select(parents, offsprings, generation, frequency):
            return select(parents + offsprings)
    else:
        def clean_and_select(parents, offsprings, generation, frequency):
            if generation % frequency == 0:
                return clean_population(parents, offsprings)
            else:
                return select(parents + offsprings)
    
    boxes = load_boxes(parameters['boxes initialization'], parameters['flip'])
    sort_boxes(boxes, parameters['sort'])
    
    bin = Bin(parameters['bin length'])
    bin.define_limit(boxes)
    
    parent = pack(Genotype(boxes.copy(), 0), bin)
    parent.fitness = fitness(parent, bin)
    
    parents = [Genotype(boxes.copy(), 0, parent.fitness) for i in range(parameters['population size'])]

    generation, termination_counter, last_optimal = 0, 0, parent.fitness
    optimal_fitnesses, generation_fitnesses = [], {'Generation 0':[i.fitness for i in parents]}
 
    while (termination_counter < parameters['termination factor'] and generation < parameters['max generations']) or generation < parameters['min generations']:
        generation += 1

        offsprings = crossover(parents.copy(), boxes, generation)
        offsprings = mutate(offsprings)
        for phenotype in offsprings:
            phenotype = pack(phenotype, bin)
            phenotype.fitness = fitness(phenotype, bin)

        parents = clean_and_select(parents, offsprings, generation, parameters['cleaning frequency'])
        optimal = min(parents)

        generation_fitnesses.update({'Generation ' + str(generation):[i.fitness for i in offsprings]})        
        optimal_fitnesses.append(optimal.fitness)

        if last_optimal == optimal.fitness:
            termination_counter = termination_counter + 1
        else:
            termination_counter, last_optimal = 0, optimal.fitness

    for box in optimal.genome: box.gap = False
    optimal = pack(optimal, bin)
    optimal.fitness = fitness(optimal, bin)
    end = time.time() - start

    if parameters['export results'] == 'yes':
        export_results(parameters, generation_fitnesses, optimal, end)
    if parameters['print results'] == 'yes':
        print('\n******************************************************************************************')
        print('Optimal Phenotype', '\nFitness Value: ', optimal.fitness, '\nGeneration', optimal.generation,'\nSequence:', [i.number for i in optimal.genome], '\n')
        print("---Runtime:  %s seconds ---" % end , '\n')
    if parameters['plot bin'] == 'yes':
        bin.plot(optimal, parameters['run order'], parameters['gap fill'])
    if parameters['plot results'] == 'yes': 
        plot_results(optimal_fitnesses, parameters['run order'])

    return [optimal.fitness, optimal.generation, end, parameters['run order']]

if __name__ == '__main__':
    main(local_parameters())