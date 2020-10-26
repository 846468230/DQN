# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tensorflow as tf
import numpy as np
import os
from gym import make
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
from datetime import datetime
from dqn import DQNAgent
from rl.policy import BoltzmannQPolicy
from rl.memory import SequentialMemory
tf.compat.v1.disable_eager_execution()

def build_model(nb_actions,observation_space):
    # Next, we build a very simple model.
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + observation_space.shape))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(16))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    model.summary()
    return model

def build_model1(nb_actions,observation_space):
    # Next, we build a very simple model.
    import keras
    w_initializer, b_initializer = keras.initializers.RandomUniform(-0.3, 0.3), keras.initializers.Constant(0.1)
    model = Sequential()
    model.add(Flatten(input_shape=(1,) + observation_space.shape))
    model.add(keras.layers.Dense(100, activation="relu", kernel_initializer=w_initializer, bias_initializer=b_initializer))
    model.add(Dense(nb_actions))
    model.add(Activation('linear'))
    model.summary()
    return model


def play_it():
    #ENV_NAME = 'CartPole-v0'
    #ENV_NAME = 'MountainCar-v0'
    ENV_NAME = 'Single_virtual-v0'
    # Get the environment and extract the number of actions.
    env = make(ENV_NAME)
    env1 = make(ENV_NAME)
    np.random.seed(123)
    env.seed(123)
    nb_actions = env.action_space.n
    model = build_model(nb_actions,env.observation_space)
    # model = build_model1(nb_actions, env.observation_space)

    # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and
    # even the metrics!
    memory = SequentialMemory(limit=50000, window_length=1)
    policy = BoltzmannQPolicy()
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=10,
                   target_model_update=1e-2, policy=policy,)
    dqn.compile(Adam(lr=1e-3), metrics=['mae'])

    # Okay, now it's time to learn something! We visualize the training here for show, but this
    # slows down training quite a lot. You can always safely abort the training prematurely using
    # Ctrl + C.
    dqn.fit(env, nb_steps=50000, visualize=False, verbose=2)

    # After training is done, we save the final weights.
    dqn.save_weights(os.path.join('models_weights_logs','dqn_{}_weights.h5f'.format(ENV_NAME+ datetime.now().strftime("%Y%m%d-%H%M%S"))), overwrite=True)
    # dqn.load_weights(os.path.join('models_weights_logs','dqn_{}_weights.h5f'.format(ENV_NAME)))
    # Finally, evaluate our algorithm for 5 episodes.
    dqn.test(env1, nb_episodes=5, visualize=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    play_it()
    # custom_gym = make('Single_virtual-v0')
    # custom_gym.step('some action')
    # custom_gym.reset()
    # custom_gym.render()
    # custom_gym.close()