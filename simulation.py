from queue import Queue, PriorityQueue, Full, Empty
import random
from milestone2 import RandomNumberGenerator
import statistics 
import matplotlib.pyplot as plt
import numpy as np


#GREEN: event added to the FEL
#BLUE: is a buffer insertion
#YELLOW: component/product ready to be consumed
#RED means the inspector/workstation is working / blocked
class bcolors:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


# define FEL and global clock
FEL = PriorityQueue()
_Clock = 0.0

# define random number generator
rng = RandomNumberGenerator(seed=12345)

#statistics 
current_iteration = 0 
components_in_system = 0 
components_in_workstation = {'1': [], '2': [], '3': []}
component_times_in_system = {'total': [], '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [],
                              '8': [], '9': [], '10': [], '11': [], '12': [],
                               '13': [], '14': [], '15': [], '16': [], '17': [],
                                '18': [], '19': [], '20': [], '21': [], '22': [],
                                 '23': [], '24': [], '25': [], '26': [], '27': [],
                               '28': [], '29': [], '30': [], '31': [], '32': [],
                                '33': [], '34': [], '35': [], '36': [], '37': []}

component_pass_through_times = 0
individual_run_buffer_occupancies = {}
components_passed_through_system = 0 

# define product list to track how many products were created
product_list = {'P1': 0, 'P2': 0, 'P3': 0}



class Product:
    def __init__(self, components):
        #determine product type based on components provided
        self.components = components

        if len(components) == 1 and components[0].name == 'C1':
            self.name = 'P1'
        elif len(components) == 2 and components[0].name == 'C1':
            if components[1].name == 'C2':
                self.name = 'P2'
            elif components[1].name == 'C3':
                self.name = 'P3'
        else:
            raise Exception('invalid product')  # or raise an error if the input is invalid
        
        self._ready = False
    
    # signals the component is finished inspecting and can be passed to workstation
    def mark_as_ready(self):
        self._ready = True

    # returns true if the component passed inspection
    def is_ready(self) -> bool:
        return self._ready

    def __repr__(self):
        return self.name

class Component:
    def __init__(self, name):

        self.name = name
        self._ready = False

        # statistics
        self._time_entered_system = _Clock
        self._time_entered_buffer = None

    # returns true if the component passed inspection
    def is_ready(self) -> bool:
        return self._ready

    # time to inspect this component, reads data from historical files
    def get_inspection_time(self) -> float:
        if self.name == 'C1':
            return rng.expovariate(1/10.357909999999993)
        elif self.name == 'C2':
            return rng.expovariate(1/15.53690333333332)
        elif self.name == 'C3':
            return rng.expovariate(1/20.632756666666666)
        else:
            raise Exception("invalid component")
    
    def set_buffer_time(self):
        self._time_entered_buffer = _Clock
    
    # signals the component is finished inspecting and can be passed to workstation
    def mark_as_ready(self):
        self._ready = True

    def get_arrival_time(self):
        return self._time_entered_system
    
    def get_buffer_arrival_time(self):
        return self._time_entered_buffer
    
    def __repr__(self) -> str:
        return self.name

