# Imports
import pandas as pd
import numpy as np
import random
import math
import pickle
import os 
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from sklearn.metrics import accuracy_score, mean_squared_error,mean_absolute_error
from tensorflow.keras.models import Sequential,load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout

from matplotlib import pyplot as plt
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
tf.random.set_seed(1337) # setting seed 
random.seed(1337)
# from keras.utils.vis_utils import plot_model
from utils import data_load , train_metrics_plot, metric_errors

#Loading the dataset
def raw_data(path):
    """

    Loads the dataset with stock prices from csv.

    Args:
        path(os path)

    Arguments:
        path(os path): path to the csv from the data folder

    Returns: 
        data_no_close: A numpy array with float values with no 'close' column.

    """
    print("Loading Raw data..")

    # path='https://raw.githubusercontent.com/kannavdhawan/Time_series_stocks_LSTM/master/q2_dataset.csv?token=AHMAKJAQPICJFWARH35B4US7DEIJE'

    data=pd.read_csv(path)
    # print("Checking head..:\n",data.head(3))

    data_no_close=data.drop([" Close/Last"],axis=1)             # Dropping the Close/Last column 
    # print("No close ds test..:\n",data_no_close.head(3))

    data_no_close['Date']=pd.to_datetime(data_no_close['Date']) # converting date from str to datetime
    # print("Checking ds..:\n",data_no_close.head(3))

    data_no_close=data_no_close.sort_values('Date')             # Sorting df by date
    # print("sorted date ds..:\n",data_no_close)

    data_no_close=data_no_close.reset_index(drop=True)          # Reseting the reversed index after sorting.
    # print("Reset index ds..:\n",data_no_close.head(3))
    """
    calculating the average percentage change for better analysis in the end.

    """
    
    # ma= data_no_close[' Open'].rolling(window=3).mean()

    # print(data_no_close[' Open'].pct_change().mean()*1256) #1.3296575036506153
    

    data_no_close=data_no_close.iloc[:,1:].values.astype('float32')     #converting into np array and 'float32'.  {Already floats!~Volume}
    # print("np array floats..:\n",data_no_close[0])
    # print("Shape np array=> ",data_no_close.shape)
    
    return data_no_close


# Generating the features
def feature_gen(data_values,size):
    """
    Generates the features for lstm with the required window size for time series input. 

    Args:
        data_values(np array)
        size(int)

    Arguments:
        data_values(np array): numpy array returned by load_data with float values. 
        size(int): window size
    
    Returns: 
        features(list): [1256, 3, 4]
        targets(list): [1256]

    """
    print("Feature generation..")
    features=[]
    targets=[]
    old_days=size
    for current_day in range(old_days,len(data_values)):
        features.append(data_values[current_day-old_days:current_day,:])  #[1259*(3,4)shape]
        targets.append(data_values[current_day][1])

    # print("type(features):",type(features))           #list
    # print("type(features[0])",type(features[0]))      #numpy array
    # print("shape check features: ",np.asarray(features).shape) # (1256, 3, 4)
    # print("shape check target: ",np.asarray(targets).shape)    # (1256,)
    return features,targets

def split(features,targets):
    """
    splits the data and stores in a csv.
    
    Args:
        features(list)
        targets(list)
    
    Attributes:

        features(list): list generated by the feature_gen having shape [1256,3,4]. list of numpy arrays of shape (3,4).
        targets(list): list having 1256 elements

    Returns: 
        Saves the csv files in data/ directory for tarin and test data with labels.

    """
    print("Splitting..")

    # shuffling the dataset
    zipped_f_t=list(zip(features,targets))
    random.shuffle(zipped_f_t)                           #shuffling the zipped object with features and labels
    tr_sz=int(0.70*len(zipped_f_t))                      # getting size for splitting the dataset into train and test
    train,test = zipped_f_t[:tr_sz], zipped_f_t[tr_sz:]  # splitting the zipped object list
    
    
    """
    ** train,test : list of truple of numpy array of shape (None,3,4) and int target.

    ** This preprocessing is done to store the data in a csv file ..
    
        * Each feature set below is a tuple with features of shape (3,4)
            and an int value for target at first index.
        * we flatten the features at 0th index from shae (3,4) to 12 for each element/input. 
        
    """
    X_train=pd.DataFrame([feature_set[0].ravel() for feature_set in train])
    X_test=pd.DataFrame([feature_set[0].ravel() for feature_set in test])
    y_train=pd.DataFrame([feature_set[1] for feature_set in train])
    y_test=pd.DataFrame([feature_set[1] for feature_set in test])

    # print((X_train).head(2))
    # print((X_test).head(2))
    # print((y_train).head(2))
    # print((y_test).head(2))

    # Creating dataframes 

    train=X_train.copy()        
    train['Target']=y_train     # concatinating labels
    
    test=X_test.copy()
    test['Target']=y_test       # concatinating labels

    # print(train.head(3))
    # print(test.head(3))

    train.to_csv(os.path.join("data/","train_data_RNN.csv")) # saving csv of train and test in data/
    test.to_csv(os.path.join("data/","test_data_RNN.csv"))



"""
Time series csv's created above
"""


# train_data_RNN.csv is loaded below at function calls using utils "data_load" function. 

def normalize(X_train,y_train):
    """
    Normalizing the dataset using Minmaxscalar and saving the objects in a pickle file for saving the mean and stand dev. 
    Reshapes the dataset into time series of (879,3,4)to be fed to lstm.
    
    Args:
        X_train(dataframe)
        y_train(dataframe)

    Attributes:
        X_train(dataframe): Dataframe containing train features
        y_train(dataframe): Series containing train labels

    Returns: 
        X_train: Reshaped time series numpy array of shape (879,3,4) readyto be fed into our RNN.
        y_train: 2- dimensional numpy array with shape (879,1)
    """
    print("Normalizing..")
    #scaling 
    scalar=[]
    X_train_scalar=MinMaxScaler(feature_range=(0,1))    #setting the range between 0 and 1. scalar for features.
    y_train_scalar=MinMaxScaler(feature_range=(0,1))    # scalar ob for label

    X_train=X_train_scalar.fit_transform(X_train)       # Fitting the ob with train features
    y_train=y_train_scalar.fit_transform(np.asarray(y_train).reshape(-1,1)) # To make it 2D, reshaping ..

    scalar.extend([X_train_scalar,y_train_scalar])      # serialized objects to be saved in pkl file
    pickle.dump(scalar,open(os.path.join("models/","scalar.pkl"), "wb" ))   # writing pickle file
    
    X_train=np.asarray(X_train).reshape(X_train.shape[0],3,4)    #Reshaping the dataset X_train to 3 dimensional numpy array for lstm
   
    # print("X_train shape: ",X_train.shape)
    # print("y train shape:",y_train.shape)
    return X_train,y_train,X_train_scalar,y_train_scalar

def LSTM_RNN(add_dense_32,add_dense_20,add_dense_10,opt,base=True):
    """LSTM Model odel Architecture
    Agrs:
        add_dense_32(bool)
        add_dense_20(bool)
        add_dense_10(bool)
        opt(str)

    Arguments:
        add_dense_32(bool): If True, adding a dense layer with 32 units after 2 hidden layers.
        add_dense_20(bool): If True, adding a dense layer with 20 units.
        add_dense_10(bool): If True, adding a dense layer with 10 units.
        opt(str): A string with optimizer name.

    Returns: 
        model(ob): compiled model 
    """
    print("Training..")

    if base:

        model = Sequential()
        model.add(LSTM(64, input_shape=(3,4)))
        # model.add(LSTM(units=32))
        # model.add(Dense(10))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam',metrics=['mae'])
    else:
        model= Sequential()

        model.add(LSTM(units=32, return_sequences= True, input_shape=(3,4)))  # Hidden lstm layer with 32 units.

        model.add(LSTM(units=10, return_sequences= False))                    # Hidden lstm layer with 10 units.


        if add_dense_32:        
            model.add(Dense(units=32))                                        # A fully connected dense layer with 32 units
        
        if add_dense_20:
            model.add(Dense(units=20))                                        # A fully connected dense layer with 20 units
        
        if add_dense_10:
            model.add(Dense(units=10))                                        # A fully connected dense layer with 10 units

        model.add(Dense(units=1))                                             # output fully connected dense layer with 1 unit.
        model.compile(loss='mean_squared_error', optimizer=opt,metrics=['mae'])     # metrics as mse, opt as sdg and adam during calls, loss as mse.
        
    print(model.summary())                                                # printing model summary
        
        # plot_model(model, to_file='data/mlp_base.png', show_shapes=True, show_layer_names=True)
    return model 
    


