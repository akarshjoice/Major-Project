
import numpy as np
import h5py
import scipy.io as sio
from tensorflow import keras
from skimage.io import imread
import numpy as np
from tensorflow import keras
import tensorflow as tf
from matplotlib import pyplot as plt
from IPython.display import clear_output


path ='/home/b160148cs/Music'




class DataGenerator(keras.utils.Sequence):
    def __init__(self, list_IDs, data_dir, batch_size = 32, x_dim=(512,512,1), y_dim=(512,512,1), shuffle=True):
        self.list_IDs = list_IDs
        self.data_dir = data_dir
        self.batch_size = batch_size
        self.x_dim = x_dim
        self.y_dim = y_dim
        self.shuffle = shuffle
        self.on_epoch_end()
    
    def __len__(self):
        return int(np.floor(len(self.list_IDs)/self.batch_size))
    
    def on_epoch_end(self):
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle == True:
            np.random.shuffle(self.indexes)
    
    def __getitem__(self, index):
        batch_indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        batch_IDs = [self.list_IDs[k] for k in batch_indexes]
        
        X, Y = self.__batch_data_generation(batch_IDs)
        
        return X,Y
    
    def __batch_data_generation(self, batch_IDs):
        X = np.empty((self.batch_size, *self.x_dim)) #* is used to unpack the self.dim tuple
        Y = np.empty((self.batch_size, *self.y_dim))
        
        for i, ID in enumerate(batch_IDs):
            X[i,:], Y[i,:] = self.load_mat(ID, 'new_sino', 'sino')
            
        return X,Y
    
    def load_mat(self, ID, x_name, y_name):
        file_name = self.data_dir+'Metal Deleted Sinogram/' + str(ID) + '.mat'
        try:
            with h5py.File(file_name, 'r') as f:
                x = np.reshape(f[x_name], self.x_dim)
        except OSError:
            f = sio.loadmat(file_name)
            x = np.reshape(f[x_name], self.x_dim)
        file_name = self.data_dir+'True Sinogram/' + str(ID) + '.mat'
        try:
            with h5py.File(file_name, 'r') as f:
                y = np.reshape(f[y_name], self.y_dim)
        except OSError:
            f = sio.loadmat(file_name)
            y = np.reshape(f[y_name], self.y_dim)
                    
        #sart=imread(self.data_dir+'/SART/Sparse100/'+str(ID)+'.png',0)
        #x = np.reshape(sart, self.y_dim)
        return x,y





def downsample(filters, size, apply_batchnorm=True):
    initializer = tf.random_normal_initializer(0., 0.02)
    result = keras.Sequential()
    result.add(keras.layers.Conv2D(filters, size, strides=2, padding='same',
                              kernel_initializer=initializer, use_bias=False))
    if apply_batchnorm:
      result.add(keras.layers.BatchNormalization())
    result.add(keras.layers.LeakyReLU())

    return result

def upsample(filters, size, apply_dropout=False):
    initializer = tf.random_normal_initializer(0., 0.02)
    result = keras.Sequential()
    result.add(keras.layers.Conv2DTranspose(filters, size, strides=2, padding='same',
                                      kernel_initializer=initializer, use_bias=False))
    result.add(keras.layers.BatchNormalization())
    if apply_dropout:
        result.add(keras.layers.Dropout(0.5))
    result.add(keras.layers.ReLU())

    return result