class Workstation:
    def __init__(self, name, *buffer_components):
        self.name = name

        self.current_product = None
        self.assembly_time_left = 0.0
        self._time_of_last_update = 0.0
        self.components = [] 
        self._BUFFER_SIZE = 2
        self.buffers = {}
        self.buffer_occupancy = {}
        self.workstation_occupancy = []
        self.components_arrived = 0
        self.component_times_in_workstation =  [] 
        self.num_of_components_in_workstation = 0
        self.num_of_components_passed_through = 0 
        for c in buffer_components:
            self.buffers[c.name] = Queue(self._BUFFER_SIZE)
            self.buffer_occupancy[c.name] = [] 
            key = self.name + ":" + c.name
            individual_run_buffer_occupancies[key] = [] 
        

        #metrics
        self.total_components = {}
        for c in buffer_components:
            self.total_components[c.name] = 0

        #metrics
        self.total_components = {}
        for c in buffer_components:
            self.total_components[c.name] = 0

    def update(self):
        delay = _Clock - self._time_of_last_update
        global components_in_system
        for key in self.buffers.keys():
            self.total_components[key] += self.buffers.get(key).qsize() * delay
        
        current_workstation_occupancy = 0 
        if(self.name == 'W1'):
            if self.current_product is not None: 
                current_workstation_occupancy =  (self.buffers.get('C1').qsize() + 1) 
                self.num_of_components_in_workstation += (current_workstation_occupancy) * delay
                components_in_system +=  (current_workstation_occupancy + 2) * delay
            else: 
                current_workstation_occupancy = (self.buffers.get('C1').qsize()) 
                self.num_of_components_in_workstation += (current_workstation_occupancy) * delay
                components_in_system +=  (current_workstation_occupancy + 2) * delay
        elif(self.name == 'W2'):
            if self.current_product is not None: 
                current_workstation_occupancy = (self.buffers.get('C1').qsize() + self.buffers.get('C2').qsize() + 2) 
                self.num_of_components_in_workstation += (current_workstation_occupancy) * delay
                components_in_system +=  current_workstation_occupancy * delay
            else: 
                current_workstation_occupancy = (self.buffers.get('C1').qsize() + self.buffers.get('C2').qsize()) 
                self.num_of_components_in_workstation += (current_workstation_occupancy) * delay
                components_in_system +=  current_workstation_occupancy * delay

        elif(self.name == 'W3'): 
            if self.current_product is not None: 
                current_workstation_occupancy = (self.buffers.get('C1').qsize() + self.buffers.get('C3').qsize() + 2)
                self.num_of_components_in_workstation += (current_workstation_occupancy) * delay
                components_in_system +=  current_workstation_occupancy * delay
            else: 
                current_workstation_occupancy =  (self.buffers.get('C1').qsize() + self.buffers.get('C3').qsize() )
                self.num_of_components_in_workstation += (current_workstation_occupancy) * delay
                components_in_system +=  current_workstation_occupancy * delay
    
        self._time_of_last_update = _Clock
        self.pass_time(delay)
        # self.try_consume_buffers()
    
    def add_to_buffer(self, current_comp):
        self.num_of_components_passed_through = self.num_of_components_passed_through + 1
        self.buffers[current_comp.name].put_nowait(current_comp)
        
        current_comp.set_buffer_time() 
        self.components.append(current_comp)

        #statistics
        if not self.buffer_occupancy[current_comp.name]:
            self.buffer_occupancy[current_comp.name].append(1)
            self.components_arrived += 1 
        else: 
            self.buffer_occupancy[current_comp.name].append(self.buffer_occupancy[current_comp.name][-1:][0] + 1)
            self.components_arrived += 1 

        if not self.workstation_occupancy: 
            self.workstation_occupancy.append(1)
        else: 
            self.workstation_occupancy.append(self.workstation_occupancy[-1:][0] + 1)

        print(f"{bcolors.OKBLUE}[{_Clock}s] {self}:{bcolors.ENDC} Inserting {current_comp} into buffer")

        self.add_event_to_FEL(0.0, 'check if product can be assembled')

        return True

    # check if all buffers have at least one component in them, if so consume and add to FEL
    def try_consume_buffers(self):
        all_non_empty = True
        global components_passed_through_system
        global component_pass_through_times
        for q in self.buffers.values():
            
            if q.qsize() == 0:
                all_non_empty = False
                break

        if self.current_product != None and self.current_product.is_ready():
            #try to move item to buffer. If successful, change current item to null

            product_list[self.current_product.name] += 1 #temporary just throwing them in a dict
           

            if self.current_product.name == 'P1':
          #      component_times_in_system["total"].append(_Clock - self.current_product.components[0].get_arrival_time())
           #     component_times_in_system[str(current_iteration)].append(_Clock - self.current_product.components[0].get_arrival_time())
            
                component_pass_through_times = component_pass_through_times + (_Clock - self.current_product.components[0].get_arrival_time())
            
                components_passed_through_system = components_passed_through_system + 1
                #statistics
                self.component_times_in_workstation.append(_Clock - self.components[0].get_buffer_arrival_time())
                del self.components[0]

            elif self.current_product.name == 'P2' or self.current_product.name == 'P3':
              #  component_times_in_system['total'].append(_Clock - self.current_product.components[0].get_arrival_time())
             #   component_times_in_system['total'].append(_Clock - self.current_product.components[1].get_arrival_time())
              #  component_times_in_system[str(current_iteration)].append(_Clock - self.current_product.components[0].get_arrival_time())
             #   component_times_in_system[str(current_iteration)].append(_Clock - self.current_product.components[1].get_arrival_time())
               
                component_pass_through_times = component_pass_through_times + (_Clock - self.current_product.components[0].get_arrival_time())
                component_pass_through_times = component_pass_through_times + (_Clock - self.current_product.components[1].get_arrival_time())
               
                components_passed_through_system = components_passed_through_system + 2
               
                self.component_times_in_workstation.append(_Clock - self.components[0].get_buffer_arrival_time())
                self.component_times_in_workstation.append(_Clock - self.components[1].get_buffer_arrival_time())

                print(self.components)
                del self.components[0] 
                del self.components[0] 
  
            self.current_product = None

        if self.current_product != None:
            print(f'{bcolors.FAIL}[{_Clock}s] {self}:{bcolors.ENDC} still working on {self.current_product}')
            return # still working or still blocked
        if all_non_empty:
            for i in self.buffers.keys():
                self.buffer_occupancy[i].append(self.buffer_occupancy[i][-1:][0] - 1)
            self.current_product = Product([i.get() for i in self.buffers.values()])
            self.assembly_time_left = self.get_assembly_time()
            self.add_event_to_FEL(self.assembly_time_left, 'finished assembling ' + str(self.current_product))

    def update_statistics(self): 
        for i in self.buffers.keys():
            key = self.name + ":" + i
            individual_run_buffer_occupancies[key].append(sum(self.buffer_occupancy[i])/len(self.buffer_occupancy[i]))
        

    def generate_report(self):
        for i in self.buffers.keys():
            print(f"Length of occupancy list for {self.name}, buffer {i}: {len(self.buffer_occupancy[i])}")
            print(f"standard deviation of occupancy for {self.name}, buffer {i}: {statistics.stdev(self.buffer_occupancy[i])}")
            print(f"Average occupancy for {self.name}, buffer {i}: {sum(self.buffer_occupancy[i])/len(self.buffer_occupancy[i])}")
        print(f"Average time in workstation for {self.name} : {sum(self.component_times_in_workstation) / len(self.component_times_in_workstation)}")
        print(f"Arrival rate for {self.name}: {self.components_arrived / _Clock}")
        print(f"Average workstation occupancy {self.name}: {sum(self.workstation_occupancy)/ len(self.workstation_occupancy)}")

    def get_assembly_time(self):
        if self.name == 'W1':
            return rng.expovariate(1/4.604416666666665)
        elif self.name == 'W2':
            return rng.expovariate(1/11.092606666666665)
        elif self.name == 'W3':
            return rng.expovariate(1/8.795580000000005)
        else:
            raise Exception("invalid component")


    def pass_time(self, delay):
        if self.current_product != None and not self.current_product.is_ready():
            self.assembly_time_left -= delay
            if abs(self.assembly_time_left) < 1e-6:
                self.current_product.mark_as_ready()
                print(f"{bcolors.WARNING}[{_Clock}] {self}:{bcolors.ENDC} marked its product {self.current_product} as ready\033[0m")


    def add_event_to_FEL(self, delay, event_name):
        print(f"{bcolors.OKGREEN}[{_Clock}s] {self}:{bcolors.ENDC} adding '{event_name}' at time {_Clock + delay} to the FEL")
        FEL.put_nowait(_Clock + delay)


    def __repr__(self):
        return self.name


