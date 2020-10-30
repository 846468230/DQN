import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import os
from datetime import datetime
from simulations.config import model_path
np.random.seed(1)


class DeepQNetwork:
    def __init__(
            self,
            n_actions,
            n_features,
            learning_rate=0.01,
            reward_decay=0.9,
            e_greedy=0.9,
            replace_target_iter=300,
            memory_size=500,
            batch_size=32,
            e_greedy_increment=None,
            output_graph=False,
    ):
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max

        # total learning step
        self.learn_step_counter = 0

        # initialize zero memory [s, a, r, s_]
        self.memory = np.zeros((self.memory_size, n_features * 2 + 2))

        # consist of [target_net, evaluate_net]
        self.model = self._build_net()
        self.target_model = self._build_net()
        self.cost_his = []
        #logdir = "logs\\fit\\" + datetime.now().strftime("%Y%m%d-%H%M%S")
        #self.tensorboard_callback = keras.callbacks.TensorBoard(log_dir=logdir)

    def _build_net(self):
        w_initializer, b_initializer = keras.initializers.RandomUniform(-0.3, 0.3), keras.initializers.Constant(0.1)
        model = keras.Sequential()
        model.add(keras.layers.InputLayer(input_shape=(self.n_features,)))
        model.add(keras.layers.Dense(256, activation="relu", kernel_initializer=w_initializer,
                                     bias_initializer=b_initializer))
        model.add(keras.layers.Dense(128, activation="relu", kernel_initializer=w_initializer,
                                     bias_initializer=b_initializer))
        model.add(keras.layers.Dense(self.n_actions, activation="linear", kernel_initializer=w_initializer,
                                     bias_initializer=b_initializer))
        model.compile(loss=keras.losses.MeanSquaredError(),
                      optimizer=keras.optimizers.RMSprop(lr=self.lr))
        model.summary()
        return model

    def store_transition(self, s, a, r, s_):
        if not hasattr(self, "memory_counter"):
            self.memory_counter = 0

        transition = np.hstack((s, [a, r], s_))
        index = self.memory_counter % self.memory_size
        self.memory[index, :] = transition

        self.memory_counter += 1

    def choose_action(self, observation,train):
        observation = observation[np.newaxis, :]
        if train:
            if np.random.uniform() < self.epsilon:
                actions_value = self.model.predict(observation)
                action = np.argmax(actions_value)
            else:
                action = np.random.randint(0, self.n_actions)
        else:
            actions_value = self.model.predict(observation)
            action = np.argmax(actions_value)
        return action

    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.target_model.set_weights(self.model.get_weights())
            print('\ntarget_params_replaced\n')

        # sample batch memory from all memory
        if self.memory_counter > self.memory_size:
            sample_index = np.random.choice(self.memory_size, self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_counter, self.batch_size)

        batch_memory = self.memory[sample_index, :]
        q_next = self.target_model.predict(batch_memory[:, -self.n_features:])
        q_eval = self.model.predict(batch_memory[:, :self.n_features])
        q_target = q_eval.copy()
        batch_index = np.arange(self.batch_size, dtype=np.int32)
        eval_act_index = batch_memory[:, self.n_features].astype(int)
        reward = batch_memory[:, self.n_features + 1]
        q_target[batch_index, eval_act_index] = reward + self.gamma * np.max(q_next, axis=1)
        # train eval network
        # history = self.model.fit(batch_memory[:,:self.n_features],q_target,verbose=0,callbacks=[self.tensorboard_callback])
        history = self.model.fit(batch_memory[:, :self.n_features], q_target, verbose=0)
        self.cost_his.extend(history.history["loss"])

        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step_counter += 1

    def save_model(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        self.model.save_weights(os.path.join(path,"weights"))

    def load_model(self, path):
        self.model.load_weights(os.path.join(path,"weights"))

    def plot_cost(self):
        import matplotlib.pyplot as plt
        plt.plot(np.arange(len(self.cost_his)), self.cost_his)
        plt.ylabel('Cost')
        plt.xlabel('training steps')
        plt.show()


def play_it():
    env = gym.make('CartPole-v0')
    env = env.unwrapped

    print(env.action_space)
    print(env.observation_space)
    print(env.observation_space.high)
    print(env.observation_space.low)

    RL = DeepQNetwork(n_actions=env.action_space.n,
                      n_features=env.observation_space.shape[0],
                      learning_rate=0.01, e_greedy=0.9,
                      replace_target_iter=100, memory_size=2000,
                      e_greedy_increment=0.001, )

    totel_steps = 0

    for i_episode in range(10):
        observation = env.reset()
        ep_r = 0
        while True:
            env.render()
            action = RL.choose_action(observation)
            observation_, reward, done, info = env.step(action)

            # the smaller theta and closer to center the better
            x, x_dot, theta, theta_dot = observation_
            r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
            r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
            reward = r1 + r2

            RL.store_transition(observation, action, reward, observation_)
            ep_r += reward
            if totel_steps > 1000:
                RL.learn()

            if done:
                print('episode: ', i_episode, 'ep_r: ', round(ep_r, 2), ' epsilon: ', round(RL.epsilon, 2))
                break
            observation = observation_
            totel_steps += 1

    RL.plot_cost()
    RL.save_model(model_path)
    RL.load_model(model_path)
    observation = env.reset()
    while True:
        env.render()
        action = RL.choose_action(observation)
        observation_, reward, done, info = env.step(action)

        # the smaller theta and closer to center the better
        x, x_dot, theta, theta_dot = observation_
        r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
        r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
        reward = r1 + r2

        ep_r += reward
        if done:
            print('episode: ', i_episode, 'ep_r: ', round(ep_r, 2), ' epsilon: ', round(RL.epsilon, 2))
            break
        observation = observation_
import gym


def play_MountainCar():
    env = gym.make('MountainCar-v0')
    env = env.unwrapped

    print(env.action_space)
    print(env.observation_space)
    print(env.observation_space.high)
    print(env.observation_space.low)

    RL = DeepQNetwork(n_actions=3, n_features=2, learning_rate=0.001, e_greedy=0.9,
                      replace_target_iter=300, memory_size=3000,
                      e_greedy_increment=0.0002, )

    total_steps = 0
    for i_episode in range(10):

        observation = env.reset()
        ep_r = 0
        while True:
            env.render()

            action = RL.choose_action(observation)

            observation_, reward, done, info = env.step(action)

            position, velocity = observation_

            # the higher the better
            reward = abs(position - (-0.5))  # r in [0, 1]

            RL.store_transition(observation, action, reward, observation_)

            if total_steps > 1000:
                RL.learn()

            ep_r += reward
            if done:
                get = '| Get' if observation_[0] >= env.unwrapped.goal_position else '| ----'
                print('Epi: ', i_episode,
                      get,
                      '| Ep_r: ', round(ep_r, 4),
                      '| Epsilon: ', round(RL.epsilon, 2))
                break

            observation = observation_
            total_steps += 1

    RL.plot_cost()


def play_single():
    env = gym.make('Single_virtual-v0')
    env = env.unwrapped

    print(env.action_space)
    print(env.observation_space)
    print(env.observation_space.high)
    print(env.observation_space.low)

    RL = DeepQNetwork(n_actions=env.action_space.n,
                      n_features=env.observation_space.shape[0],
                      learning_rate=0.01, e_greedy=0.9,
                      replace_target_iter=100, memory_size=2000,
                      e_greedy_increment=0.001, )

    totel_steps = 0

    for i_episode in range(1000):
        observation = env.reset()
        ep_r = 0
        while True:
            # env.render()
            action = RL.choose_action(observation)
            observation_, reward, done, info = env.step(action)

            # the smaller theta and closer to center the better
            # x, x_dot, theta, theta_dot = observation_
            # r1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
            # r2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
            # reward = r1 + r2

            RL.store_transition(observation, action, reward, observation_)
            ep_r += reward
            if totel_steps > 1000:
                RL.learn()

            if done:
                print('episode: ', i_episode, 'ep_r: ', round(ep_r, 2), ' epsilon: ', round(RL.epsilon, 2))
                break
            observation = observation_
            totel_steps += 1

    RL.plot_cost()


if __name__ == '__main__':
    play_it()
    # play_MountainCar()
    # play_single()
