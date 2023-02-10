import queue

class Inspector(object):
    def __init__(self, inspector_ID): 
        self.in_service = [] 
        self.inspector_ID = inspector_ID 

    def put(self, component, blocked): 
        #function to add component to inspector/ generate departure event
        self.in_service.append(component)
        return self.generateDepartureEvent(blocked)

    def generateDepartureEvent(component, blocked): 
        #Generate departure 
        if(blocked):
            #Return departure event with time + some constant
            pass
        else: 
            #Return departure event with time + next service time from file
            pass

    def getNextComponent(self): 
        if self.inspector_ID == 1:
            # return component of type 1
            pass
        else: 
            #randomly decide if it should return component of type 1 or 2
            pass 

    def get(self):
        #remove component from inspector and put in workstation buffer if one of right type is available
        
        leaving_component = self.in_service.pop()
        new_component = self.getNextComponent() 
        self.in_service.append(new_component) 

        return leaving_component, self.generateDepartureEvent(False)

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
                    event = self.workstation_2.put()
                elif w3_lengths[0] < 2 and w3_lengths[0] < w2_lengths[0]: 
                    event = self.workstation_3.put()
                elif w3_lengths[0] < 2 and w3_lengths[0] == w2_lengths[0]: 
                    event = self.workstation_2.put()
                else: 
                    event = self.inspector_1.put((clock, component), clock, True)
            elif(w1_lengths[0] == 1): 
                if w2_lengths[0] == 0: 
                    event = self.workstation_2.put()
                elif w3_lengths[0] == 0: 
                    event = self.workstation_3.put()
                else: 
                    event = self.workstation_1.put()
            else:
                event = self.workstation_1.put()
        elif(component == 'c2'): 
            if w2_lengths[1] >= 2:
                event = self.inspector_2.put((clock, component), clock, True)
            else: 
                event = self.workstation_2.put()
        elif(component == 'c3'): 
            if w3_lengths[1] >= 2:
                event = self.inspector_2.put((clock, component), clock, True)
            else: 
                event = self.workstation_3.put()
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

#Schedule First Arrival
simulation.scheduleArrival() 

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
    