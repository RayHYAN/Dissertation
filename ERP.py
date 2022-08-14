"""
 Sample script using EEGNet to classify Event-Related Potential (ERP) EEG data
 from a four-class classification task, using the sample dataset provided in
 the MNE [1, 2] package:
     https://martinos.org/mne/stable/manual/sample_dataset.html#ch-sample-data
   
 The four classes used from this dataset are:
     LA: Left-ear auditory stimulation
     RA: Right-ear auditory stimulation
     LV: Left visual field stimulation
     RV: Right visual field stimulation

 The code to process, filter and epoch the data are originally from Alexandre
 Barachant's PyRiemann [3] package, released under the BSD 3-clause. A copy of 
 the BSD 3-clause license has been provided together with this software to 
 comply with software licensing requirements. 
 
 When you first run this script, MNE will download the dataset and prompt you
 to confirm the download location (defaults to ~/mne_data). Follow the prompts
 to continue. The dataset size is approx. 1.5GB download. 
 
 For comparative purposes you can also compare EEGNet performance to using 
 Riemannian geometric approaches with xDAWN spatial filtering [4-8] using 
 PyRiemann (code provided below).

 [1] A. Gramfort, M. Luessi, E. Larson, D. Engemann, D. Strohmeier, C. Brodbeck,
     L. Parkkonen, M. Hämäläinen, MNE software for processing MEG and EEG data, 
     NeuroImage, Volume 86, 1 February 2014, Pages 446-460, ISSN 1053-8119.

 [2] A. Gramfort, M. Luessi, E. Larson, D. Engemann, D. Strohmeier, C. Brodbeck, 
     R. Goj, M. Jas, T. Brooks, L. Parkkonen, M. Hämäläinen, MEG and EEG data 
     analysis with MNE-Python, Frontiers in Neuroscience, Volume 7, 2013.

 [3] https://github.com/alexandrebarachant/pyRiemann. 

 [4] A. Barachant, M. Congedo ,"A Plug&Play P300 BCI Using Information Geometry"
     arXiv:1409.0107. link

 [5] M. Congedo, A. Barachant, A. Andreev ,"A New generation of Brain-Computer 
     Interface Based on Riemannian Geometry", arXiv: 1310.8115.

 [6] A. Barachant and S. Bonnet, "Channel selection procedure using riemannian 
     distance for BCI applications," in 2011 5th International IEEE/EMBS 
     Conference on Neural Engineering (NER), 2011, 348-351.

 [7] A. Barachant, S. Bonnet, M. Congedo and C. Jutten, “Multiclass 
     Brain-Computer Interface Classification by Riemannian Geometry,” in IEEE 
     Transactions on Biomedical Engineering, vol. 59, no. 4, p. 920-928, 2012.

 [8] A. Barachant, S. Bonnet, M. Congedo and C. Jutten, “Classification of 
     covariance matrices using a Riemannian-based kernel for BCI applications“, 
     in NeuroComputing, vol. 112, p. 172-178, 2013.


 Portions of this project are works of the United States Government and are not
 subject to domestic copyright protection under 17 USC Sec. 105.  Those 
 portions are released world-wide under the terms of the Creative Commons Zero 
 1.0 (CC0) license.  
 
 Other portions of this project are subject to domestic copyright protection 
 under 17 USC Sec. 105.  Those portions are licensed under the Apache 2.0 
 license.  The complete text of the license governing this material is in 
 the file labeled LICENSE.TXT that is a part of this project's official 
 distribution. 
"""

import numpy as np
import random

# mne imports
import mne
from mne import io
from mne.datasets import sample

# EEGNet-specific imports
from eegmodels.EEGModels import EEGNet, ShallowConvNet, DeepConvNet
import tensorflow as tf
from tensorflow.keras import utils as np_utils
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import backend as K

# PyRiemann imports
from pyriemann.estimation import XdawnCovariances
from pyriemann.tangentspace import TangentSpace
from pyriemann.utils.viz import plot_confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

# tools for plotting confusion matrices
from matplotlib import pyplot as plt

# Ray import
import Ray.data_load_save as data_load_save
import Ray.basic_fun as basic_fun

# while the default tensorflow ordering is 'channels_last' we set it here
# to be explicit in case if the user has changed the default ordering
K.set_image_data_format('channels_last')

##################### Process, filter and epoch the data ######################
data_path = sample.data_path()

# Set parameters and read data
modelNet = 'EEGNet' # EEGNet, ShallowConvNet, DeepConvNet
EEG_data, _ = data_load_save.set_up(isE4 = False)
event_id = dict(familiar_music=1, wildlife_video=2, family_inter=3, Tchaikovsky=4, exper_video=5)
# event_id = dict(familiar_music=1, wildlife_video=2, family_inter=3, Tchaikovsky=4)
tmin, tmax = -0., 1
fs, windows, interval = 250, 4, 250 # windows: second, interval: num of data_point
kernels, chans, samples = 1, 7, windows * fs

# train: test: validate = 6:2:2
train_part_list, test_part_list, val_part_list = basic_fun.gen_train_test_valid(EEG_data)
train_test_val_data = {
    'train': [],
    'test': [],
    'val': []
}

# set a limit to balance data
train_test_val_data_num = {
    'train': {1:0, 2:0, 3:0, 4:0, 5:0},
    'test': {1:0, 2:0, 3:0, 4:0, 5:0},
    'val': {1:0, 2:0, 3:0, 4:0, 5:0},
}
train_test_val_class_num_limit = {
    'train': 2000,
    'test': 400,
    'val': 400
}

for partID in EEG_data.keys():
    if partID in train_part_list:
        dataset = 'train'
    elif partID in test_part_list:
        dataset = 'test'
    else: dataset = 'val'

    for event in event_id.keys():
        if EEG_data[partID].event_details.check_has_event(event) and EEG_data[partID].event_details.check_event_has_start_and_end(event):
            event_data = EEG_data[partID].get_EEG_by_event(event)
            for start in range(0, len(event_data[0]) - samples, interval):
                if train_test_val_data_num[dataset][event_id[event]] >= train_test_val_class_num_limit[dataset]:
                    break
                data_point_metric = []
                for channel in event_data:
                    data_point_metric.append([data_point for data_point in channel[start: start+samples]])
                train_test_val_data[dataset].append((data_point_metric, event_id[event]))
                train_test_val_data_num[dataset][event_id[event]] += 1

print(train_test_val_data_num)

random.shuffle(train_test_val_data['train'])
random.shuffle(train_test_val_data['test'])
random.shuffle(train_test_val_data['val'])

Y_train = np.array([item[1] for item in train_test_val_data['train']], dtype=np.int32)
Y_test = np.array([item[1] for item in train_test_val_data['test']], dtype=np.int32)
Y_validate = np.array([item[1] for item in train_test_val_data['val']], dtype=np.int32)
X_train = np.array([item[0] for item in train_test_val_data['train']], dtype=float)
X_test = np.array([item[0] for item in train_test_val_data['test']], dtype=float)
X_validate = np.array([item[0] for item in train_test_val_data['val']], dtype=float)

############################# EEGNet portion ##################################

# convert labels to one-hot encodings.
Y_train      = np_utils.to_categorical(Y_train-1)
Y_validate   = np_utils.to_categorical(Y_validate-1)
Y_test       = np_utils.to_categorical(Y_test-1)

print(X_train.shape)
print(X_test.shape)
print(X_validate.shape)
print(Y_train.shape)
print(Y_test.shape)
print(Y_validate.shape)

# convert data to NHWC (trials, channels, samples, kernels) format. Data 
# contains 60 channels and 151 time-points. Set the number of kernels to 1.
X_train      = X_train.reshape(X_train.shape[0], chans, samples, kernels)
X_validate   = X_validate.reshape(X_validate.shape[0], chans, samples, kernels)
X_test       = X_test.reshape(X_test.shape[0], chans, samples, kernels)
   
print('X_train shape:', X_train.shape)
print(X_train.shape[0], 'train samples')
print(X_test.shape[0], 'test samples')

print(modelNet)
if modelNet == 'EEGNet':
# configure the EEGNet-8,2,16 model with kernel length of 32 samples (other 
# model configurations may do better, but this is a good starting point)
    model = EEGNet(nb_classes = len(event_id.keys()), Chans = chans, Samples = samples, 
                dropoutRate = 0.5, kernLength = 32, F1 = 8, D = 2, F2 = 16, 
                dropoutType = 'Dropout')
elif modelNet == 'ShallowConvNet':
    model = ShallowConvNet(nb_classes = len(event_id.keys()), Chans = chans, Samples = samples, 
               dropoutRate = 0.5)
elif modelNet == 'DeepConvNet':
    model = DeepConvNet(nb_classes = len(event_id.keys()), Chans = chans, Samples = samples, 
               dropoutRate = 0.5)
