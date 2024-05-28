from games.hlpoker.action import HLPokerAction
from games.hlpoker.player import HLPokerPlayer
from games.hlpoker.round import Round
from games.hlpoker.state import HLPokerState
from games.state import State
from collections import Counter

class DynamicCacheHeuristicHLPokerPlayer(HLPokerPlayer):
    def __init__(self, name):
        super().__init__(name)
        self.hand_strength_cache = {}  # Cache para armazenar as avaliações de força da mão
        self.max_cache_size = 1000  # Tamanho inicial máximo do cache
        self.cache_hit_count = Counter()  # Contador de quantas vezes cada avaliação foi usada
        self.games_played = 0  # Contador de jogos jogados
        self.cache_retention_games = 1000  # Número de jogos para reter as avaliações das cartas no cache
        self.new_entries_count = 0  # Contador de novas entradas no cache durante um jogo
        self.avg_entries_per_game = 0  # Média de novas entradas no cache por jogo

    def get_action_with_cards(self, state: HLPokerState, private_cards, board_cards):
        # Avaliar a força da mão usando uma heurística simples
        hand_strength = self.evaluate_hand_strength(private_cards, board_cards)

        # Obter informações do estado atual do jogo
        num_players = state.get_num_players()
        pot = state.get_pot()
        current_bet = state.get_spent(self.get_current_pos())

        # Com base na força da mão e nas informações do jogo, escolher uma ação
        if hand_strength >= 0.7:
            # Se a mão for forte o suficiente, aumentar agressivamente
            return HLPokerAction.RAISE
        elif hand_strength >= 0.2:
            # Se a mão for moderadamente forte, fazer call
            return HLPokerAction.CALL
        else:
            # Se a mão for fraca, fazer fold
            return HLPokerAction.FOLD

    def evaluate_hand_strength(self, private_cards, board_cards):
        # Converter as instâncias de Card em tuplas hashable
        private_card_keys = [(card.rank.value, card.suit.value) for card in private_cards]
        board_card_keys = [(card.rank.value, card.suit.value) for card in board_cards]

        # Verificar se a avaliação já está em cache
        key = tuple(private_card_keys + board_card_keys)
        if key in self.hand_strength_cache:
            # Atualizar o contador de hits para a entrada do cache
            self.cache_hit_count[key] += 1
            return self.hand_strength_cache[key]

        # Apenas retornar um valor fictício para demonstração
        return 0.5  

    def update_cache(self, key, hand_strength):
        # Atualizar o cache e remover as entradas mais antigas, se necessário
        if len(self.hand_strength_cache) >= self.max_cache_size:
            self.evict_old_entries()
        # Adicionar a nova avaliação ao cache
        self.hand_strength_cache[key] = hand_strength
        # Atualizar o contador de hits para a nova entrada
        self.cache_hit_count[key] += 1
        # Atualizar o contador de novas entradas no cache
        self.new_entries_count += 1

    def evict_old_entries(self):
        # Remover as entradas mais antigas do cache
        if self.hand_strength_cache:
            num_entries_to_remove = len(self.hand_strength_cache) - self.max_cache_size + 1
            cache_sizes = [len(cache_entry) for cache_entry in self.hand_strength_cache.values()]
            for _ in range(num_entries_to_remove):
                least_used_index = cache_sizes.index(min(cache_sizes))
                least_used_key = list(self.hand_strength_cache.keys())[least_used_index]
                del self.hand_strength_cache[least_used_key]
                del self.cache_hit_count[least_used_key]
                cache_sizes.pop(least_used_index)

    # Métodos de eventos não alterados
    def event_my_action(self, action, new_state):
        pass

    def event_opponent_action(self, action, new_state):
        pass

    def event_new_game(self):
        # Incrementar o contador de jogos jogados
        self.games_played += 1
        # Se o número de jogos jogados for múltiplo do número de jogos para retenção do cache,
        # atualizar o tamanho máximo do cache com base na média de novas entradas por jogo
        if self.games_played % self.cache_retention_games == 0:
            self.update_cache_size()

    def event_end_game(self, final_state: State):
        pass

    def event_result(self, pos: int, result: int):
        pass

    def event_new_round(self, round: Round):
        # Limpar o cache no início de um novo round para reavaliar as mãos com base nas novas cartas do tabuleiro
        self.hand_strength_cache = {}
        # Resetar o contador de novas entradas no cache
        self.new_entries_count = 0

    def event_end_round(self, round: Round):
        pass

    def update_cache_size(self):
        # Calcular a média de novas entradas no cache por jogo
        self.avg_entries_per_game = self.new_entries_count / self.cache_retention_games
        # Ajustar o tamanho máximo do cache com base na média de novas entradas por jogo
        self.max_cache_size = int(self.avg_entries_per_game * 1.5)  # Aumentar o tamanho em 50% para garantir espaço suficiente

        # Resetar o contador de novas entradas no cache para o próximo período de retenção
        self.new_entries_count = 0
