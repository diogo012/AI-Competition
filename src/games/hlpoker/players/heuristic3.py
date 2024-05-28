from games.hlpoker.action import HLPokerAction
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.round import Round
from games.hlpoker.state import HLPokerState
from games.state import State
from itertools import combinations
from collections import defaultdict
from collections import OrderedDict

class AdvancedHeuristicHLPokerPlayer(HLPokerPlayer):
    def __init__(self, name):
        super().__init__(name)
        self.hand_strength_cache = OrderedDict()  # Cache para armazenar as avaliações de força da mão
        self.max_cache_size = 1000  # Tamanho máximo do cache
        self.cache_hit_count = defaultdict(int)  # Contador de quantas vezes cada avaliação foi usada

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        # Avaliar a força da mão usando uma heurística simples
        hand_strength = self.evaluate_hand_strength(private_cards, board_cards)

        # Com base na força da mão e nas informações do jogo, escolher uma ação
        if hand_strength >= 0.7:
            # Se a mão for forte o suficiente, aumentar agressivamente
            return HLPokerAction.RAISE
        elif hand_strength >= 0.5:
            # Se a mão for moderadamente forte, fazer call
            return HLPokerAction.CALL
        else:
            # Se a mão for fraca, fazer fold
            return HLPokerAction.FOLD

    def evaluate_hand_strength(self, private_cards, board_cards):
        # Verificar se a avaliação já está em cache
        key = tuple(private_cards + board_cards)
        if key in self.hand_strength_cache:
            # Atualizar o contador de hits para a entrada do cache
            self.cache_hit_count[key] += 1
            return self.hand_strength_cache[key]

        # Calcular a força da mão
        hand_strength = self.calculate_hand_strength(private_cards, board_cards)

        # Armazenar a avaliação no cache
        self.update_cache(key, hand_strength)

        return hand_strength

    def update_cache(self, key, hand_strength):
        # Atualizar o cache e remover a entrada menos utilizada, se necessário
        if len(self.hand_strength_cache) >= self.max_cache_size:
            # Encontrar a entrada menos utilizada no cache
            least_used_key = min(self.cache_hit_count, key=self.cache_hit_count.get)
            # Remover a entrada menos utilizada do cache
            del self.hand_strength_cache[least_used_key]
            del self.cache_hit_count[least_used_key]
        # Adicionar a nova avaliação ao cache
        self.hand_strength_cache[key] = hand_strength
        # Atualizar o contador de hits para a nova entrada
        self.cache_hit_count[key] += 1

    def calculate_hand_strength(self, private_cards, board_cards):
        # Implementar uma heurística simples para avaliar a força da mão
        # Aqui, podemos considerar critérios como valor do par, número de outs, textura do board, etc.
        # Utilizar algum algoritmo de avaliação de mãos de poker pode ser útil
        return 0.5  # Valor fictício para demonstração

    # Métodos de eventos não alterados
    def event_my_action(self, action, new_state):
        pass

    def event_opponent_action(self, action, new_state):
        pass

    def event_new_game(self):
        # Não precisa limpar o cache entre os jogos para manter as avaliações de força da mão
        pass

    def event_end_game(self, final_state: State):
        pass

    def event_result(self, pos: int, result: int):
        pass

    def event_new_round(self, round: round):
        # Limpar o cache no início de um novo round para reavaliar as mãos com base nas novas cartas do tabuleiro
        self.hand_strength_cache = {}