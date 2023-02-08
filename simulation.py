import queue

class Inspector(object):
    def __init__(self): 
        arrival_queue = [] 
        pass 

    def put(): 
        #TODO: function to add component to inspector/ generate departure event? 
        pass 

    def get():
        #TODO: remove component from inspector and put in workstation buffer if one of right type is available
        pass

class Workstation(object):
    #Define each queue

    def __init__(self):
        buffer1 = queue.Queue(maxsize=2)
        buffer2 = queue.Queue(maxsize=2)
    

    def put(): 
        #TODO: function to add component to workstation 
        # If Both buffers have at least one component, and
        # If workstation is available, remove components from buffers and add one product to workstation (generate workstation departure event)
        pass 

    def get():
        #TODO: remove products from workstation
        pass

    def scheduleDeparture(): 
        #TODO: 
        pass 

class Sim(object):
    def __init__(self):
        #Number of queues to create
        self.number_of_queues = 5  
        
        #starting queue ID 
        self.queue_id = 0

        #list of queues for simulation 
        self.queue_list = []

        #Total number of customers the system will run for 
        self.total_customers = 10

        #Total number of departures from system 
        self.total_departures = 0 

        #Create future event list
        self.FEL = queue.PriorityQueue()
        
        #Create an instance of queue for each 
        for i in range(self.number_of_queues):
                self.queue_list.append(Queue(self.queue_id))
                self.queue_id += 1
    
    def scheduleArrival():
        #TODO: schedule new arrival to the system 
        pass 

    def processDeparture():
        #TODO: Process Departure from system
        pass

#Create instance of simulation
simulation = Sim() 

#Schedule First Arrival
simulation.scheduleArrival() 

#Loop 
while(simulation.total_departures < simulation.total_customers):
    #Get next item from FEL 
    #Do stuff
    #Repeat
    pass; 