if __name__ == "__main__": 


    """
    //CALLS FOR CREATING TIME SERIES DATASET//
    Please uncomment if you want to re split and re create the data.
    """

    # data_no_close=raw_data(os.path.join("data/","q2_dataset.csv"))          # Loading dataset from csv


    # win_size=3
    # features,targets=feature_gen(data_no_close,win_size)                    # Generating features


    # split(features,targets)                                                 # Preprocessing and saving preprocessed dataset


    
    # Loading prerocessed data from utils call
    X_train,y_train=data_load(os.path.join("data/","train_data_RNN.csv"))

    # Normalizing the train dataset and reshaping.
    X_train,y_train,X_train_scalar,y_train_scalar=normalize(X_train,y_train)

    # Training.. 
                    #Best model is uncommented..
    model=LSTM_RNN(add_dense_32=False,add_dense_20=False,add_dense_10=False,opt='adam',base=True)           #Architecture-1 
        
    # model=LSTM_RNN(add_dense_32=False,add_dense_20=False,add_dense_10=False,opt='adam',base=False)        #Architecture-2
    # model=LSTM_RNN(add_dense_32=False,add_dense_20=False,add_dense_10=False,opt='sgd',base=False)         #Architecture-3
    # model=LSTM_RNN(add_dense_32=True,add_dense_20=False,add_dense_10=False,opt='adam',base=False)         #Architecture-4
    # model=LSTM_RNN(add_dense_32=True,add_dense_20=True,add_dense_10=False,opt='adam',base=False)          #Architecture-5

    # model=LSTM_RNN(add_dense_32=True,add_dense_20=True,add_dense_10=True,opt='adam',base=False)           #Architecture-6


    # history=model.fit(X_train, y_train, epochs=100, batch_size=50, verbose=2)                             # on second model only   
    # history=model.fit(X_train, y_train, epochs=50, batch_size=10, verbose=2)                              # on second model only   

    history=model.fit(X_train, y_train, epochs=100, batch_size=10, verbose=2) #Fitting the model

    model.save(os.path.join("models/","20831774_RNN_model.h5"))               #Saving the fitted model

    train_metrics_plot(history)                                               #Plotting the Training loss and MSE

    loss=model.evaluate(X_train,y_train)                                      #Evaluating the model on train data for overall loss.
    print("\n\nLoss and MAE on Train set: ",loss)

    y_pred_train= model.predict(X_train)                                      #To get the overall metric results while training

    # print("y_pred_train:",y_pred_train.shape) #np array (879,1)
    # print("y_train:", y_train.shape)          #np array (879,1)


    y_pred_train = y_train_scalar.inverse_transform(y_pred_train)    #Inverting both y_train and y_pred_train to get real values. 
    y_train = y_train_scalar.inverse_transform(y_train) 

    print("\n\nRandom Testing for Training data \n\nPredicted: ",y_pred_train[0])
    print("Target: ",y_train[0])

    # MAE,MSE,RMSE from utils call for training data 
    print("\n\nDifferent Losses after inverting the prices to real scale for Train Data: \n")
    metric_errors(y_train,y_pred_train,flag="Train")