import queue

ARRIVAL_EVENT = 1
DEPARTURE_EVENT = 2

class Inspector(object):
    def __init__(self, inspector_ID): 
        self._arrival = ARRIVAL_EVENT      
        self._departure = DEPARTURE_EVENT     

        self.in_service = []
        self.inspector_ID = inspector_ID 

        self._Clock = 0.0 
        

    def put(self, component, clock, is_blocked): 
        """ add a component into queue"""
        """ component = (arrivalTime, componentID) """

        """ update clock"""
        self._Clock = clock

        """ start service """
        self.in_service.append(component)
        depart = self.scheduleDeparture(component, is_blocked)

        """update statistic here eventually """
            
        return depart

    def get(self, clock):
        """ get component from the service queue"""
        component = self.in_service.pop(0)

        """ update clock"""
        self._Clock = clock

        """ get next component to be serviced"""
        next_component = self.getNextComponent()
        self.in_service.append(next_component)
        """ schedule departure for next component"""
        depart = self.scheduleDeparture(next_component)

        return component, depart 


    def scheduleDeparture(self, component, is_blocked):
        """ This functions schedules a departure event for a given component"""
        if is_blocked:
            deltaTime = 1.0
            depart = (self._Clock + deltaTime, self._departure, self.inspector_ID, component)
        else:
            ServiceTime = self.getServiceTime()
            depart = (self._Clock + ServiceTime, self._departure, self.inspector_ID, component)

        return depart  

    def getServiceTime(self):
        """ This function gets the service time for a component from the file""" 

        #temporarily just returns constant value
        return 0.25

    def getNextComponent(self): 
        """ This function generates the next component when the previous one departs - depends on the inspector ID"""
        if self.inspector_ID == 1:
            # return component of type 1
            arrivalTime = self._Clock
            componentID = 1
            component = (arrivalTime, componentID)
        else: 
            #randomly decide if it should return component of type 1 or 2
            pass 

class Workstation(object):
    #Define each queue

    def __init__(self, workstation_ID):

        self._arrival = ARRIVAL_EVENT      
        self._departure = DEPARTURE_EVENT  

        self.waiting_buffer_one = []
        self.waiting_buffer_two = []

        self.in_service = []
        self.workstation_ID = workstation_ID

        self._Clock = 0.0 

    def put(self, buffer, component, clock):
        """ add a component into its respective buffer"""
        """ buffer: what buffer to put into
            component: the component that is being put
            clock: clock time of event
        """

        """ update clock"""
        self._Clock = clock
        
        """if workstation one, only has one buffer"""
        if self.workstation_ID == 1: 
            if len(self.waiting_buffer_one) < 2: 
                self.waiting_buffer_one.append(component)
            else:
                #buffer is full, should never reach here
                pass
            """ if buffer one has at least one component, put it in service """
            if len(self.waiting_buffer_one > 0):
                product = (self.waiting_buffer_one.pop(0), None)
                self.in_service.append(product)
                depart = self.scheduleDeparture(product)
            else:
                depart = None

        elif self.workstation_ID == 2 or self.workstation_ID == 3: 
            """ if buffer one isn't full, add component """
            if buffer == 1:
                if len(self.waiting_buffer_one) < 2:
                    self.waiting_buffer_one.append(component)
                else:
                    #buffer is full, should never reach here
                    pass

            """ if buffer two isn't full, add component """ 
            if buffer == 2:
                if len(self.waiting_buffer_two) < 2:
                    self.waiting_buffer_two.append(component)
                else:
                    #buffer is full, should never reach here
                    pass

            """ if both buffers have at least one component, put them in service """
            if len(self.waiting_buffer_one > 0) and len(self.waiting_buffer_two) > 0:
                product = (self.waiting_buffer_one.pop(0), self.waiting_buffer_two.pop(0))
                self.in_service.append(product)
                depart = self.scheduleDeparture(product)
            else:
                depart = None

        return depart

    def get(self, clock):
        """ get product from the server of the queue"""
        product = self.in_service.pop(0)

        """ update clock"""
        self._Clock = clock

        if self.workstation_ID == 1: 
            """ if there are components waiting to be serviced, schedule next departure"""
            if len(self.waiting_buffer_one > 0):
                """ move component from queue to service"""
                product = (self.waiting_buffer_one.pop(0), None)
                self.in_service.append(product)
                """ schedule departure for head-of-line component"""
                depart = self.scheduleDeparture(product)
            else:
                depart = None


        elif self.workstation_ID == 2 or self.workstation_ID == 3: 
            """ if there are components waiting to be serviced, schedule next departure"""
            if len(self.waiting_buffer_one > 0) and len(self.waiting_buffer_two) > 0:
                """ move component from queue to service"""
                product = (self.waiting_buffer_one.pop(0), self.waiting_buffer_two.pop(0))
                self.in_service.append(product)
                """ schedule departure for head-of-line component"""
                depart = self.scheduleDeparture(product)
            else:
                depart = None

        #return product, departure event
        return product, depart    

    def scheduleDeparture(self, product): 
        ServiceTime = self.getServiceTime()
        depart = (self._Clock + ServiceTime, self._departure, self.workstation_ID, product)
        return depart  

    def getServiceTime(self):
        """ This function gets the service time for a component from the file""" 

        #temporarily just returns constant value
        return 0.25

    def getBufferLengths(self):
        """returns the current state of the workstations buffers"""
        return (len(self.waiting_buffer_one), len(self.waiting_buffer_two))

