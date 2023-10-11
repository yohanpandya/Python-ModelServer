import torch
from collections import OrderedDict
import threading
import modelserver_pb2_grpc, modelserver_pb2

import grpc
from concurrent import futures
class ModelServer(modelserver_pb2_grpc.ModelServerServicer):
    def __init__(self):
        self.p = PredictionCache();
    def SetCoefs(self, request, context):
        try:
            coefs = torch.Tensor(request.coefs)
            result = self.p.SetCoefs(coefs)
            print("coefs Worked")
            return modelserver_pb2.SetCoefsResponse(error = "")
        except:
            print("coefs Didn't work")
            return modelserver_pb2.SetCoefsResponse(error = "failed")
    def Predict(self, request, context):
        try:
            X = torch.Tensor(request.X)
            #print(X.shape)
            
            result = self.p.Predict(X)
            print("predict worked")
            return modelserver_pb2.PredictResponse(y=result[0],hit = result[1], error = "")
        except:
            print("predict didntwork")
            return modelserver_pb2.PredictResponse(error = "failed")

class PredictionCache:
    #lock = threading.Lock()
    def __init__(self):
        self.lock = threading.Lock()
        self.coefs = None
        self.cache = OrderedDict()
    def SetCoefs(self,coefs):
        
        self.lock.acquire()
        self.coefs = coefs
        self.cache.clear()
        self.lock.release()
    def Predict(self,X):
        X = X.flatten(); 
        if self.coefs is not None:
            lock= threading.Lock()        
            self.lock.acquire()
           # print ("lock acquired 1")
            X = torch.round(X,decimals = 4)
           # print("torch round worked")
       # Convert the rounded X to a tuple for caching
            if isinstance(X, torch.Tensor):# and len(X.shape)==1:
            #    print ("isinstance")
                if X.shape[0]==self.coefs.shape[0]:
             #       print("X shape")
                    X_tuple = tuple(X.flatten().tolist())
              #      print("tuple recieved")
                    if(X_tuple in self.cache):
               #         print("tuple in cache")
                        self.lock.release()
                        return self.cache[X_tuple], True
                #    print("tuple not in cache")
                    y = X @ self.coefs
                   # y = torch.round(y,decimals = 5)
                    if(len(self.cache)>=10):
                     #   print("cache is full")
                        self.cache.popitem(last = False)
                      #  print("item popped")
                    self.cache[X_tuple] = y
                   # print("cached new item")
                    self.lock.release()
                   # print("released lock")
                    return y, False
                    

                else:
                    self.lock.release()
                    print("failed at shape check")
                    raise ValueError("didn't work")
            else:
                print ("failed at isinstance tensor")
                self.lock.release()
                raise ValueError("didn't work")
        print("Beginning didn't work")
            
        raise ValueError("didn't work")

server = grpc.server(futures.ThreadPoolExecutor(max_workers=4), options=(('grpc.so_reuseport', 0),))
modelserver_pb2_grpc.add_ModelServerServicer_to_server(ModelServer(), server)
server.add_insecure_port("[::]:5440", )
server.start()
server.wait_for_termination()
