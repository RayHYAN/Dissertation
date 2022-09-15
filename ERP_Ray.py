import numpy as np
import pandas as pd

# EEGNet-specific imports
from eegmodels.EEGModels import EEGNet
from tensorflow.keras import utils as np_utils
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import backend as K

K.set_image_data_format('channels_last')
event_id = dict(familiar_music=1, wildlife_video=2, family_inter=3, Tchaikovsky=4, exper_video=5)
kernels, chans, samples, epochs = 1, 4, 1024, 200

# data loading
DIR = 'D:/Work/UCL/Modules/Dissertation/data/EEG-Motor-Movement-Imagery-Dataset/Ray/5classes_mix/'
train_data = pd.read_csv(DIR + 'training_set.csv', header=None)
train_data = np.array(train_data).astype('float32')
train_labels = pd.read_csv(DIR + 'training_label.csv', header=None)
train_labels = np.array(train_labels).astype('int32')
test_data = pd.read_csv(DIR + 'test_set.csv', header=None)
test_data = np.array(test_data).astype('float32')
test_labels = pd.read_csv(DIR + 'test_label.csv', header=None)
test_labels = np.array(test_labels).astype('int32')

print((train_data.shape))
print((train_labels.shape))
print((test_data.shape))
print((test_labels.shape))

X_train = train_data.reshape(train_data.shape[0], chans, samples, 1)
X_validate = test_data.reshape(test_data.shape[0], chans, samples, 1)
Y_train      = np_utils.to_categorical(train_labels)
Y_validate   = np_utils.to_categorical(test_labels)

print('X_train shape:', X_train.shape)
print('Y_train shape:', Y_train.shape)
print('X_validate shape:', X_validate.shape)
print(X_train.shape[0], 'train samples')
print(X_validate.shape[0], 'val samples')

# model setting
def run(batch_size, kernel_length, dropout_rate):
    model = EEGNet(nb_classes = len(event_id.keys()), Chans = chans, Samples = samples, 
                dropoutRate = dropout_rate, kernLength = kernel_length, F1 = 8, D = 2, F2 = 16, 
                dropoutType = 'Dropout')

    model.compile(loss='categorical_crossentropy', optimizer='adam', 
                metrics = ['accuracy'])

    tmp_file_path = r'./Dissertation/eegmodels/examples/tmp/checkpoint.h5'
    checkpointer = ModelCheckpoint(filepath=tmp_file_path, verbose=1,
                                save_best_only=True)
    class_weights = {i:1 for i in range(len(event_id.keys()))}

    fittedModel = model.fit(X_train, Y_train, batch_size = batch_size, epochs = epochs, 
                            verbose = 2, validation_data=(X_validate, Y_validate),
                            callbacks=[checkpointer], class_weight = class_weights)

    # save training result
    model.load_weights(tmp_file_path)
    res = pd.DataFrame({
        'acc': model.history.history['accuracy'],
        'val_acc': model.history.history['val_accuracy'],
        'loss': model.history.history['loss'],
        'val_loss': model.history.history['val_loss'],
    })
    res.to_csv('./Dissertation/eegmodels/examples/res/res_{}_{}_{}.csv'.format(dropout_rate, batch_size, kernel_length) \
        , index = None, encoding = 'utf8')

    probs       = model.predict(X_validate)
    preds       = probs.argmax(axis = -1)  
    acc         = np.mean(preds == Y_validate.argmax(axis=-1))
    print("Classification accuracy: %f " % (acc))
    print()
    return acc


for batch_size in [16, 32]:
    for dropout_rate in [0.5, 0.8]:
        for kernel_length in [32, 64, 125]:
            run(batch_size, kernel_length, dropout_rate)
