import numpy as np
import hashlib, random, time, json, os

class Agent:

    #Q-learning
    observations = []   #observations
    states = []         #states
    learning_rate = 0   #alpha
    discount_factor = 1 #gamma
    greedy = 0          #greedy
    Q = {}              #initial conditions

    #data files
    filename = './data/data.json'

    #constructor
    def __init__(self,
                 learning_rate = 0.1,
                 discount_factor = 0.9,
                 greedy = 0.9):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.greedy = greedy

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#Agent rules waiting to overwirte.
    def get_actions(self, observations):
        if observations['S'] == 1:
            return ['right']
        elif observations['S'] == 6:
            return ['left']
        else:
            return ['left', 'right']
        
    def get_next_observations(self, observations, action):
        next_observations = observations.copy()
        if action == 'left':
            next_observations['S'] -= 1
        elif action == 'right':
            next_observations['S'] += 1
        self.add_state(next_observations)
        return next_observations

    def get_reward(self, observations, action):
        if observations['S'] == 5 and action == 'right':
            return 1
        return 0
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    
    #Load data.
    #params: none
    #return: void
    def load_data(self):
        if not os.path.exists(self.filename):
            f = open(self.filename, 'w')
            f.write('')
            f.close()
            
        f = open(self.filename, 'r')
        data = f.readlines()
        f.close()
        if len(data) > 0:
            temp = json.loads(data[0])
            self.observations = temp['0']
            self.Q = temp['1']

    #Save data.
    #params: none
    #return: void
    def save_data(self):
        data = json.dumps({'0': [], '1': self.Q})
        f = open(self.filename, 'w')
        f.write(data)
        f.close()

    #Q-learning study method.
    #params:
    #   observations: dict
    #   action: string
    #return: next observations
    def study(self, observations, action):
        state = self.get_key(observations)

        next_observations = self.get_next_observations(observations, action)
        next_state = self.get_key(next_observations)
        next_action = self.get_optimal_action(next_observations)
        
        #Q[n]
        old_value = self.Q[state][action]
        #R[n]
        reward = self.get_reward(observations, action)
        #Q[n+1]
        future_value = self.Q[next_state][next_action]

        #Q[n] <- Q[n] + a * (R[n] + y * Q[n+1] - Q[n])
        self.Q[state][action] = old_value + self.learning_rate * (reward + self.discount_factor * future_value - old_value) 

        #save data
        #self.save_data()

        return next_observations

    #print Q.
    #params: none
    #return: void
    def print_Q(self):
        for i in range(0, len(self.observations)):
            state = self.get_key(self.observations[i])
            print(str(self.observations[i]) + ': ' + str(self.Q[state]))

    #get a randomize action by observations.
    #params:
    #   observations : dict
    #return: string
    def get_random_action(self, observations):
        state = self.get_key(observations)
        actions = self.Q[state].keys()
        if len(actions) == 0: return ''
        
        rand = random.randint(0, len(actions) - 1)
        return actions[rand]

    #get a optimal action by observations.
    #params:
    #   observations : dict
    #return: string
    def get_optimal_action(self, observations):
        state = self.get_key(observations)
        actions = self.Q[state].keys()
        if len(actions) == 0: return ''

        #random action order
        for i in range(0, len(actions)):
            rand = random.randint(0, len(actions) - 1)
            temp = actions[i]
            actions[i] = actions[rand]
            actions[rand] = temp

        #get the max one
        action = actions[0]
        max_value = self.Q[state][action]
        for i in range(1, len(actions)):
            if self.Q[state][actions[i]] > max_value:
                action = actions[i]
                max_value = self.Q[state][actions[i]]
        return action

    #get a action by observations.
    #params:
    #   observations : dict
    #return: string
    def get_action(self, observations):
        if random.random() < self.greedy:
            return self.get_optimal_action(observations)
        else:
            return self.get_random_action(observations)
    
    #add a new state
    #params:
    #   observations : dict
    #   actions : array
    #return: void
    def add_state(self, observations):
        state = self.get_key(observations)
        if self.Q.has_key(state):
            return
        
        self.states.append(state)
        self.observations.append(observations)
        
        #renew Q
        self.Q[state] = {}
        actions = self.get_actions(observations)
        for i in range(0, len(actions)):
            self.Q[state][actions[i]] = 0

    #named state by observations
    #params:
    #   observations : dict
    #return: string
    def get_key(self, observations):
        temp = ''
        for key, value in observations.iteritems():
            temp += str(key) + ':' + str(value) + ','
        md5 = hashlib.md5(temp.encode('utf-8')).hexdigest()
        return md5

#main function for testing.
if __name__ == '__main__':
    agent = Agent()
    agent.load_data()
    
    for i in range(0, 10):
        state = {'S': 1}
        while True:
            print(str(state))
            if state['S'] == 6: break;
            agent.add_state(state)
            action = agent.get_action(state)
            state = agent.study(state, action)
            time.sleep(0.05)
        agent.print_Q()
    print('END')
