from games.connect4.action import Connect4Action
from games.connect4.player import Connect4Player
from games.connect4.state import Connect4State
from games.connect4.result import Connect4Result
from games.state import State
from math import inf

class MinimaxConnect4Player(Connect4Player):
    def __init__(self, name):
        super().__init__(name)
        self.states_evaluated = {}
        self.iteration_count = 0

    def get_action(self, state: Connect4State):
        self.states_evaluated.clear()  # Limpar a tabela de transposição a cada novo movimento
        self.iteration_count = 0
        best_action, _ = self.minimax(state, depth=2, maximizing_player=True, alpha=-inf, beta=inf)
        return best_action

    def minimax(self, state: Connect4State, depth, maximizing_player, alpha, beta):
        self.iteration_count += 1
        if depth == 0 or state.is_finished():
            return None, self.evaluate_state(state) or 0  # Retorna 0 se a avaliação for None

        if state in self.states_evaluated:  # Verificar se o estado já foi avaliado
            return None, self.states_evaluated[state]

        if maximizing_player:
            max_eval = -inf
            best_action = None
            actions = self.order_actions(state.get_possible_actions())  # Ordenar as ações
            for action in actions:
                next_state = self.get_next_state(state, action)
                _, eval_value = self.minimax(next_state, depth-1, False, alpha, beta)
                if eval_value is not None and eval_value > max_eval:  # Verifica se a avaliação é None
                    max_eval = eval_value
                    best_action = action
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break
            self.states_evaluated[state] = max_eval  # Salvar o valor avaliado na tabela de transposição
            return best_action, max_eval
        else:
            min_eval = inf
            best_action = None
            actions = self.order_actions(state.get_possible_actions())  # Ordenar as ações
            for action in actions:
                next_state = self.get_next_state(state, action)
                _, eval_value = self.minimax(next_state, depth-1, True, alpha, beta)
                if eval_value is not None and eval_value < min_eval:  # Verifica se a avaliação é None
                    min_eval = eval_value
                    best_action = action
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break
            self.states_evaluated[state] = min_eval  # Salvar o valor avaliado na tabela de transposição
            return best_action, min_eval
        
    def get_next_state(self, state, action):
        next_state = state.clone()
        next_state.play(action)
        return next_state

    def evaluate_state(self, state):
        if state.is_finished():
            result = state.get_result(self.get_current_pos())
            if result == Connect4Result.WIN.value:
                return 100
            elif result == Connect4Result.LOOSE.value:
                return -100
            else:
                return 0

    def order_actions(self, actions):
        # Ordenar as ações de acordo com alguma heurística (por exemplo, preferir o centro)
        return sorted(actions, key=lambda action: abs(action.get_col() - 3))

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass
