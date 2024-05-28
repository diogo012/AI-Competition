from games.minesweeper.action import MinesweeperAction
from games.minesweeper.player import MinesweeperPlayer
from games.minesweeper.state import MinesweeperState
from games.state import State

class RiskMinimizingMinesweeperPlayer(MinesweeperPlayer):

    def __init__(self, name):
        super().__init__(name)

    def get_action(self, state: MinesweeperState):
        possible_actions = list(state.get_possible_actions())
        # Ordenar as ações com base no risco calculado
        sorted_actions = sorted(possible_actions, key=lambda action: self.calculate_risk(state, action))
        # Escolher a ação com menor risco
        return sorted_actions[0]

    def calculate_risk(self, state: MinesweeperState, action: MinesweeperAction) -> float:
        # Obter as coordenadas da ação
        row, col = action.get_row(), action.get_col()
        # Obter o valor da célula no tabuleiro
        cell_value = state.get_grid()[row][col]
        # Se a célula já estiver revelada ou marcada, o risco é infinito
        if cell_value != MinesweeperState.EMPTY_CELL:
            return float('inf')

        # Calcular o risco com base nos vizinhos
        risk = 0
        for r in range(max(0, row - 1), min(state.get_num_rows(), row + 2)):
            for c in range(max(0, col - 1), min(state.get_num_cols(), col + 2)):
                # Se a célula vizinha for uma mina, aumentar o risco
                if (r, c) in state._MinesweeperState__mines:
                    risk += 1
        return risk

    def event_action(self, pos: int, action, new_state: State):
        # ignore
        pass

    def event_end_game(self, final_state: State):
        # ignore
        pass