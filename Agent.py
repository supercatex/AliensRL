import numpy as np
import hashlib, random, time, json, os


class QLearningAgent:

    #Q-learning
    learning_rate = 0   #alpha
    discount_factor = 1 #gamma
    greedy = 0          #greedy
    Q = {}              #initial conditions

    #data files
    filename = './data/data.json'
    training = 0


    #constructor
    def __init__(self,
                 learning_rate = 0.1,
                 discount_factor = 0.9,
                 greedy = 0.9):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.greedy = greedy


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
            self.training = int(temp['0'])
            self.Q = temp['1']


    #Save data.
    #params: none
    #return: void
    def save_data(self):
        data = json.dumps({'0': self.training, '1': self.Q})
        f = open(self.filename, 'w')
        f.write(data)
        f.close()


    #Q-learning study method.
    #params:
    #   observations: dict
    #   action: string
    #   next_observations: dict
    #   reward: number
    #return: next observations
    def study(self, observations, action, next_observations, reward):
        state = self.get_key(observations)

        next_state = self.get_key(next_observations)
        next_action = self.get_optimal_action(next_observations)
        
        #Q[n]
        old_value = self.Q[state][action]
        #Q[n+1]
        future_value = self.Q[next_state][next_action]

        #Q[n] <- Q[n] + a * (R[n] + y * Q[n+1] - Q[n])
        self.Q[state][action] = old_value + self.learning_rate * (reward + self.discount_factor * future_value - old_value) 

        #self.training = self.training + 1
        return next_observations


    #print Q.
    #params: none
    #return: void
    def print_Q(self):
        for state, actions in self.Q.items():
            print(str(state) + ': ' + str(actions))

    def get_Q_zero_count(self):
        count = 0
        for state, actions in self.Q.items():
            for action, value in actions.items():
                if value == 0:
                    count += 1
        return count

    def get_Q_max_value(self):
        v = 0
        for state, actions in self.Q.items():
            for action, value in actions.items():
                if value > v:
                    v = value
        return v

    def get_Q_min_value(self):
        v = 0
        for state, actions in self.Q.items():
            for action, value in actions.items():
                if value < v:
                    v = value
        return v
                

    #get a randomize action by observations.
    #params:
    #   observations : dict
    #return: string
    def get_random_action(self, observations):
        state = self.get_key(observations)
        actions = list(self.Q[state].keys())
        if len(actions) == 0: return ''
        
        rand = random.randint(0, len(actions) - 1)
        return actions[rand]


    #get a optimal action by observations.
    #params:
    #   observations : dict
    #return: string
    def get_optimal_action(self, observations):
        state = self.get_key(observations)
        actions = list(self.Q[state].keys())
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
    def add_state(self, observations, actions, f):
        state = self.get_key(observations)
        ff = self.get_key(f)
        if state in self.Q:
            return

#         print ( state )
#         print ( observations )
        
#         existed_keys = {}
#         existed_errs = 0
#         for key1, val1 in self.Q.items():
#             obj1 = json.loads(key1)
#             temp = {}
#             errs = 0
#             for key2, val2 in observations.items():
#                 if key2 in obj1:
#                     temp.update({key2: obj1[key2]})
#                     errs += np.mean((np.array(obj1[key2]) - np.array(val2)) ** 2)
#             if len(temp) > len(existed_keys):
#                 existed_keys = temp
#                 existed_errs = errs
#             elif len(temp) == len(existed_keys):
#                 if existed_errs > errs:
#                     existed_keys = temp
#                     existed_errs = errs
#         
#         if len(existed_keys) > 0:
#             temp = self.get_key(existed_keys)
#             if temp in self.Q:
#                 self.Q[state] = {}
#                 for i in range(0, len(actions)):
#                     self.Q[state][actions[i]] = self.Q[temp][actions[i]]
#                 return
        
        #renew Q
        self.Q[state] = {}
        #actions = self.get_actions(observations)
        for i in range(0, len(actions)):
            if ff not in self.Q:
                self.Q[state][actions[i]] = 0
            else:
                self.Q[state][actions[i]] = self.Q[ff][actions[i]]


    #named state by observations
    #params:
    #   observations : dict
    #return: string
    def get_key(self, observations):
        temp = '{'
        keys = sorted(list(observations.keys()))
        for i in range(0, len(keys) - 1):
            temp += '"' + str(keys[i]) + '": ' + str(observations[keys[i]]) + ', '
        if len(keys) > 0:
            temp += '"' + str(keys[len(keys) - 1]) + '": ' + str(observations[keys[len(keys) - 1]]) + ''
        temp += '}'
        return temp


#main function for testing.
if __name__ == '__main__':
    
    agent = QLearningAgent()
    for i in range(0, 10):
        print('Round:', i + 1)
        position = 1
        prev_state = {}
        curr_state = {}
        prev_action = ''
        curr_action = ''
        reward = 0
        
        while True:
            #Renew state
            prev_state = curr_state
            curr_state = {'S1': position}
            if position == 1:
                agent.add_state(curr_state, ['R'])
            elif position == 6:
                agent.add_state(curr_state, ['L'])
            else:
                agent.add_state(curr_state, ['L', 'R'])

            #Renew action
            prev_action = curr_action
            curr_action = agent.get_action(curr_state)
            if curr_action == 'L':
                position = position - 1
            elif curr_action == 'R':
                position = position + 1
                
            #Study
            if prev_action != '':
                reward = 0
                if curr_state['S1'] == 6:
                    reward = 1
                agent.study(prev_state, prev_action, curr_state, reward)
                
            print(curr_state)
            time.sleep(0.1)
            
            if reward:
                break
        
    print('END')