class Sim(object):
    def __init__(self):
        self._Clock = 0.0 

        self._arrival = 1
        self._inspector_departure = 2
        self._workstation_departure = 3 

        #Number of queues to create
        self.number_of_queues = 5  
        
        #starting queue ID 
        self.queue_id = 0

        #Total number of customers the system will run for 
        self.total_customers = 10

        #Total number of departures from system 
        self.total_departures = 0 

        #Create future event list
        self.FEL = queue.PriorityQueue()

        #initialize inspectors and workstations 
        self.inspector_1 = Inspector(1)
        self.inspector_2 = Inspector(2)
        self.workstation_1 = Workstation(1)
        self.workstation_2 = Workstation(2)
        self.workstation_3 = Workstation(3)

    def scheduleArrival(self, clock, ID, component):
        if(ID == 1):
            event = self.inspector_1.put((clock, component), clock, False)
        elif(ID == 2): 
            event = self.inspector_2.put((clock, component), clock, False)
        

        self.FEL.put(event)

    def processInspectionDeparture(self, clock, ID, component):
        #TODO: Process Departure from inspector
        
        w1_lengths = self.workstation_1.getBufferLengths() 
        w2_lengths = self.workstation_1.getBufferLengths() 
        w3_lengths = self.workstation_1.getBufferLengths() 

        if(component == 'c1'): 
            if w1_lengths[0] >= 2:
                if w2_lengths[0] < 2 and w2_lengths[0] < w3_lengths[0]: 
                    event = self.workstation_2.put(1, (clock, component), clock)
                elif w3_lengths[0] < 2 and w3_lengths[0] < w2_lengths[0]: 
                    event = self.workstation_3.put(1, (clock, component), clock)
                elif w3_lengths[0] < 2 and w3_lengths[0] == w2_lengths[0]: 
                    event = self.workstation_2.put(1, (clock, component), clock)
                else: 
                    event = self.inspector_1.put((clock, component), clock, True)
            elif(w1_lengths[0] == 1): 
                if w2_lengths[0] == 0: 
                    event = self.workstation_2.put(1, (clock, component), clock)
                elif w3_lengths[0] == 0: 
                    event = self.workstation_3.put(1, (clock, component), clock)
                else: 
                    event = self.workstation_1.put(1, (clock, component), clock)
            else:
                event = self.workstation_1.put(1, (clock, component), clock)
        elif(component == 'c2'): 
            if w2_lengths[1] >= 2:
                event = self.inspector_2.put((clock, component), clock, True)
            else: 
                event = self.workstation_2.put(2, (clock, component), clock)
        elif(component == 'c3'): 
            if w3_lengths[1] >= 2:
                event = self.inspector_2.put((clock, component), clock, True)
            else: 
                event = self.workstation_3.put(3, (clock, component), clock)
        else: 
            #something horrible has happened
            event = None 

        return event
    
    def processWorkstationDeparture(self, clock, ID): 
        if(ID == 1):
            self.inspector_1.get(clock)
        elif(ID == 2): 
            self.inspector_2.get(clock)
        elif(ID == 3): 
            self.workstation_3.get(clock)


#Create instance of simulation
simulation = Sim() 

event = (simulation._Clock, simulation._arrival, 1, 'c1')
event2 = (simulation._Clock, simulation._arrival, 2, 'c2')

simulation.FEL.put(event)
simulation.FEL.put(event2)

#Loop 
while(simulation.total_departures < simulation.total_customers):
    event = simulation.FEL.get()
    simulation._Clock = event[0]
    
    if(event[1] == simulation._arrival):
        simulation.scheduleArrival(simulation._Clock, event[2], event[3])
    elif(event[1] == simulation._inspector_departure):
        simulation.processInspectionDeparture(simulation._Clock, event[2], event[3])
    elif(event[1] == simulation._workstation_departure): 
        simulation.total_departures = simulation.total_departures + 1
        simulation.processWorkstationDeparture(simulation._Clock, event[2])
    