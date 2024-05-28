from games.hlpoker.action import HLPokerAction
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.state import HLPokerState
from games.hlpoker.round import Round
from concurrent.futures import ProcessPoolExecutor
from collections import Counter
import random
import math

class MonteCarloPlayer(HLPokerPlayer):
    def __init__(self, name):
        super().__init__(name)
        self.total_simulations = 0
        self.wins = {action: 0 for action in HLPokerAction}
        self.plays = {action: 0 for action in HLPokerAction}
        self.hand_eval_weights = {
            "flush": 10,
            "straight": 8,
            "three_of_a_kind": 6,
            "two_pair": 4,
            "pair": 2
        }

    def get_action_with_cards(self, state, private_cards, board_cards):
        num_simulations_per_process = 200 // 10  # Dividindo o número total de simulações entre 5 processos
        # Use o número adequado de simulações e ajuste conforme necessário
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.run_simulations, state.clone(), private_cards, board_cards, num_simulations_per_process) for _ in range(10)]
            results = [future.result() for future in futures]
        return max(state.get_possible_actions(), key=lambda a: self.ucb_value(a))

    def run_simulations(self, state, private_cards, board_cards, num_simulations):
        for _ in range(num_simulations):
            self.simulate(state.clone(), private_cards, board_cards)

    def simulate(self, state, private_cards, board_cards):
        visited = set()
        current_round = state.get_current_round()
        state_tuple = tuple(state.get_sequence())
        own_position = self.get_current_pos()

        while not state.is_finished():
            possible_actions = state.get_possible_actions()

            if current_round != state.get_current_round():
                current_round = state.get_current_round()
                visited.clear()

            if all(self.plays[a] > 0 for a in possible_actions):
                action = max(possible_actions, key=lambda a: self.ucb_value(a))
            else:
                action = self.choose_action_based_on_strategy(state, private_cards, board_cards)

            visited.add(state_tuple)

            state.update(action)
            if tuple(state.get_sequence()) in visited:
                break

            # Avaliação da mão atual
            hand_strength = self.evaluate_hand(private_cards, board_cards)

            # Probabilidade de vencer
            win_probability = self.calculate_win_probability(hand_strength, state, private_cards, board_cards)

            # Ajuste da estratégia com base na situação atual
            if win_probability > 0.5:
                action = HLPokerAction.RAISE  # Aumentar se a probabilidade de vitória for alta
            elif win_probability > 0.3:
                action = HLPokerAction.CALL  # Chamar se a probabilidade de vitória for moderada
            else:
                action = HLPokerAction.FOLD  # Desistir se a probabilidade de vitória for baixa

            self.total_simulations += 1
            self.plays[action] += 1
            if state.get_result(own_position) > 0:
                self.wins[action] += 1

    def calculate_win_probability(self, hand_strength, state, private_cards, board_cards):
        # Lógica para calcular a probabilidade de vitória com base na avaliação da mão e na situação atual do jogo
        # Você pode implementar uma lógica mais avançada aqui, considerando as informações disponíveis
        # Como exemplo, retornarei uma probabilidade fixa de 0.5
        return 0.5

    def choose_action_based_on_strategy(self, state, private_cards, board_cards):
        possible_actions = state.get_possible_actions()
        weighted_choices = []
        weights = [0.9, 0.6, 0.0]  # Exemplo de pesos ajustados

        for action in possible_actions:
            if action == HLPokerAction.RAISE:
                weighted_choices.append((action, weights[0]))
            elif action == HLPokerAction.CALL:
                weighted_choices.append((action, weights[1]))
            elif action == HLPokerAction.FOLD:
                weighted_choices.append((action, weights[2]))

        selected_action = self.random_choice_weighted(weighted_choices)
        return selected_action

    def ucb_value(self, action):
        if self.plays[action] == 0:
            return float('inf')
        else:
            exploitation = self.wins[action] / self.plays[action]
            exploration = math.sqrt(math.log(self.total_simulations) / self.plays[action])
            return exploitation + exploration

    def evaluate_hand(self, private_cards, board_cards):
        hand_strength = self.evaluate_hand_sophisticated(private_cards, board_cards)
        return hand_strength

    def evaluate_hand_sophisticated(self, private_cards, board_cards):
        hand_combinations = private_cards + board_cards
        # Exemplo: Pontuação baseada na força das cartas mais altas
        score = sum(card.rank.value for card in hand_combinations) / len(hand_combinations)
        # Adicione lógica para verificar flush, straight, three of a kind, etc.
        # Atualize a pontuação com base na presença dessas combinações
        return score

    def get_hand_rank(self, hand):
        # Calcula o rank da mão com base em diferentes combinações de mãos vencedoras
        flush_rank = self.evaluate_flush(hand)
        straight_rank = self.evaluate_straight(hand)
        three_of_a_kind_rank = self.evaluate_three_of_a_kind(hand)
        two_pair_rank = self.evaluate_two_pair(hand)
        pair_rank = self.evaluate_pair(hand)

        # Combina os ranks ponderados
        rank = (flush_rank * self.hand_eval_weights["flush"] +
                straight_rank * self.hand_eval_weights["straight"] +
                three_of_a_kind_rank * self.hand_eval_weights["three_of_a_kind"] +
                two_pair_rank * self.hand_eval_weights["two_pair"] +
                pair_rank * self.hand_eval_weights["pair"])

        return rank

    def evaluate_flush(self, hand):
        # Avalia se há um flush
        suits = [card.suit for card in hand]
        suit_count = Counter(suits)
        if max(suit_count.values()) >= 5:
            return 1
        return 0

    def evaluate_straight(self, hand):
        # Avalia se há uma sequência
        ranks = sorted([card.rank.value for card in hand])  # Usar os valores das classificações em vez dos objetos Rank
        straight_count = 1
        for i in range(1, len(ranks)):
            if ranks[i] == ranks[i - 1] + 1:
                straight_count += 1
                if straight_count >= 5:
                    return 1
            else:
                straight_count = 1
        return 0

    def evaluate_three_of_a_kind(self, hand):
        # Avalia se há uma trinca
        rank_count = Counter([card.rank for card in hand])
        for rank, count in rank_count.items():
            if count >= 3:
                return 1
        return 0

    def evaluate_two_pair(self, hand):
        # Avalia se há dois pares
        rank_count = Counter([card.rank for card in hand])
        pairs = [rank for rank, count in rank_count.items() if count >= 2]
        if len(pairs) >= 2:
            return 1
        return 0

    def evaluate_pair(self, hand):
        # Avalia se há um par
        rank_count = Counter([card.rank for card in hand])
        for count in rank_count.values():
            if count >= 2:
                return 1
        return 0

    def random_choice_weighted(self, weighted_choices):
        total = sum(weight for _, weight in weighted_choices)
        r = random.uniform(0, total)
        upto = 0
        for choice, weight in weighted_choices:
            if upto + weight >= r:
                return choice
            upto += weight

    # Métodos de evento omitidos por brevidade

    def event_my_action(self, action, new_state):
        pass

    def event_opponent_action(self, action, new_state):
        pass

    def event_new_game(self):
        pass

    def event_end_game(self, final_state: HLPokerState):
        pass

    def event_result(self, pos: int, result: int):
        pass

    def event_new_round(self, round: Round):
        pass
