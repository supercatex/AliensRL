import Agent
import time

class GameAgent(Agent.Agent):
    def get_actions(self, observations):
        return ['L', 'R']
        
    def get_next_observations(self, observations, action):
        next_observations = observations.copy()
        player_move = 0
        if action == 'L':
            player_move = next_observations['speed']
        elif action == 'R':
            player_move = -next_observations['speed']

        bomb_infos = next_observations['bomb_infos']
        for i in range(0, len(bomb_infos)):
            bomb = bomb_infos[i]
            bomb['dx'] += player_move
            bomb['dy'] += bomb['speed']
            distance = bomb['dx'] * bomb['dx'] + bomb['dy'] * bomb['dy']
            if distance < 100:
                next_observations['alive'] = False

        self.add_state(next_observations)
        return next_observations

    def get_reward(self, observations, action):
        if not observations['alive']:
            return -999
        return 0

if __name__ == '__main__':
    agent = GameAgent()
    agent.load_data()
    
    for i in range(0, 1):
        state = {'S': 1}
        while True:
            print(str(state))
            if state['S'] == 7: break;
            agent.add_state(state)
            action = agent.get_action(state)
            state = agent.study(state, action)
            time.sleep(0.05)
        agent.print_Q()
    print('END')