def UNet():
    inputs = keras.layers.Input(shape=(512,512,1))
    
    #level 1
    conv64_1 = keras.layers.Conv2D(64, [3,3], [1,1], 'same', activation = 'relu')(inputs)
    conv64_1_BN = keras.layers.BatchNormalization()(conv64_1)
    conv64_2 = keras.layers.Conv2D(64, [3,3], [1,1], 'same', activation = 'relu')(conv64_1_BN)
    conv64_2_BN = keras.layers.BatchNormalization()(conv64_2)
    conv64_3 = keras.layers.Conv2D(64, [3,3], [1,1], 'same', activation = 'relu')(conv64_2_BN)
    conv64_3_BN = keras.layers.BatchNormalization()(conv64_3)
    
    #downsampling to level 2
    conv64_3_pool = keras.layers.MaxPool2D([2,2], padding = 'valid')(conv64_3_BN)
    conv128_1 = keras.layers.Conv2D(128, [3,3], [1,1], 'same', activation = 'relu')(conv64_3_pool)
    conv128_1_BN = keras.layers.BatchNormalization()(conv128_1)
    conv128_2 = keras.layers.Conv2D(128, [3,3], [1,1], 'same', activation = 'relu')(conv128_1_BN)
    conv128_2_BN = keras.layers.BatchNormalization()(conv128_2)
    
    #downsampling to level 3
    conv128_2_pool = keras.layers.MaxPool2D([2,2], padding = 'valid')(conv128_2_BN)
    conv256_1 = keras.layers.Conv2D(256, [3,3], [1,1], 'same', activation = 'relu')(conv128_2_pool)
    conv256_1_BN = keras.layers.BatchNormalization()(conv256_1)
    conv256_2 = keras.layers.Conv2D(256, [3,3], [1,1], 'same', activation = 'relu')(conv256_1_BN)
    conv256_2_BN = keras.layers.BatchNormalization()(conv256_2)
    
    #downsampling to level 4
    conv256_2_pool = keras.layers.MaxPool2D([2,2], padding = 'valid')(conv256_2_BN)
    conv512_1 = keras.layers.Conv2D(512, [3,3], [1,1], 'same', activation = 'relu')(conv256_2_pool)
    conv512_1_BN = keras.layers.BatchNormalization()(conv512_1)
    conv512_2 = keras.layers.Conv2D(512, [3,3], [1,1], 'same', activation = 'relu')(conv512_1_BN)
    conv512_2_BN = keras.layers.BatchNormalization()(conv512_2)
    
    #downsampling to level 5
    conv512_2_pool = keras.layers.MaxPool2D([2,2], padding = 'valid')(conv512_2_BN)
    conv1024_1 = keras.layers.Conv2D(1024, [3,3], [1,1], 'same', activation = 'relu')(conv512_2_pool)
    conv1024_1_BN = keras.layers.BatchNormalization()(conv1024_1)
    conv1024_2 = keras.layers.Conv2D(1024, [3,3], [1,1], 'same', activation = 'relu')(conv1024_1_BN)
    conv1024_2_BN = keras.layers.BatchNormalization()(conv1024_2)
    
    #upsampling to level 4
    level4_ini = keras.layers.Conv2D(512, [3,3], [1,1], 'same', activation='relu')(keras.layers.UpSampling2D((2,2))(conv1024_2_BN))
    level4_ini_concat = keras.layers.concatenate([conv512_2_BN, level4_ini], axis = -1)
    conv512_1_up = keras.layers.Conv2D(512, [3,3], [1,1], 'same', activation = 'relu')(level4_ini_concat)
    conv512_1_BN_up = keras.layers.BatchNormalization()(conv512_1_up)
    conv512_2_up = keras.layers.Conv2D(512, [3,3], [1,1], 'same', activation = 'relu')(conv512_1_BN_up)
    conv512_2_BN_up = keras.layers.BatchNormalization()(conv512_2_up)
    
    #upsampling to level 3
    level3_ini = keras.layers.Conv2D(256, [3,3], [1,1], 'same', activation='relu')(keras.layers.UpSampling2D((2,2))(conv512_2_BN_up))
    level3_ini_concat = keras.layers.concatenate([conv256_2_BN, level3_ini], axis = -1)
    conv256_1_up = keras.layers.Conv2D(256, [3,3], [1,1], 'same', activation = 'relu')(level3_ini_concat)
    conv256_1_BN_up = keras.layers.BatchNormalization()(conv256_1_up)
    conv256_2_up = keras.layers.Conv2D(256, [3,3], [1,1], 'same', activation = 'relu')(conv256_1_BN_up)
    conv256_2_BN_up = keras.layers.BatchNormalization()(conv256_2_up)
    
    #upsampling to level 2
    level2_ini = keras.layers.Conv2D(128, [3,3], [1,1], 'same', activation='relu')(keras.layers.UpSampling2D((2,2))(conv256_2_BN_up))
    level2_ini_concat = keras.layers.concatenate([conv128_2_BN, level2_ini], axis = -1)
    conv128_1_up = keras.layers.Conv2D(128, [3,3], [1,1], 'same', activation = 'relu')(level2_ini_concat)
    conv128_1_BN_up = keras.layers.BatchNormalization()(conv128_1_up)
    conv128_2_up = keras.layers.Conv2D(128, [3,3], [1,1], 'same', activation = 'relu')(conv128_1_BN_up)
    conv128_2_BN_up = keras.layers.BatchNormalization()(conv128_2_up)
    
    #upsampling to level 1
    level1_ini = keras.layers.Conv2D(64, [3,3], [1,1], 'same', activation='relu')(keras.layers.UpSampling2D((2,2))(conv128_2_BN_up))
    level1_ini_concat = keras.layers.concatenate([conv64_3_BN, level1_ini], axis = -1)
    conv64_1_up = keras.layers.Conv2D(64, [3,3], [1,1], 'same', activation = 'relu')(level1_ini_concat)
    conv64_1_BN_up = keras.layers.BatchNormalization()(conv64_1_up)
    conv64_2_up = keras.layers.Conv2D(64, [3,3], [1,1], 'same', activation = 'relu')(conv64_1_BN_up)
    conv64_2_BN_up = keras.layers.BatchNormalization()(conv64_2_up)
    conv1_up = keras.layers.Conv2D(1, [1,1], [1,1], 'same')(conv64_2_BN_up)
    outputs = keras.layers.add([inputs, conv1_up])
    
    
    ###################################################################################
    model = keras.models.Model(inputs = inputs, outputs = outputs)
    #if pretrained_weights:
     #  generator.load_weights(pretrained_weights)
    
    return model
    

