import GA_BPP as genetic_algorithm
import pandas
import os
import time
import concurrent.futures
import sklearn.ensemble

def main():
    optimal_fitnesses, optimal_generations, execution_times, run_order, parameters_list, count = [], [] ,[], [], [], 0 # lists used to hold results adn to hold different sets of parameters
    parameters_sheet = pandas.read_csv(os.path.dirname(os.path.abspath(__file__)) + '/DOE Parameters.csv') # open up excel sheet
    runs = list(parameters_sheet['Run Order']) # get the run order

    for run in runs: # get a list of the different parameter sets to run for the DOE
        parameters = {'run order': run, 'bin length':50, 'fitness operator':'area above', 'max generations':10000, 'export results':'yes', 'print results':'no', 'plot bin':'yes', 'plot results':'yes',\
        
        'mutation operator':'insertion', 'crossover operator':'1-point', 'selection operator':'elitist', 'population size':500, 'termination factor':50, 'min generations': 250} #, 'cleaning frequency':10001}
        parameters['packing algorithm'] = list(parameters_sheet['Packing'])[run - 1]
        parameters['gap fill'] = list(parameters_sheet['Gap'])[run - 1]
        parameters['flip'] = list(parameters_sheet['Flip'])[run - 1]
        parameters['sort'] = list(parameters_sheet['Sort'])[run - 1]

        #'packing algorithm':______, 'gap fill':______, 'flip':______, 'sort':______}
        #parameters['mutation operator'] = list(parameters_sheet['Mutation'])[run - 1]
        #parameters['crossover operator'] = list(parameters_sheet['Crossover'])[run - 1]
        #parameters['selection operator'] = list(parameters_sheet['Selection'])[run -1]
        #parameters['population size'] = list(parameters_sheet['Population'])[run - 1]
        #parameters['termination factor'] = list(parameters_sheet['Termination'])[run - 1]
        #parameters['min generation'] = list(parameters_sheet['Generations'])[run - 1]
        #parameters['cleaning frequency'] = list(parameters_sheet['Cleaning'])[run - 1]
         
        parameters['boxes initialization'] = list(parameters_sheet['Problem Set'])[run - 1]
        parameters_list.append(parameters)

    with concurrent.futures.ProcessPoolExecutor() as executor: # run concurrently the runs
        results = [executor.submit(genetic_algorithm.main, parameters) for parameters in parameters_list]
        for run in concurrent.futures.as_completed(results): # print the results as they are finshed
            count = count + 1

            print('****************************************************************************************')
            print('run', count)
            print('optimal:', run.result()[0], ' generation:', run.result()[1], ' execution time:', run.result()[2],  'run order:', run.result()[3], '\n')

            # optimal_fitnesses.append(run.result()[0]) # record the results
            # optimal_generations.append(run.result()[1])
            # execution_times.append(run.result()[2])
            # run_order.append(run.result()[3])

    # df1 = pandas.DataFrame({'Optimal': optimal_fitnesses}) # create dataframes to hold the results
    # df2 = pandas.DataFrame({'Generation': optimal_generations})
    # df3 = pandas.DataFrame({'Execution Time': execution_times})
    # df4 = pandas.DataFrame({'Run Order': run_order})
    # writer = pandas.ExcelWriter(os.path.dirname(__file__) + '/DOE_results.xlsx', engine='xlsxwriter') # Create a Pandas Excel writer using XlsxWriter as the engine.
    # df4.to_excel(writer, sheet_name='Sheet1', startcol=3)
    # df3.to_excel(writer, sheet_name='Sheet1', startcol=2)
    # df2.to_excel(writer, sheet_name='Sheet1', startcol=1) 
    # df1.to_excel(writer, sheet_name='Sheet1', startcol=0) # Position the dataframes in the worksheet.
    # writer.save()


import sys, inspect
def print_classes():
    for name, obj in inspect.getmembers(sys.modules['sklearn.ensemble.__stacking']):
        if inspect.isclass(obj):
            print('CLASS: ', obj)

if __name__ == '__main__':
    start = time.time()
   # main()
    print_classes()
    print('\n ---TOTAL EXECUTION TIME: {}--- \n'.format(time.time() - start)) # get the total time to run the program