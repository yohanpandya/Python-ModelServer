Dockerfile, server.py, client.py and modelserver.proto create a client-server system for serving machine learning models via gRPC. Clients can connect to the server, set model coefficients, and make predictions using data from CSV files. The server caches predictions to improve performance, and the client reports the final prediction success rate after all threads have finished making predictions. This system can be used for real-time prediction services and machine learning model deployment.

How to run:
1) clone repository
2) build Dockerfile using: docker build -t p3 . (this will launch the protobuf and create .pb2 files)
3) start server.py: python3 server.py
4) open new terminal window
5) run client using the following form: python3 client.py 5440 <COEF> <THREAD1-WORK.csv> <THREAD2-WORK.csv> ...
   The port is set to 5440. You can use the provided workload_.csv files in the workload directory, So you can run      the client using: python3 client.py 5440 "1.0,2.0,3.0" workload/workload1.csv workload/workload2.csv
6) Feel free to use your own csv files and coefs. Thanks!

More detailed explanation: 
The server.py program uses grpc to start a server, in which a client can specify coefficients and data to determine what percent of their data can be cache in a LRU cache of size 10. server.py contains 2 classes: ModelServer and PredictionCache. ModelServer contains methods that the protobuf will call on, which in turn call on methods in PredictionCache. The methods SetCoefs and Predict exist in both ModelServer and PredictionCache (but MS calls the methods in PC). The following explanations are for SetCoefs and Predict in PC. SetCoefs initializes a global variable "self.coefs" according to what the user enters, and then clears the cache, as new coefs will likely result in new values in the cache. Predict begins by flattening the current row (X) and making sure that the dimensions of the current row match with the coefs. It then checks to see if the tuple is already in the cache. If it is, it returns True along with the prediction. If not, it computes Y, the prediction, by multiplying X by coefs. After poppinf the LRU item from the cache (if necessary), it inserts Y, and returns y,False.

The Client uses this information (specifically the true/false) to determine whether or not there was a hit, and returns the hit rate.
