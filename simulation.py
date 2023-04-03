from queue import Queue, PriorityQueue, Full, Empty
import random
from milestone2 import RandomNumberGenerator

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
components_in_system = [] 

# define product list to track how many products were created
product_list = {'P1': 0, 'P2': 0, 'P3': 0}

class Product:
    def __init__(self, components):
        #determine product type based on components provided
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
        self._time_exited_system = None

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

    # signals the component is finished inspecting and can be passed to workstation
    def mark_as_ready(self):
        self._ready = True
        
    def __repr__(self) -> str:
        return self.name

class Workstation:
    def __init__(self, name, *buffer_components):
        self.name = name

        self.current_product = None
        self.assembly_time_left = 0.0
        self._time_of_last_update = 0.0

        self._BUFFER_SIZE = 2
        self.buffers = {}
        for c in buffer_components:
            self.buffers[c.name] = Queue(self._BUFFER_SIZE)

    def update(self):
        delay = _Clock - self._time_of_last_update
        self._time_of_last_update = _Clock
        self.pass_time(delay)
        # self.try_consume_buffers()

    def add_to_buffer(self, current_comp):
        self.buffers[current_comp.name].put_nowait(current_comp)
        print(f"{bcolors.OKBLUE}[{_Clock}s] {self}:{bcolors.ENDC} Inserting {current_comp} into buffer")

        self.add_event_to_FEL(0.0, 'check if product can be assembled')

        return True

    # check if all buffers have at least one component in them, if so consume and add to FEL
    def try_consume_buffers(self):
        all_non_empty = True
        for q in self.buffers.values():
            if q.qsize() == 0:
                all_non_empty = False
                break

        if self.current_product != None and self.current_product.is_ready():
            #try to move item to buffer. If successful, change current item to null

            product_list[self.current_product.name] += 1 #temporary just throwing them in a dict
           

            #statistics
            if self.current_product.name == 'P1':
                components_in_system.append(components_in_system[-1:][0]- 1)
            elif self.current_product.name == 'P2' or self.current_product.name == 'P3':
                components_in_system.append(components_in_system[-1:][0] - 2)
            
            self.current_product = None

        if self.current_product != None:
            print(f'{bcolors.FAIL}[{_Clock}s] {self}:{bcolors.ENDC} still working on {self.current_product}')
            return # still working or still blocked
        if all_non_empty:
            self.current_product = Product([i.get() for i in self.buffers.values()])
            self.assembly_time_left = self.get_assembly_time()
            self.add_event_to_FEL(self.assembly_time_left, 'finished assembling ' + str(self.current_product))


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

        self.time_spent_in_states = {}

        #reference to workstations
        self._workstations = workstations

    def update(self):
        delay = _Clock - self._time_of_last_update

        state_since_last_update = self.get_state()
        time_already_spent_in_this_state = self.time_spent_in_states.get(state_since_last_update, 0.0)
        self.time_spent_in_states.update({state_since_last_update: time_already_spent_in_this_state + delay})

        self._time_of_last_update = _Clock
        self.pass_time(delay)
        # self.maybe_act()

    #potentially useless
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
                self.current_comp = None
                #self.add_event_to_FEL(0.0, "buffer got new component")

        if self.current_comp != None:
            print(f'{bcolors.FAIL}[{_Clock}s] {self}:{bcolors.ENDC} still working or still blocked on {self.current_comp}')
            return # still working or still blocked

        self.current_comp = self.get_new_component()
        self.inspection_time_left = self.current_comp.get_inspection_time()
        
        if not components_in_system:
            components_in_system.append(1)
        else:
            components_in_system.append(components_in_system[-1:][0] + 1)

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

if __name__ == '__main__':

    #init workstations and inspectors
    w1 = Workstation('W1', Component('C1'))
    w2 = Workstation('W2', Component('C1'), Component('C2'))
    w3 = Workstation('W3', Component('C1'), Component('C3'))
    workstations = [w1, w2, w3]

    i1 = Inspector('I1', workstations, Component('C1'))
    i2 = Inspector('I2', workstations, Component('C2'), Component('C3'))
    inspectors = [i1, i2]

    #run the simulation loop 100 times
    for i in range(100):
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
        
    #print final states
    print('final buffer states: ')
    print_buffers()
    print('Products: ', product_list)

    print('Components in system', components_in_system)


    print('Inspector 1 time spent in states: ', i1.time_spent_in_states)
    print('Inspector 2 time spent in states: ', i2.time_spent_in_states)