#if __name__ == '__main__':
#    model = UNet((512,512,1))
#    #model.summary()
#    model.compile(optimizer = 'rmsprop', loss = 'binary_crossentropy')#, metrics = ['accuracy'])
#    x = np.random.random((1,512,512,1))
#    final_out = model.predict(x)
#    print(np.shape(final_out))

generator = UNet()


LAMBDA = 10
def generator_loss(disc_generated_output, gen_output, target):
    gan_loss = loss_object(tf.ones_like(disc_generated_output), disc_generated_output)
    # mean absolute error
    l1_loss = tf.reduce_mean(tf.abs(target - gen_output))
    total_gen_loss = gan_loss + (LAMBDA * l1_loss)

    return total_gen_loss, gan_loss, l1_loss

def Discriminator():
    inp = keras.layers.Input(shape=(512,512,1), name='input_image')
    tar = keras.layers.Input(shape=(512,512,1), name='target_image')

    inputs = keras.layers.Concatenate()([inp, tar])

    #downsampling to level 1
    dlvl1 = downsample(64,4,apply_batchnorm=False)(inputs)
    
    #downsampling to level 2
    dlvl2 = downsample(128,4)(dlvl1)
    
    #downsampling to level 3
    dlvl3 = downsample(256,4)(dlvl2)
    
    #downsampling to level 4
    dlvl4 = downsample(512,4)(dlvl3) 
    
    #downsampling to level 5
    dlvl5 = downsample(512,4)(dlvl4) 

    #downsampling to level 6
    dlvl6 = downsample(512,4)(dlvl5)
    
    #downsampling to level 7
    dlvl7 = downsample(512,4)(dlvl6)
    
    flat1 = keras.layers.Flatten()(dlvl7)
    dense1 = keras.layers.Dense(1, activation='softmax')(flat1)
    # falt1 = keras.layers.Flatten()(conv1024_2_BN)

    model = keras.models.Model(inputs = [inp, tar], outputs = dense1)
    return model



discriminator = Discriminator()


loss_object = keras.losses.BinaryCrossentropy(from_logits=True)

def discriminator_loss(disc_real_output, disc_generated_output):
    real_loss = loss_object(tf.ones_like(disc_real_output), disc_real_output)
    generated_loss = loss_object(tf.zeros_like(disc_generated_output), disc_generated_output)
    total_disc_loss = real_loss + generated_loss

    return total_disc_loss

generator_optimizer = keras.optimizers.Adam(learning_rate=0.0002, beta_1=0.9,beta_2=0.999)
discriminator_optimizer = keras.optimizers.Adam(0.0002, beta_1=0.9)

"""Plotting Metrics and Loss"""


class PlotLearning(keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.i = 0
        self.x = []
        self.losses = []
        self.val_losses = []
        #self.acc = []
        #self.val_acc = []
        self.ssim=[]
        self.psnr=[]
        self.fig = plt.figure()
        
        self.logs = []

    def on_epoch_end(self, epoch, logs={}):
        
        self.logs.append(logs)
        self.x.append(self.i)
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        self.ssim.append(logs.get('ssim_loss'))
        self.psnr.append(logs.get('psnr'))
        #self.acc.append(logs.get('acc'))
        #self.val_acc.append(logs.get('val_acc'))
        self.i += 1
        f, (ax1,ax2,ax3) = plt.subplots(1, 3,figsize=(16,8), sharex=True)
        
        clear_output(wait=True)
        
        ax1.set_yscale('log')
        ax1.plot(self.x, self.losses, label="loss")
        ax1.plot(self.x, self.val_losses, label="val_loss")
        ax1.set_ylabel('MSE')
        ax1.set_xlabel('Epoch')
        ax1.legend()
        
        ax2.plot(self.x, self.ssim, label="ssim")
        ax2.set_ylabel('SSIM')
        ax2.set_xlabel('Epoch')
        ax2.legend()
        
        ax3.plot(self.x, self.psnr, label="psnr")
        ax3.set_ylabel('PSNR')
        ax3.set_xlabel('Epoch')
        ax3.legend()
    
        plt.savefig(path+'training.png')
        plt.show()

        
plot = PlotLearning()

"""Metrics For Evaluation"""

import tensorflow as tf
from keras import backend

 
# Structural Similarity Index
def ssim_loss(y_true, y_pred):
  return tf.reduce_mean(tf.image.ssim(y_true, y_pred, 255))

# Peak Signal To Noise Ratio
def psnr(y_true, y_pred):
  return tf.reduce_mean(tf.image.psnr(y_true, y_pred, 255))

def msr(y_true, y_pred):
  return tf.reduce_mean(tf.keras.losses.mean_squared_error(y_true,y_pred))

"""Training with matlab generated shapes"""

train_IDs = list(np.arange(0,680))
val_IDs = list(np.arange(680, 910))
train_generator = DataGenerator(train_IDs, path, batch_size = 2)
val_generator = DataGenerator(val_IDs, path, batch_size = 2)

#tbCallBack = keras.callbacks.TensorBoard(log_dir = path+'TestTraining/logs', write_graph = True, write_images = True) #Tensorboard callback
#checkpoint_path = path+'TestTraining/checkpoints/test_cp.ckpt'
#cpCallBack = keras.callbacks.ModelCheckpoint(checkpoint_path) #checkpoints callBack

#model = UNet((512,512,1))
#model.summary()
#model.compile(optimizer = 'rmsprop', loss = 'mean_squared_error', metrics = [ssim_loss,psnr])
#history= model.fit_generator(train_generator, epochs = 100, validation_data = val_generator,
                    #workers = 6, callbacks = [plot])#,tbCallBack, cpCallBack])

#print(train_generator[0][0].astype('float32'))
#print(train_generator[0][1].astype('float32'))
#print(np.shape(train_generator)[0])

def generate_images(model, test_input, tar):
    prediction = model(test_input, training=True)
    plt.figure(figsize=(15,15))

    display_list = [test_input[0], tar[0], prediction[0]]
    title = ['Input Image', 'Ground Truth', 'Predicted Image']

    for i in range(3):
        plt.subplot(1, 3, i+1)
        plt.title(title[i])
        # getting the pixel values between [0, 1] to plot it.
        plt.imshow(display_list[i])
        plt.axis('off')
    plt.show()

@tf.function
def train_step(input_image, target, epoch):
    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        gen_output = generator(input_image, training=True)
        disc_real_output = discriminator([input_image, target], training=True)
        disc_generated_output = discriminator([input_image, gen_output], training=True)
        gen_total_loss, gen_gan_loss, gen_l1_loss = generator_loss(disc_generated_output, gen_output, target)
        disc_loss = discriminator_loss(disc_real_output, disc_generated_output)

    generator_gradients = gen_tape.gradient(gen_total_loss,
                                            generator.trainable_variables)
    discriminator_gradients = disc_tape.gradient(disc_loss,
                                                discriminator.trainable_variables)

    generator_optimizer.apply_gradients(zip(generator_gradients,
                                            generator.trainable_variables))
    discriminator_optimizer.apply_gradients(zip(discriminator_gradients,
                                                discriminator.trainable_variables))

    #with summary_writer.as_default():
    #    tf.summary.scalar('gen_total_loss', gen_total_loss, step=epoch)
    #    tf.summary.scalar('gen_gan_loss', gen_gan_loss, step=epoch)
    #    tf.summary.scalar('gen_l1_loss', gen_l1_loss, step=epoch)
    #    tf.summary.scalar('disc_loss', disc_loss, step=epoch)

import os
import time
from IPython import display
checkpoint_dir = path + 'training_checkpoints/'
checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                 discriminator_optimizer=discriminator_optimizer,
                                 generator=generator,
                                 discriminator=discriminator)

def fit(train_ds, epochs, test_ds):
    for epoch in range(epochs):
        start = time.time()

        display.clear_output(wait=True)

        #for n in range(np.shape(test_ds)[0]):
         #   generate_images(generator, test_ds[n][0].astype('float32'), test_ds[n][1].astype('float32'))
        print("Epoch: ", epoch)

        # Train
        for n in range(np.shape(train_ds)[0]):
          print('.', end='')
          if (n+1) % 100 == 0:
            print()
          train_step(train_ds[n][0].astype('float32'), train_ds[n][1].astype('float32'), epoch)
        print()

        # saving (checkpoint) the model every 20 epochs
        if (epoch + 1) % 20 == 0:
            checkpoint.save(file_prefix = checkpoint_prefix)

        print ('Time taken for epoch {} is {} sec\n'.format(epoch + 1,
                                                          time.time()-start))
    checkpoint.save(file_prefix = checkpoint_prefix)

EPOCHS = 100
fit(train_generator, EPOCHS, val_generator)

"""Save Model"""

generator.save(path+"modelgpu.h5")
#checkpoint.restore(tf.train.latest_checkpoint(checkpoint_dir))

"""Load Model from Disk"""