class Inspector:
    def __init__(self, name, workstations, *incoming_components):
        self.name = name
        self.incoming_components = [i for i in incoming_components]

        self.current_comp = None
        self.inspection_time_left = 0.0
        self._time_of_last_update = 0.0
        self.percentage_time_blocked = 0 
        self.time_spent_in_states = {}
        self.inspection_times = [] 
        #reference to workstations
        self.num_arrivals = 0 
        self._workstations = workstations

    def generate_report(self):
        self.percentage_time_blocked = self.time_spent_in_states['blocked']/(self.time_spent_in_states['working'] + self.time_spent_in_states['blocked'])
        print(f"Percentage blocked {self.name}: {self.time_spent_in_states['blocked']/(self.time_spent_in_states['working'] + self.time_spent_in_states['blocked'])}")

    def update(self):
        delay = _Clock - self._time_of_last_update

        state_since_last_update = self.get_state()
        time_already_spent_in_this_state = self.time_spent_in_states.get(state_since_last_update, 0.0)
        self.time_spent_in_states.update({state_since_last_update: time_already_spent_in_this_state + delay})

        self._time_of_last_update = _Clock

        self.pass_time(delay)
        # self.maybe_act()

    def get_state(self):
        if self.current_comp == None:
            return 'initial'
        elif self.current_comp.is_ready():
            return "blocked"
        else:
            return "working"
    
    def maybe_act(self):
        if self.current_comp != None and self.current_comp.is_ready():
            #try to move item to buffer. If successful, change current item to null
            got_rid = self.try_to_move_component_to_buffer(self.current_comp)
            if got_rid:
               
                self.inspection_times.append(_Clock - self.current_comp.get_arrival_time())
                self.current_comp = None
                #self.add_event_to_FEL(0.0, "buffer got new component")

        if self.current_comp != None:
            print(f'{bcolors.FAIL}[{_Clock}s] {self}:{bcolors.ENDC} still working or still blocked on {self.current_comp}')
            return # still working or still blocked
        
        self.num_arrivals = self.num_arrivals + 1
        self.current_comp = self.get_new_component()
        self.inspection_time_left = self.current_comp.get_inspection_time()
        
    

        self.add_event_to_FEL(self.inspection_time_left, 'finished inspecting ' + str(self.current_comp))

    def get_new_component(self) -> Component:
        return Component(random.choice(self.incoming_components).name)

    def pass_time(self, delay):
        if self.current_comp != None and not self.current_comp.is_ready():
            
            self.inspection_time_left -= delay
            if abs(self.inspection_time_left) < 1e-6:
                self.current_comp.mark_as_ready()
                print(f"{bcolors.WARNING}[{_Clock}] {self}:{bcolors.ENDC} marked its component {self.current_comp} as ready")

    def add_event_to_FEL(self, delay, event_name):
        print(f"{bcolors.OKGREEN}[{_Clock}s] {self}:{bcolors.ENDC} adding '{event_name}' at time {_Clock + delay} to the FEL")
        FEL.put_nowait(_Clock + delay)

    def try_to_move_component_to_buffer(self, current_comp) -> bool:
        """
        Tries to move a component to the corresponding workstation's buffer.
        Returns True if the move was successful, False otherwise.
        """

        min_queue_len = 2  # all buffers have max length 2
        min_queue_workstation = None

        # Find the workstation with the shortest queue for the given component
        for w in self._workstations:
            if current_comp.name in w.buffers:
                queue_len = w.buffers[current_comp.name].qsize()
                if queue_len < min_queue_len:
                    min_queue_len = queue_len
                    min_queue_workstation = w
        # Try to add the component to the buffer with the shortest queue
        if min_queue_workstation is not None:

            return min_queue_workstation.add_to_buffer(current_comp)

        return False       

    def __repr__(self):
        return self.name

