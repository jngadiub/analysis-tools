import sys
import os
from optparse import OptionParser
from keras.models import load_model, Model
from argparse import ArgumentParser
from keras import backend as K
import numpy as np
import h5py
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import pandas as pd
import yaml
# To turn off GPU
#os.environ['CUDA_VISIBLE_DEVICES'] = ''

## Config module
def parse_config(config_file) :

    print "Loading configuration from " + str(config_file)
    config = open(config_file, 'r')
    return yaml.load(config)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-m','--model'   ,action='store',type='string',dest='inputModel'   ,default='model/KERAS_check_best_model.h5', help='input model')
    parser.add_option('-i','--input'   ,action='store',type='string',dest='inputFile'   ,default='data/processed-pythia82-lhc13-all-pt1-50k-r1_h022_e0175_t220_nonu_truth.z', help='input file')
    parser.add_option('-t','--tree'   ,action='store',type='string',dest='tree'   ,default='t_allpar_new', help='tree name')
    parser.add_option('-o','--output'   ,action='store',type='string',dest='outputDir'   ,default='data_to_txt/', help='output directory')
    parser.add_option('-c','--config'   ,action='store',type='string', dest='config', default='train_config_threelayer.yml', help='configuration file')
    (options,args) = parser.parse_args()
     
    yamlConfig = parse_config(options.config)

    if os.path.isdir(options.outputDir):
        print "Directory exist: do not create"
    else:
        os.mkdir(options.outputDir)


    # To use one data file:
    h5File = h5py.File(options.inputFile)
    treeArray = h5File[options.tree][()]
    
    # List of features to use
    # List of features to use
    features = yamlConfig['Inputs']
    
    # List of labels to use
    labels = yamlConfig['Labels']

    # Convert to dataframe
    features_df = pd.DataFrame(treeArray,columns=features)
    labels_df = pd.DataFrame(treeArray,columns=labels)
    
    # Convert to numpy array with correct shape
    features_val = features_df.values
    labels_val = labels_df.values

    X_train_val, X_test, y_train_val, y_test = train_test_split(features_val, labels_val, test_size=0.2, random_state=42)
    print X_train_val.shape
    print y_train_val.shape
    print X_test.shape
    print y_test.shape

    #Normalize
    if yamlConfig['NormalizeInputs']:
     scaler = preprocessing.StandardScaler().fit(X_train_val)
     X_test = scaler.transform(X_test) 
             
    modelName = options.inputModel.split('/')[-1].replace('.h5','')
    
    model = load_model(options.inputModel)
    predict_test = model.predict(X_test)

    print "Writing",y_test.shape[1],"predicted labels for",y_test.shape[0],"events in outfile",(options.outputDir+'/'+modelName+'_truth_labels.dat')  
    outf_labels = open(options.outputDir+'/'+modelName+'_truth_labels.dat','w')
    for e in range(y_test.shape[0]):
     line=''
     for l in range(y_test.shape[1]):
      line+=(str(y_test[e][l])+' ')
     outf_labels.write(line+'\n')
    outf_labels.close() 
        
    print "Writing",X_test.shape[1],"features for",X_test.shape[0],"events in outfile",(options.outputDir+'/'+modelName+'_input_features.dat')
    outf_features = open(options.outputDir+'/'+modelName+'_input_features.dat','w')
    for e in range(X_test.shape[0]):
     line=''
     for f in range(len(X_test[e])):
      line+=(str(X_test[e][f])+' ')
     outf_features.write(line+'\n')    
    outf_features.close()  
     
    print "Writing",predict_test.shape[1],"predicted labels for",predict_test.shape[0],"events in outfile",(options.outputDir+'/'+modelName+'_predictions.dat')  
    outf_predict = open(options.outputDir+'/'+modelName+'_predictions.dat','w')
    for e in range(predict_test.shape[0]):
     line=''
     for l in range(predict_test.shape[1]):
      line+=(str(predict_test[e][l])+' ')
     outf_predict.write(line+'\n')
    outf_predict.close() 
