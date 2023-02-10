import queue

class Inspector(object):
    def __init__(self, inspector_ID): 
        self._arrival = 1
        self._departure = 2

        self.waiting_queue = []
        self.in_service = []
        self.inspector_ID = inspector_ID 

        self._Blocked = False
        self._Clock = 0.0 
        

    def put(self, component, clock): 
        """ add a component into queue"""
        """ component = (arrivalTime, componentID) """

        """ update clock"""
        self._Clock = clock

        if self._Blocked:
            """ add to queue if server busy"""
            self.waiting_queue.append(component)

        else:
            """ start service if inspector is free """
            self._Blocked = True
            self.in_service.append(component)
            depart = self.scheduleDeparture(component)

            """update statistic here eventually """
            
        return depart

    def get(self, clock):
        """ get component from the service queue"""
        component = self.in_service.pop(0)

        """ update clock"""
        self._Clock = clock

        """ if there is a component waiting to be serviced, schedule next departure"""
        if (len(self.waiting_queue) > 0):
            """ move component from queue to service"""
            
            component1 = self.waiting_queue.pop(0)
            self.in_service.append(component1)
 
            """ schedule departure for head-of-line component"""
            depart = self.scheduleDeparture(component1)
        
        else:
            self._Blocked = False
            depart = None


    def scheduleDeparture(self, component):
        ServiceTime = self.getServiceTime()
        depart = (self._Clock + ServiceTime, self._departure, self.inspector_ID, component)
        return depart  


    def getServiceTime(self):
        """ This function gets the service time for a component from the file""" 
        return 0.25

    def print_state(self):
        print("waiting_queue: ", self.waiting_queue)
        print("in_service: ", self.in_service)
        print("blocked: ", self._Blocked)
        print("clock: ", self._Clock)



class Workstation(object):
    #Define each queue

    def __init__(self, workstation_ID):
        self.buffer1 = []
        self.buffer2 = []
        self.in_service = []
        self.workstation_ID = workstation_ID

    def put(self, buffer, component): 
        #function to add component to workstation 
        
        #If workstation ID is 1, only one buffer is used
        if(self.workstation_ID == 1): 
             if(len(self.buffer1) < 2): 
                self.buffer1.append(component)
                self.in_service.append(self.buffer1.pop())
                
                return self.generateDepartureEvent()
        else: 
            #if buffer is 1, buffer one has space, and buffer 2 isn't empty
            if(buffer == 1 and len(self.buffer2) > 0 and len(self.buffer1) < 2): 
                
                self.buffer1.append(component)
                self.in_service.append(self.buffer1.pop(), self.buffer2.pop())
                
                return self.generateDepartureEvent()
                # If Both buffers have at least one component, and
                # If workstation is available, remove components from buffers and add one product to workstation (generate workstation departure event)
            else:
                return None


    def get(self):
        #generate product from in_service components 
        self.in_service.pop() 
        #return product

        #If both buffers are full, should generate a new departure event
        departure_event = None 
        if(self.workstation_ID == 1):
            if(len(self.buffer1) > 0): 
                self.in_service.append(self.buffer1.pop())
               
                departure_event = self.generateDepartureEvent() 
        elif(len(self.buffer1) > 0 and len(self.buffer2) > 0): 
            self.in_service.append(self.buffer1.pop(), self.buffer2.pop())
          
            departure_event = self.generateDepartureEvent()
        
        #return product, departure event
        pass

    def generateDepartureEvent(self): 
        #Generate departure event with time + next workstation service time from file
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
        
    def scheduleArrival(self):
        #TODO: schedule new arrival to the system 
        pass 

    def processDeparture(self):
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