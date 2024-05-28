import numpy as np
from games.connect4.action import Connect4Action
from games.connect4.player import Connect4Player
from games.connect4.state import Connect4State
from games.connect4.result import Connect4Result
from games.state import State
import random
import time

class MCTSNode:
    def __init__(self, state: Connect4State, parent=None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.wins = 0

    def select_action(self):
        return max(self.children.keys(), key=lambda action: self.children[action].wins / (self.children[action].visits + 1e-6))

    def expand(self):
        actions = self.state.get_possible_actions()
        for action in actions:
            next_state = self.state.clone()
            next_state.play(action)
            self.children[action] = MCTSNode(next_state, parent=self)

    def backpropagate(self, result):
        self.visits += 1
        self.wins += result
        if self.parent:
            self.parent.backpropagate(result)

class MCTSConnect4Player(Connect4Player):
    def __init__(self, name, iterations=10):
        super().__init__(name)
        self.iterations = iterations

    def get_action(self, state: Connect4State):
        
        root = MCTSNode(state)
        for _ in range(self.iterations):
            node = root
            while node.children:
                action = random.choice(list(node.children.keys()))
                node = node.children[action]
            node.expand()
            result = self.simulate(node.state)
            node.backpropagate(result)
        
        return root.select_action()

    def simulate(self, state: Connect4State):
        while not state.is_finished():
            action = random.choice(state.get_possible_actions())
            state.play(action)
        result = state.get_result(self.get_current_pos())
        return 1 if result == Connect4Result.WIN.value else 0

    def event_action(self, pos: int, action, new_state: State):
        pass

    def event_end_game(self, final_state: State):
        pass