# Below this is just for running the simulation and printing stuff
def print_buffers():
    print("w1 c1 buffer = ", end ="")
    while not w1.buffers['C1'].empty():
        item = w1.buffers['C1'].get()
        print(item, end=" ")
        
    print("\nw2 c1 buffer = ", end ="")
    while not w2.buffers['C1'].empty():
        item = w2.buffers['C1'].get()
        print(item, end=" ")

    print("\nw2 c2 buffer = ", end ="")
    while not w2.buffers['C2'].empty():
        item = w2.buffers['C2'].get()
        print(item, end=" ")

    print("\nw3 c1 buffer = ", end ="")
    while not w3.buffers['C1'].empty():
        item = w3.buffers['C1'].get()
        print(item, end=" ")

    print("\nw3 c3 buffer = ", end ="")
    while not w3.buffers['C3'].empty():
        item = w3.buffers['C3'].get()
        print(item, end=" ")

    print()

def update_statistics():
    w1.update_statistics() 
    w2.update_statistics() 
    w3.update_statistics() 


#def plot_ensemble_means():
#    means = [] 
#    i = 0
#    min_components =  min(len(component_times_in_system['1']), 
#                          len(component_times_in_system['2']), len(component_times_in_system['3']),
#                          len(component_times_in_system['4']), len(component_times_in_system['5']), 
#                          len(component_times_in_system['6'])
#                          )
#    cumulative_average = [] 
#    
#    while i < min_components:
#        result = (component_times_in_system['1'][i] + component_times_in_system['2'][i] + component_times_in_system['3'][i] + component_times_in_system['4'][i] + component_times_in_system['5'][i] + component_times_in_system['6'][i]) / current_iteration 
#        means.append(result)
#        cumulative_average.append(sum(means)/len(means))
#        i = i + 1
#
#    components_through_system = range(0, min_components)
#    plt.plot( means)
#    a, b = np.polyfit(np.array(components_through_system), np.array(means), 1)
#    plt.plot(cumulative_average)
#    plt.ylabel('Performance Measure')
#    plt.xlabel('Number of Components Through System')
#    plt.title('Welch Plot')
#
 #   plt.savefig('welch.png')
 #   plt.clf()


