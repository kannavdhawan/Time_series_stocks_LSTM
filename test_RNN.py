import os 
from keras.models import load_model
import pickle
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
from sklearn.metrics import accuracy_score, mean_squared_error, mean_absolute_error
import math

# loading scalar
scalar=pickle.load(open(os.path.join("models/","scalar.pkl"),"rb"))
X_scalar=scalar[0]
y_scalar=scalar[1]

# test data
test=pd.read_csv(os.path.join("data/","test_data_RNN.csv"), index_col=[0])
print(test.head())

X_test=test.iloc[:,0:-1]
y_test=test['Target']


"""scaling with same mean and sd | please uncomment if don't want to use pickkle file of saved scalar..
"""

# from sklearn.preprocessing import MinMaxScaler

# X_scaler_test=MinMaxScaler(feature_range=(0,1))
# y_scaler_test=MinMaxScaler(feature_range=(0,1))

# train=pd.read_csv(os.path.join("data/","train_data_RNN.csv"),index_col=[0])
# X_train=train.iloc[:,:-1]
# y_train=train['Target']

# X_train=X_scaler_test.fit_transform(X_train)
# y_train=y_scaler_test.fit_transform(np.asarray(y_train).reshape(-1,1))

# X_test=X_scaler_test.transform(X_test)
# y_test=y_scaler_test.transform(np.asarray(y_test).reshape(-1,1))

"""
Scaling test data using saved scalar from train_RNN. please uncomment above if don't want to use saved scalar.
"""
X_test=X_scalar.transform(X_test)
y_test=y_scalar.transform(np.asarray(y_test).reshape(-1,1))


print("X_test:\n",X_test[0]," shape:",X_test.shape) #(377,12)
print("y_test:\n",y_test[0]," Shape:",y_test.shape) #(377,1)

#Reshaping to in the desired shape
X_test=np.asarray(X_test).reshape(X_test.shape[0],3,4)
print("Reshaped X_test: \n",X_test.shape)


#  Loading model
lstm_model=load_model(os.path.join("models/","20831774_RNN_model.h5"))
# print(X_test)
# Prediction
y_pred=lstm_model.predict(X_test)
print(y_pred.shape)
loss=lstm_model.evaluate(X_test,y_test)
print("Loss on Test set: ",loss)


y_pred= y_scalar.inverse_transform(y_pred) 
y_test= y_scalar.inverse_transform(y_test)

print(y_pred[0])
print(y_test[0])

rmse_test= math.sqrt(mean_squared_error(y_test, y_pred[:,0]))
print('Test RMSE: ',rmse_test)

mse_test=mean_squared_error(y_test, y_pred)
print('Test MSE: ',mse_test)

mae_test=mean_absolute_error(y_test, y_pred)
print('Test MAE: ',mae_test)


plt.figure(figsize=(8,8))
plt.plot(y_pred, "r")
plt.plot(y_test,"g")
plt.legend(["Predicted Price","Real Price"])
plt.xlabel("Days")
plt.ylabel("Price")
plt.savefig(os.path.join("data/","True_Predicted_plot_test.png"))
plt.show()