import os
import numpy as np
import pandas as pd
import random 
import copy
import matplotlib.pyplot as plt
import datetime as dt
from sklearn.metrics import mean_absolute_error as MAE
from sklearn import linear_model as lm
from keras.models import Sequential
from keras.layers import Activation, Dense,Bidirectional,Dropout,LSTM

original_data= pd.read_excel('/kaggle/input/YES_BANK.xlsx',
header=None,
index_col=False,
keep_default_na=True,names=['Date','Open','High','Low','Close','Volume']
)

original_data.shape

original_data['Date'] = pd.to_datetime(original_data['Date'])
original_data.head()



def datasetpreparation(original_data):
  data_split = int(len(original_data)*0.8)
  data1 = original_data.drop(['Date','Volume'],axis = 1)
  data1.head()
  data1_input = []
  for i in range(len(data1) - 4):
    list1 = data1[i:i+5].values.tolist() #each training data point consists of list of stock price of 5 days (last day ) and training output for that point is stock price for next day
    data1_input.append(list1)
  #print(np.array(data4_input).shape)
  #(data4_input)
  data1_output = data1.ix[5:,:]
  #data4_output
  train1_input = np.array(data1_input[0:data_split])
  train1_output = np.array(data1_output[0:data_split])
  print(train1_input.shape)
  print(train1_output.shape)
  test1_input = np.array(data1_input[data_split:]) #similar to training data in continuation the testing data point also contain the test data for this day + 4 more days and test output for next day, 
  test1_output = np.array(data1_output[data_split:])
  print(test1_input.shape)
  print(test1_output.shape)
  return train1_input,train1_output,test1_input,test1_output

def LSTMmodel():
  model1 = Sequential()
  model1.add(Bidirectional(LSTM(50, activation='relu'), input_shape=(5, 4)))
  model1.add(Dropout(0.25))
  model1.add(Dense(4))
  model1.compile(optimizer='adam', loss='mse')
  model1.summary()
  return model1

LSTMmodel()

def modeltrain(train1_input,train1_output,model1):
  #train_input,train_output,test1_input,test1_output = datasetpreparation(original_data)
  #model = LSTMmodel 
  history = model1.fit(train1_input, train1_output, epochs=500, verbose=1)
  model1.save('project_model.h5')

def evaluateval(model1,train1_input,train1_output):
  #train_input,train_output,test1_input,test1_output = datasetpreparation(original_data)
  predict = model1.predict(train1_input)
  predict1 = pd.DataFrame(predict)
  output = pd.DataFrame(train1_output)
  for i in range(4):
    plt.plot(predict1.ix[:,i])
    plt.plot(output.ix[:,i])
    plt.show()

"""It is interesting to note how testing is being done.
Say you are at first day of testing what will you have in the testing data input for the first day, it should be last training point that will give output for the first day of the testing data. Right? But wait we wanted to give more weights to last 20 days so that it can capture the dependencies. So to do this I need to train my data on last 20 days of training data which is covered by last 16 data points,because last data point in training set contains the infor of last 5 days we need 15 more days info so we pass last 16 days in the feedback loop. 
Now you run the model and see some output and then stock market gets closed for that day and you also know the actual value for that day.

Now prediction for next day happen as follows:

As you already know todays closing/opening/high /low we append it to the data set containing last 19 days data , basically appending to training data and extracting data for last 20 days and again predicting through the feedback loop.

**since you have alread done the last day for training data the first point of the test data you start from appending the test data for that day and follow**
"""

def test(model1,train1_input,train1_output,test1_input,test1_output,i):
  input = test1_input[i].reshape(1,5,4)
  train1_input = np.concatenate((train1_input,input),axis = 0)
  output = test1_output[i].reshape(1,4)
  prediction = model1.predict(input)
  train1_output = np.concatenate((train1_output,output),axis = 0)
  return prediction,train1_input,train1_output

def feedback(model1,train1_input,train1_output,test1_input,i):
  model1.fit(train1_input[-16:-1], train1_output[-16:-1], epochs=10, verbose=1) 
  prediction = model1.predict(test1_input[i].reshape(1,5,4))
  return prediction

def runprograme(original_data):
  train1_input,train1_output,test1_input,test1_output = datasetpreparation(original_data)
  model1 = LSTMmodel()
  modeltrain(train1_input,train1_output,model1)
  from keras.models import load_model
  model1 = load_model('project_model.h5')
  evaluateval(model1,train1_input,train1_output)
  pred=[]
  for i in range(len(test_df)):
     pred,train1_input,train1_output = test(model1,train1_input,train1_output,test1_input,test1_output,i)
     prediction = feedback(model1,train1_input,train1_output,test1_input,i)
   pred.append(prediction)
   for i in range(4):                           #These loops are nothing but the open / close /high /low predictions in pred.
      plt.plot(pred.ix[:,i])
      plt.plot(test_output.ix[:,i])
      plt.show()

runprograme(original_data)

