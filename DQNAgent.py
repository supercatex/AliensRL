from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Dense , Dropout , Flatten
from keras.layers import  Conv2D , MaxPooling2D

import random
import numpy as np 
from collections import deque


class DQNAgent:


    def __init__ ( self , state_size , action_size ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = 0.95
        self.epsilon = 0.1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.1
        self.memory = deque ( maxlen = 2000 )
        self.model = self.build_model()
        self.training = 0
        self.training_record = None


    def build_model ( self ):
        model = Sequential()
        model.add ( Conv2D ( filters = 16 ,
                             kernel_size = ( 3 , 4 ) ,
                             padding = 'same' ,
                             activation = 'relu',
                             input_shape = self.state_size ) )
        model.add ( Dropout ( 0.1 ) )
        model.add ( MaxPooling2D ( pool_size = ( 2 , 2 ) ) )
        model.add ( Conv2D ( filters = 32 ,
                             kernel_size = ( 3 , 4 ) ,
                             padding = 'same' ,
                             activation = 'relu' ) )
        model.add ( Dropout ( 0.1 ) )
        model.add ( MaxPooling2D ( pool_size = ( 2 , 2 ) ) )
        model.add ( Flatten() )
        model.add ( Dense ( 1000 , activation = 'relu' ) )
        model.add ( Dropout ( 0.1 ) )
        model.add ( Dense ( self.action_size , activation = 'softmax' ) )
        model.compile ( loss = 'mse' , 
                        optimizer = 'adam' ,
                        metrics = ['accuracy'] )
        return model
    

    def remember ( self , state , action , reward , next_state , done ):
        self.memory.append ( ( state , action , reward , next_state , done ) )
    

    def get_action ( self , state ):
        if np.random.rand() <= self.epsilon:
            return random.randrange ( self.action_size )
        act_values = self.model.predict ( state )
        print ( act_values )
        return np.argmax ( act_values[0] )
    

    def replay ( self , batch_size ):
        minibatch = random.sample ( self.memory , batch_size )
        for state , action , reward , next_state , done in minibatch:
            target = reward
            if not done:
                target = ( reward + \
                         self.gamma * np.amax ( self.model.predict ( next_state )[0] ) )
            target_f = self.model.predict ( state )
            target_f[0][action] = target
            self.training_record = self.model.fit ( state , target_f , epochs = 1 , verbose = 0 )
        #if self.epsilon > self.epsilon_min:
        #    self.epsilon *= self.epsilon_decay
    

    def load ( self , name ):
        try:
            self.model.load_weights ( name )
            print ( 'training continue...')
        except:
            print ( 'training reload failed...' )
            pass

    def save ( self , name ):
        try:
            self.model.save_weights ( name )
            print ( 'training weights saved...' )
        except:
            print ( 'training weights save failed...' )
            pass