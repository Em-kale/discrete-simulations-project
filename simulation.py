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