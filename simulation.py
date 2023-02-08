import queue

class Queue(object):
    #Define each queue

    def __init__(self):
        pass 

    def put(): 
        #TODO: function to add component/product to queue 
        pass 

    def get():
        #TODO: function to remove component/product from queue 
        pass

    def scheduleDeparture(): 
        #TODO: function to schedule departure from queue 
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
