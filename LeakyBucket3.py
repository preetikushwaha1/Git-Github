from datetime import datetime
import time
import redis

r = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)  
class Leaking_Bucket:
    def __init__(self, capacity, refill_rate, request):
        self.request = request
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity 
        self.last_refill = datetime.now().strftime("%H:%M:%S")
        self.last_processed_time =None
        
    def refill(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        print("current time:",current_time)
        time_since_elapsed = datetime.strptime(current_time,"%H:%M:%S")-datetime.strptime(self.last_refill,"%H:%M:%S")
        print("time_since_elapsed:",time_since_elapsed)
        refill_tokens = time_since_elapsed.total_seconds() * self.refill_rate
        #print("Refill_tokens:",refill_tokens)
        self.tokens += refill_tokens
        #print("tokens:", self.tokens)
        self.tokens = min(int(self.tokens), self.capacity)
        print("min tokens", self.tokens)
        self.last_refill = current_time 
        
        
    def token_consume(self, tokens): 
        #current_time = datetime.now().strftime("%H:%M:%S")
        #print("current time:", current_time)
        if self.tokens ==0:                                      #check if token is empty 
            if self.request>0:                                   #request is greater than 0
                self.request -=1                                 #decrease request by 1
                print("Rate limit exceeded!", end=" ")           #print rate limit exceeded  
                print("request", self.request)                   #print number of request exhausted
                time.sleep(3)                                  
                self.refill()                                    #call refill function        
          
          
          
        if self.tokens >= tokens:                        #check if tokens is greater than equal to
            self.tokens -= tokens
            if self.request>0:
                self.request -= 1
                self.last_processed_time = datetime.now()      #last processed time of token
                return True
            elif self.request==0 or self.tokens>=self.request:
                self.tokens = self.tokens-self.request
                print(self.tokens)
                return False
            else:
                return False
        else:
            return False
        
        
customer = int(input("Enter the number of customers:"))   #2

for i in range(customer):
    request = int(input("Enter the number of requests for customer {}: ".format(i+1)))
    transmit_rate = 1*60                                           #in seconds
    capacity = transmit_rate
    refill_rate = int(input("Enter the refill rate for customer {}: ".format(i+1)))         #Refilled with tokens per second 
    bucket = Leaking_Bucket(capacity,refill_rate, request)                  #call leaky bucket

    print("tokens:",bucket.tokens)
    print("last refill:", bucket.last_refill)


    last_processed_time = r.get("Last Processed Time:")
    if last_processed_time:
        # Calculate the difference between the current time and last processed time
        time_since_last_processed = datetime.now() - datetime.strptime(last_processed_time, "%H:%M:%S")
        print(time_since_last_processed)
        # Calculate the number of tokens that have been refilled since the last processed time
        tokens_refilled = time_since_last_processed.total_seconds() * refill_rate
        print(tokens_refilled)
        bucket.tokens += tokens_refilled
        bucket.tokens = min(bucket.tokens, capacity)
        
    for i in range(request):
        if bucket.token_consume(1):
            print("Request processed!",end=" ")
            print("tokens",bucket.tokens, end=" ")
            print("request:", bucket.request)
       
    print("Last Processed Time:", bucket.last_processed_time)
    r.set("Last Processed Time:", bucket.last_processed_time.strftime("%H:%M:%S"))
    
        
    
    
   
   
   




"""else:
        print("capacity:",bucket.capacity)
        print("tokens:", bucket.tokens)
        print("refil rate:",bucket.refill_rate)
    
        time_to_refill = (bucket.capacity - bucket.tokens) / bucket.refill_rate
        print("time_to_refill:",time_to_refill)
        print(f"Capacity will be restored in {timedelta(seconds=time_to_refill)}")"""
       
   
         

