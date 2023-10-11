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
        self.channel = grpc.insecure_channel("localhost:"+port)
        self.coefs = coefs
        self.filenames = filenames
        self.stub = modelserver_pb2_grpc.ModelServerStub(self.channel)
        self.totalhits = 0
        self.totalcalls = 0
        self.lock = threading.Lock()
        self.finalhitrate = 0;
    def runCoefs(self):
        coefsResp = self.stub.SetCoefs(modelserver_pb2.SetCoefsRequest(coefs = self.coefs))
    def makeThreads(self):
        threads = []
        for filename in self.filenames:
            thread = threading.Thread(target = self.runPredict,args = (filename,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        self.finalhitrate = float(self.totalhits)/float(self.totalcalls)
        print (self.finalhitrate)
    def runPredict(self, filename):
        self.lock.acquire()
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
            print("totalhits now: ",self.totalhits)
            self.totalcalls +=calls
            print("totalcalls now: ",self.totalcalls)
        self.lock.release()
class main:

    port = sys.argv[1]
    coefs =list(map(float,(sys.argv[2]).split(',')))
    filenames = sys.argv[3:]
    c = Client(port,coefs,filenames)
#    print(c.channel,c.coefs,c.filenames)
    c.runCoefs()
    c.makeThreads()
   # finalhitrate = float(c.totalhits)/float(c.totalcalls)
   # print (finalhitrate)
