from games.hlpoker.action import HLPokerAction
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.round import Round
from games.hlpoker.state import HLPokerState
from collections import Counter
from games.hlpoker.card import Rank, Suit
from games.state import State
import random

class CFRHLPokerPlayer(HLPokerPlayer):
    def __init__(self, name):
        super().__init__(name)
        self.regrets = {HLPokerAction.FOLD: 0, HLPokerAction.CALL: 0, HLPokerAction.RAISE: 0}
        self.strategy = {HLPokerAction.FOLD: 0, HLPokerAction.CALL: 0, HLPokerAction.RAISE: 0}

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        # Avalia a força da mão baseada em uma função de avaliação mais sofisticada
        hand_strength = self.evaluate_hand(private_cards + board_cards)

        # Calcula as probabilidades de diferentes ações com base na força da mão e no histórico de ações
        raise_probability = min(0.5, max(0, hand_strength - 0.3) / 0.5)
        call_probability = min(0.4, max(0, hand_strength - 0.2) / 0.5)

        # Ajusta as probabilidades com base na agressividade do oponente
        if state.get_acting_player() == 1:  # Se o oponente estiver agindo (raise), ajuste as probabilidades
            raise_probability *= 1.2  # Aumenta a probabilidade de raise em resposta a raises do oponente
            call_probability *= 0.8  # Reduz a probabilidade de call em resposta a raises do oponente

        # Escolhe uma ação com base nas probabilidades calculadas
        action_choice = random.uniform(0, 1)
        if action_choice < raise_probability:
            return HLPokerAction.RAISE
        elif action_choice < raise_probability + call_probability:
            return HLPokerAction.CALL
        else:
            return HLPokerAction.FOLD

    def evaluate_hand(self, cards):
        """
        Avalia a força de uma mão de poker com base nas cartas fornecidas.

        Args:
            cards (list[Card]): Lista de cartas que compõem a mão.

        Returns:
            float: Pontuação da mão. Quanto maior, mais forte a mão.
        """
        rank_counts = Counter(card.rank for card in cards)
        suit_counts = Counter(card.suit for card in cards)

        # Verifica se há um flush
        flush = any(count >= 5 for count in suit_counts.values())

        # Verifica se há uma sequência (straight)
        straight_potential = self.has_straight_potential(rank_counts)

        # Pontuação baseada na presença de flushes e sequências
        score = 0
        if flush:
            score += 50
        if straight_potential:
            score += 30

        # Consideração dos valores dos ranks para desempate
        for rank, count in rank_counts.items():
            score += rank.value * count

        return score

    def has_straight_potential(self, rank_counts):
        """
        Verifica se há potencial para uma sequência (straight) com base nos ranks presentes na mão.

        Args:
            rank_counts (Counter): Contagem de ocorrências de cada rank na mão.

        Returns:
            bool: True se houver potencial para uma sequência, False caso contrário.
        """
        sorted_ranks = sorted(rank_counts.keys(), key=lambda x: x.value)

        # Verifica se há três ou mais ranks consecutivos
        for i in range(len(sorted_ranks) - 2):
            if sorted_ranks[i].value + 1 == sorted_ranks[i + 1].value and sorted_ranks[i + 1].value + 1 == sorted_ranks[i + 2].value:
                return True

        # Verifica a possibilidade de uma sequência com A, 2, 3, 4, 5
        if Rank.Ace in rank_counts and Rank.Two in rank_counts and Rank.Three in rank_counts and Rank.Four in rank_counts and Rank.Five in rank_counts:
            return True

        return False

    def update_strategy(self, utility):
        normalizing_sum = sum(max(0, self.regrets[action]) for action in [HLPokerAction.FOLD, HLPokerAction.CALL, HLPokerAction.RAISE])

        if normalizing_sum > 0:
            self.strategy[HLPokerAction.FOLD] = max(0, self.regrets[HLPokerAction.FOLD]) / normalizing_sum
            self.strategy[HLPokerAction.CALL] = max(0, self.regrets[HLPokerAction.CALL]) / normalizing_sum
            self.strategy[HLPokerAction.RAISE] = max(0, self.regrets[HLPokerAction.RAISE]) / normalizing_sum
        else:
            self.strategy[HLPokerAction.FOLD] = 1.0 / 3
            self.strategy[HLPokerAction.CALL] = 1.0 / 3
            self.strategy[HLPokerAction.RAISE] = 1.0 / 3

        # Update regrets
        for action in [HLPokerAction.FOLD, HLPokerAction.CALL, HLPokerAction.RAISE]:
            self.regrets[action] += utility * (self.strategy[action] - 1 / 3)

    def event_end_game(self, final_state: HLPokerState):
        pos = self.get_current_pos()
        result = final_state.get_result(pos)
        self.update_strategy(result)

    def event_new_game(self):
        pass

    def event_my_action(self, action, new_state):
        pass

    def event_opponent_action(self, action, new_state):
        pass

    def event_result(self, pos: int, result: int):
        pass

    def event_new_round(self, round: Round):
        pass