def run_replication_analysis(): 
    run1_average = sum(component_times_in_system['1'][1000:10000])/9000
    run2_average = sum(component_times_in_system['2'][1000:10000])/9000
    run3_average = sum(component_times_in_system['3'][1000:10000])/9000
    run4_average = sum(component_times_in_system['4'][1000:10000])/9000
    run5_average = sum(component_times_in_system['5'][1000:10000])/9000
    run6_average = sum(component_times_in_system['6'][1000:10000])/9000
    print("replication 1 times in system average", run1_average)
    print("replication 2 times in system average", run2_average)
    print("replication 3 times in system average", run3_average)
    print("replication 4 times in system average", run4_average)
    print("replication 5 times in system average", run5_average)
    print("replication 6 times in system average", run6_average)
    
def generate_system_report():
    
    print("\n_________ OVERALL SYSTEM STATISTICS ____________ \n")
 
    print("w1c1 avg buf occup: ", sum(w1c1_buf_occup) / len(w1c1_buf_occup))
    print('w1c1 stddev: ', statistics.stdev(w1c1_buf_occup))

    print("w2c1 avg buf occup: ", sum(w2c1_buf_occup) / len(w2c1_buf_occup))
    print('w2c1 stddev: ', statistics.stdev(w2c1_buf_occup))

    print("w2c2 avg buf occup: ", sum(w2c2_buf_occup) / len(w2c2_buf_occup))
    print('w2c2 stddev: ', statistics.stdev(w2c2_buf_occup))
    
    print("w3c1 avg buf occup: ", sum(w3c1_buf_occup) / len(w3c1_buf_occup))
    print('w3c1 stddev: ', statistics.stdev(w3c1_buf_occup))

    print("w3c3 avg buf occup: ", sum(w3c3_buf_occup) / len(w3c3_buf_occup))
    print('w3c3 stddev: ', statistics.stdev(w3c3_buf_occup))

    print("avg num of components in w1: ", sum(components_in_workstation['1']) / len(components_in_workstation['1']))
    print("avg num of components in w2: ", sum(components_in_workstation['2']) / len(components_in_workstation['2']))
    print("avg num of components in w3: ", sum(components_in_workstation['3']) / len(components_in_workstation['3']))
    print("components_in_system_total: ", components_in_system_total)
    print("avg num of components in system: ", sum(components_in_system_total) / len(components_in_system_total))
    print("avg num of time in system: ", sum(component_times_in_system_total) / len(component_times_in_system_total))

    print("arrival rate:", sum(arrival_rates)/len(arrival_rates))
    print("workstation 1 arrival rate", sum(workstation1_arrival_rates)/len(workstation1_arrival_rates))
    print("Workstation 1 avg num of components in system", sum(components_in_workstation['1'])/len(components_in_workstation['1']))
    print("workstation 1 avg time in system", sum(component_times_in_workstation1_total)/len(component_times_in_workstation1_total))
    
    print("workstation 2 arrival rate", sum(workstation2_arrival_rates)/len(workstation2_arrival_rates))
    print("Workstation 2 avg num of components in system", sum(components_in_workstation['2'])/len(components_in_workstation['2']))
    print("workstation 2 avg time in system", sum(component_times_in_workstation2_total)/len(component_times_in_workstation2_total))

    print("workstation 3 arrival rate", sum(workstation3_arrival_rates)/len(workstation3_arrival_rates))
    print("Workstation 3 avg num of components in system", sum(components_in_workstation['3'])/len(components_in_workstation['3']))
    print("workstation 3 avg time in system", sum(component_times_in_workstation3_total)/len(component_times_in_workstation3_total))

