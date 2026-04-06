import json
import os
import random
import numpy as np

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2, username='default_user'):
        self.actions = actions
        self.alpha = alpha       # Learning rate
        self.gamma = gamma       # Discount factor
        self.epsilon = epsilon   # Exploration rate
        self.username = username
        self.filename = f'q_table_{self.username}.json' # File to save/load Q-table
        self.q_table = self.load_q_table()
        
    def change_user(self, new_username):
        """Switches the active user and loads their specific Q-table."""
        self.username = new_username
        self.filename = f'q_table_{self.username}.json'
        self.q_table = self.load_q_table()


    def load_q_table(self):
        """Loads the Q-table from a file, creating an empty one if not found."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}

    def save_q_table(self):
        """Saves the Q-table to a file."""
        with open(self.filename, 'w') as f:
            json.dump(self.q_table, f)

    def get_q_value(self, state, action):
        """Returns the Q-value for a state-action pair."""
        state_key = str(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {act: 0.0 for act in self.actions}
            self.save_q_table()
        
        # Ensure action exists in case actions were updated
        if action not in self.q_table[state_key]:
            self.q_table[state_key][action] = 0.0

        return self.q_table[state_key][action]

    def choose_action(self, state):
        """Selects an action using the epsilon-greedy policy."""
        state_key = str(state)
        
        # Ensure state exists
        if state_key not in self.q_table:
            self.q_table[state_key] = {act: 0.0 for act in self.actions}
            self.save_q_table()
            
        if random.uniform(0, 1) < self.epsilon:
            # Explore: choose random action
            return random.choice(self.actions)
        else:
            # Exploit: choose best action based on Q-values
            state_actions = self.q_table[state_key]
            max_q = max(state_actions.values())
            # Handle ties randomly
            best_actions = [act for act, q in state_actions.items() if q == max_q]
            return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        """Updates the Q-value using the Q-learning formula."""
        old_q = self.get_q_value(state, action)
        
        # Future value
        next_state_key = str(next_state)
        # Ensure next state exists
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {act: 0.0 for act in self.actions}
            
        next_max = max(self.q_table[next_state_key].values())
        
        # Q-learning formula
        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        
        # Update and save
        self.q_table[str(state)][action] = new_q
        self.save_q_table()
