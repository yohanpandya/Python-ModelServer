import modelserver_pb2_grpc,modelserver_pb2

import grpc
import sys
import threading
import time
import csv
#channel = grpc.insecure_channel("localhost:5440")
#stub = modelserver_pb2_grpc.ModelServerStub(channel)
#resp1 = stub.SetCoefs(modelserver_pb2.SetCoefsRequest(coefs = [1,2,3]))
#resp2 = stub.Predict(modelserver_pb2.PredictRequest(X = [1,2,3]))

class Client:
    def __init__(self,port, coefs, filenames):
        #initialized global vars
        self.channel = grpc.insecure_channel("localhost:"+port)
        print("channel started at 5440")
        self.coefs = coefs
        self.filenames = filenames
        self.stub = modelserver_pb2_grpc.ModelServerStub(self.channel)
        self.totalhits = 0
        self.totalcalls = 0
        self.lock = threading.Lock()
        self.finalhitrate = 0;
        self.fileIndex = 0;
    def runCoefs(self):
        #set coefs in protobuf file
        
        coefsResp = self.stub.SetCoefs(modelserver_pb2.SetCoefsRequest(coefs = self.coefs))
        print("coefs",self.coefs,"have been set")
    def makeThreads(self):
        #initialize threads array
        threads = []
        for filename in self.filenames:
            thread = threading.Thread(target = self.runPredict,args = (filename,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            
            thread.join()
        self.finalhitrate = float(self.totalhits)/float(self.totalcalls)
        print ("FINAL HIT RATE:",self.finalhitrate)
    def runPredict(self, filename):
        self.lock.acquire()
        print("acquiring lock for thread",self.filenames[self.fileIndex])
        self.fileIndex+=1
        hits = 0
        calls = 0
        with open(filename,"r") as file:
            reader = csv.reader(file)
            for row in reader:
                values = list(map(float,row))
                resp =self.stub.Predict(modelserver_pb2.PredictRequest(X = values))
                if resp.hit:
                #    print("hit")
                    hits+=1
               # print("call++")
                calls+=1
      #  return hits, total
        
            self.totalhits += hits
            self.totalcalls +=calls
        self.lock.release()
class main:
    #read in arguments
    print("client started")
    print("the purpose of this client is to call methods in server.py, which will return metrics that are useful to us. The client will start by initializing the coefs (based on the input) via the protobuf. Next, the client will initialize threads for every file inputted. The client will then secure a lock and call the predict method in server.py via the protobuf. The server will then run Predict, which will look through the LRU cache and determine whether the prediction is a hit or a miss. The client will then record the overall hit rate and return it.\n")
    print("after this run, feel free to change the coefs and use your own csv files.")
    port = sys.argv[1]
    coefs =list(map(float,(sys.argv[2]).split(',')))
    filenames = sys.argv[3:]
    
    c = Client(port,coefs,filenames)
    c.runCoefs()
    c.makeThreads()
