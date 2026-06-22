import json
import os
import random

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2, username='default_user'):
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.username = username
        _base = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(_base, f'q_table_{self.username}.json')
        self.q_table = self.load_q_table()

    def change_user(self, new_username):
        self.username = new_username
        _base = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(_base, f'q_table_{self.username}.json')
        self.q_table = self.load_q_table()

    def load_q_table(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}

    def save_q_table(self):
        with open(self.filename, 'w') as f:
            json.dump(self.q_table, f)

    def get_q_value(self, state, action):
        state_key = str(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {act: 0.0 for act in self.actions}
            self.save_q_table()
        if action not in self.q_table[state_key]:
            self.q_table[state_key][action] = 0.0
        return self.q_table[state_key][action]

    def choose_action(self, state):
        state_key = str(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {act: 0.0 for act in self.actions}
            self.save_q_table()
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        else:
            state_actions = self.q_table[state_key]
            max_q = max(state_actions.values())
            best_actions = [act for act, q in state_actions.items() if q == max_q]
            return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        old_q = self.get_q_value(state, action)
        next_state_key = str(next_state)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {act: 0.0 for act in self.actions}
        next_max = max(self.q_table[next_state_key].values())
        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        self.q_table[str(state)][action] = new_q
        self.save_q_table()
