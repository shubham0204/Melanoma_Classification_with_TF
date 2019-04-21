
from tensorflow.python.keras import models , optimizers , losses ,activations , callbacks
from tensorflow.python.keras.layers import *
import tensorflow.python.keras.backend as K
from PIL import Image
import tensorflow as tf
import time
import os
import numpy as np

class Recognizer (object) :

	def __init__( self ):

		tf.logging.set_verbosity( tf.logging.ERROR )

		self.__DIMEN = 48

		input_shape = ((self.__DIMEN ** 2) * 3,)
		convolution_shape = (self.__DIMEN, self.__DIMEN, 3)

		kernel_size_1 = (8, 8)
		kernel_size_2 = (6, 6)
		kernel_size_3 = (4, 4)

		pool_size_1 = (6, 6)
		pool_size_2 = (4, 4)

		strides = 1

		seq_conv_model = [

			tf.keras.layers.Reshape(input_shape=input_shape, target_shape=convolution_shape),

			tf.keras.layers.Conv2D(32, kernel_size=kernel_size_1, strides=strides, activation='relu'),
			tf.keras.layers.MaxPooling2D(pool_size=pool_size_1, strides=strides),

			tf.keras.layers.Conv2D(64, kernel_size=kernel_size_2, strides=strides, activation='relu'),
			tf.keras.layers.MaxPooling2D(pool_size=pool_size_2, strides=strides),

			tf.keras.layers.Conv2D(128, kernel_size=kernel_size_3, strides=strides, activation='relu'),

			tf.keras.layers.Flatten(),

			tf.keras.layers.Dense(3076, activation=tf.keras.activations.sigmoid)

		]

		seq_model = tf.keras.Sequential(seq_conv_model)

		input_x1 = tf.keras.layers.Input(shape=input_shape)
		input_x2 = tf.keras.layers.Input(shape=input_shape)

		output_x1 = seq_model(input_x1)
		output_x2 = seq_model(input_x2)

		distance_euclid = tf.keras.layers.Lambda(lambda tensors: K.abs(tensors[0] - tensors[1]))([output_x1, output_x2])
		outputs = tf.keras.layers.Dense(1, activation=tf.keras.activations.sigmoid)(distance_euclid)
		self.__model = tf.keras.models.Model([input_x1, input_x2], outputs)

		self.__model.compile(loss=tf.keras.losses.binary_crossentropy, optimizer=tf.keras.optimizers.Adam(lr=0.0001),
					  metrics=['accuracy'])


	def fit(self, X, Y ,  hyperparameters  ):
		initial_time = time.time()
		self.__model.fit( X  , Y ,
						 batch_size=hyperparameters[ 'batch_size' ] ,
						 epochs=hyperparameters[ 'epochs' ] ,
						 callbacks=hyperparameters[ 'callbacks'],
						 validation_data=hyperparameters[ 'val_data' ]
						 )
		final_time = time.time()
		eta = ( final_time - initial_time )
		time_unit = 'seconds'
		if eta >= 60 :
			eta = eta / 60
			time_unit = 'minutes'
		self.__model.summary( )
		print( 'Elapsed time acquired for {} epoch(s) -> {} {}'.format( hyperparameters[ 'epochs' ] , eta , time_unit ) )


	def prepare_images_from_dir( self , dir_path ) :
		images = list()
		images_names = os.listdir( dir_path )
		for imageName in images_names :
			image = Image.open(dir_path + imageName).convert('L')
			resize_image = image.resize((self.__DIMEN, self.__DIMEN))
			array = list()
			for x in range(self.__DIMEN):
				sub_array = list()
				for y in range(self.__DIMEN):
					sub_array.append(resize_image.load()[x, y])
				array.append(sub_array)
			image_data = np.array(array)
			image = np.array(np.reshape(image_data,(self.__DIMEN, self.__DIMEN, 3)))
			images.append(image)

		return np.array( images )


	def evaluate(self , test_X , test_Y  ) :
		return self.__model.evaluate(test_X, test_Y)


	def predict(self, X  ):
		predictions = self.__model.predict( X  )
		return predictions


	def summary(self):
		self.__model.summary()

	def save_model(self , file_path ):
		self.__model.save(file_path )


	def load_model(self , file_path ):
		self.__model = models.load_model(file_path)