else:
    print('Wrong model net name!')
    exit()

# compile the model and set the optimizers
model.compile(loss='categorical_crossentropy', optimizer='adam', 
              metrics = ['accuracy'])

# count number of parameters in the model
numParams    = model.count_params()    

# set a valid path for your system to record model checkpoints
tmp_file_path = r'./Dissertation/eegmodels/examples/tmp/checkpoint.h5'
checkpointer = ModelCheckpoint(filepath=tmp_file_path, verbose=1,
                               save_best_only=True)

###############################################################################
# if the classification task was imbalanced (significantly more trials in one
# class versus the others) you can assign a weight to each class during 
# optimization to balance it out. This data is approximately balanced so we 
# don't need to do this, but is shown here for illustration/completeness. 
###############################################################################

# the syntax is {class_1:weight_1, class_2:weight_2,...}. Here just setting
# the weights all to be 1
class_weights = {i:1 for i in range(len(event_id.keys()))}
# class_weights = {0:1, 1:1, 2:1, 3:1}

################################################################################
# fit the model. Due to very small sample sizes this can get
# pretty noisy run-to-run, but most runs should be comparable to xDAWN + 
# Riemannian geometry classification (below)
################################################################################
fittedModel = model.fit(X_train, Y_train, batch_size = 16, epochs = 300, 
                        verbose = 2, validation_data=(X_validate, Y_validate),
                        callbacks=[checkpointer], class_weight = class_weights)

# load optimal weights
model.load_weights(tmp_file_path)

###############################################################################
# can alternatively used the weights provided in the repo. If so it should get
# you 93% accuracy. Change the WEIGHTS_PATH variable to wherever it is on your
# system.
###############################################################################

# WEIGHTS_PATH = './EEGNet-8-2-weights.h5'
# model.load_weights(WEIGHTS_PATH)

###############################################################################
# make prediction on test set.
###############################################################################

probs       = model.predict(X_test)
preds       = probs.argmax(axis = -1)  
acc         = np.mean(preds == Y_test.argmax(axis=-1))
print("Classification accuracy: %f " % (acc))

print(probs[:100])

all_y_T = {}
all_prediction_T = {}
all_T_all_Num = {}
all_T_T = {}
all_T_T_percent = {}

for i in event_id.values():
    all_y_T[i] = tf.equal(tf.argmax(Y_test, 1), i-1)
    all_prediction_T[i] = tf.equal(tf.argmax(probs, 1), i-1)
    all_T_all_Num[i] = tf.reduce_sum(tf.cast(all_y_T[i], tf.float32))

for i in event_id.values():
    all_T_T[i] = {}
    for j in event_id.values():
        all_T_T[i][j] = tf.reduce_sum(tf.cast(tf.math.logical_and(all_y_T[i], all_prediction_T[j]), tf.float32))

for i in event_id.values():
    all_T_T_percent[i] = {}
    for j in event_id.values():
        all_T_T_percent[i][j] = tf.divide(all_T_T[i][j], all_T_all_Num[i])

for i in all_T_T_percent.keys():
    print(all_T_T_percent[i])

############################# PyRiemann Portion ##############################

# code is taken from PyRiemann's ERP sample script, which is decoding in 
# the tangent space with a logistic regression

# n_components = 2  # pick some components

# # set up sklearn pipeline
# clf = make_pipeline(XdawnCovariances(n_components),
#                     TangentSpace(metric='riemann'),
#                     LogisticRegression())

# preds_rg     = np.zeros(len(Y_test))

# # reshape back to (trials, channels, samples)
# X_train      = X_train.reshape(X_train.shape[0], chans, samples)
# X_test       = X_test.reshape(X_test.shape[0], chans, samples)

# # train a classifier with xDAWN spatial filtering + Riemannian Geometry (RG)
# # labels need to be back in single-column format
# clf.fit(X_train, Y_train.argmax(axis = -1))
# preds_rg     = clf.predict(X_test)

# # Printing the results
# acc2         = np.mean(preds_rg == Y_test.argmax(axis = -1))
# print("Classification accuracy: %f " % (acc2))

# # plot the confusion matrices for both classifiers
# names        = ['audio left', 'audio right', 'vis left', 'vis right']
# plt.figure(0)
# plot_confusion_matrix(preds, Y_test.argmax(axis = -1), names, title = 'EEGNet-8,2')

# plt.figure(1)
# plot_confusion_matrix(preds_rg, Y_test.argmax(axis = -1), names, title = 'xDAWN + RG')



