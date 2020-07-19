import pandas as pd
import matplotlib.pyplot as plt
import os 
import math
from sklearn.metrics import accuracy_score, mean_squared_error,mean_absolute_error


def main():
    print("inside main ")

# print("l-1")

def data_load(data_path):
    """
    Loading preprocessed dataset 
    """
    print("Loading dataset..")
    dataset=pd.read_csv(data_path,index_col=[0])
    X,y=dataset.iloc[:,:-1],dataset['Target']       #separating data and labels
    return X,y

#history plot
def train_metrics_plot(history):
    """
    plots the Training Loss and training MSE at each epoch..
    """
   
    Train_MSE=history.history['mse']                    #Get traning loss from hist_object.history
    Train_Loss=history.history['loss']
    
    plot_metrics=[]
    plot_metrics.extend([Train_MSE,Train_Loss])
    for metric in plot_metrics:
            
        plt.figure(figsize=(8,7))
        if metric==Train_MSE:
            metric_name="Training MSE"
            plt.plot(metric,'r')
            plt.xlabel("Epochs")
            plt.ylabel(metric_name)
            plt.title(metric_name+" at each epoch")
            plt.legend([metric_name])
            plt.show()
            name=metric_name+".png"
            plt.savefig(os.path.join("data/",name))
        elif metric==Train_Loss:
            metric_name="Training Loss"
            plt.plot(metric,'r')
            plt.xlabel("Epochs")
            plt.ylabel(metric_name)
            plt.title(metric_name+" at each epoch")
            plt.legend([metric_name])
            plt.show()
            name=metric_name+".png"
            plt.savefig(os.path.join("data/",name))

def metric_errors(real,pred):
    """ calculate root mean squared error.
    """
    rmse_train= math.sqrt(mean_squared_error(real,pred))
    print("RMSE for training data:",rmse_train)

    mse_train= mean_squared_error(real,pred)
    print('MSE for training data: ',mse_train)

    mae_train=mean_absolute_error(real,pred)
    print('MAE for training data: ',mae_train)


if __name__ == "__main__":
    main()