def generate_run_report(): 
    print("\n_________ SYSTEM STATISTICS ____________ \n")
    print('Products: ', product_list)
  #  print('Average time component spends in system', sum(component_times_in_system['total'])/len(component_times_in_system['total']))
    print('System Throughput', (product_list['P1'] + product_list['P2'] + product_list['P3']) / _Clock)
    
    print("\n_________ INSPECTOR 2 STATISTICS ____________ \n")
    i2.generate_report()
    
    print("\n_________ WORKSTATION 1 STATISTICS ____________ \n")
    w1.generate_report()
    print("\n_________ WORKSTATION 2 STATISTICS ____________ \n")
    w2.generate_report()
    print("\n_________ WORKSTATION 3 STATISTICS ____________ \n")
    w3.generate_report()

if __name__ == '__main__':
    w1c1_buf_occup = []
    w2c1_buf_occup = []
    w2c2_buf_occup = []
    w3c1_buf_occup = []
    w3c3_buf_occup = []

    components_in_system_total = []
    component_times_in_system_total = []
    component_times_in_workstation1_total = []
    component_times_in_workstation2_total = [] 
    component_times_in_workstation3_total = [] 
    workstation1_arrival_rates = [] 
    workstation2_arrival_rates = [] 
    workstation3_arrival_rates = [] 
    component_throughput = [] 
    arrival_rates = [] 
    for i in range(1, 9):
        current_iteration = i
        components_in_system = 0 
        component_pass_through_times = 0

        _Clock = 0
        #init workstations and inspectors
        w1 = Workstation('W1', Component('C1'))
        w2 = Workstation('W2', Component('C1'), Component('C2'))
        w3 = Workstation('W3', Component('C1'), Component('C3'))
        workstations = [w1, w2, w3]

        i1 = Inspector('I1', workstations, Component('C1'))
        i2 = Inspector('I2', workstations, Component('C2'), Component('C3'))
        inspectors = [i1, i2]

        components_passed_through_system = 0 

        while components_passed_through_system < 11000:
            i1.maybe_act()
            i2.maybe_act()
            w1.try_consume_buffers()
            w2.try_consume_buffers()
            w3.try_consume_buffers()

            try:
                _Clock = FEL.get_nowait()
            except Empty:
                pass

            for i in inspectors:
                i.update()

            for w in workstations:
                w.update()


        update_statistics()
        generate_run_report()
            
        #print final states
        print('final buffer states: ')
        print_buffers()
        print('Products: ', product_list)

        print('Inspector 1 time spent in states: ', i1.time_spent_in_states)
        print('Inspector 2 time spent in states: ', i2.time_spent_in_states)


        buff_occ_avg = w1.total_components['C1']/_Clock
        w1c1_buf_occup.append(buff_occ_avg)
        w2c1_buf_occup.append(w2.total_components['C1']/_Clock)
        w2c2_buf_occup.append(w2.total_components['C2']/_Clock)
        w3c1_buf_occup.append(w3.total_components['C1']/_Clock)
        w3c3_buf_occup.append(w3.total_components['C3']/_Clock)

        components_in_workstation['1'].append(w1.num_of_components_in_workstation / _Clock)
        components_in_workstation['2'].append(w2.num_of_components_in_workstation / _Clock)
        components_in_workstation['3'].append(w3.num_of_components_in_workstation / _Clock)
        
        components_in_system_total.append(components_in_system / _Clock)
        component_times_in_system_total.append(component_pass_through_times/components_passed_through_system)
        
        arrival_rates.append((i1.num_arrivals + i2.num_arrivals)/_Clock)
        workstation1_arrival_rates.append(w1.num_of_components_passed_through/_Clock)
        workstation2_arrival_rates.append(w2.num_of_components_passed_through/_Clock)
        workstation3_arrival_rates.append(w3.num_of_components_passed_through/_Clock)
        
        component_times_in_workstation1_total.append(sum(w1.component_times_in_workstation)/len(w1.component_times_in_workstation))
        component_times_in_workstation2_total.append(sum(w2.component_times_in_workstation)/len(w2.component_times_in_workstation))
        component_times_in_workstation3_total.append(sum(w3.component_times_in_workstation)/len(w3.component_times_in_workstation))
        
    #print final states
    print('final buffer states: ')
    print_buffers()
    
    generate_system_report()

   # plot_ensemble_means()
    run_replication_analysis()


