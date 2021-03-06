import random
from copy import deepcopy

from tic_tac_toe import TicTacToeAgent, TicTacToeState, TicTacToeAction, State, Action


class LearningAgent(TicTacToeAgent):
    def __init__(self, symbol: str, world, task, alpha=0.2, epsilon=0.1,
                 initial_value=0.5, update_exploratory=False, random_tie_breaking=False):
        super().__init__(symbol, world, task)
        self.random_tie_breaking = random_tie_breaking
        self.update_exploratory = update_exploratory
        self.table = {}
        self.alpha = alpha
        self.epsilon = epsilon
        self.initial_value = initial_value
        self.previous_state = world.current_state()
        self.previous_move = None
        self.was_exploratory = False

    def value_of_state(self, state: State) -> float:
        existing_value = self.table.get(state)

        if existing_value is None:
            new_value = self.initial_value
            winner = self.task.winner(state)
            if winner == self.symbol:
                new_value = 1.0
            elif winner != self.symbol and winner is not None:
                new_value = 0.0
            elif self.task.draw(state):
                new_value = 1.0

            self.table[state] = new_value

        return self.table.get(state)

    def value_of_action_in_state(self, state, x, y) -> float:
        return self.value_of_state(self.state_for_action(state, x, y))

    def state_for_action(self, state, x, y) -> State:
        representation_copy = deepcopy(state.representation)
        representation_copy[y][x] = self.symbol
        return TicTacToeState(representation_copy)

    def choose_action(self, state) -> Action:
        options = []
        for y in range(0, len(state.representation)):
            for x in range(0, len(state.representation[0])):
                if state.representation[y][x] is None:
                    options.append((x, y))

        if random.random() < self.epsilon:
            self.was_exploratory = True

            choice = random.choice(options)
            self.previous_state = state
            self.previous_move = self.state_for_action(state, choice[0],
                                                       choice[1])

            if self.update_exploratory:
                self.update_value(self.previous_state, state)
                self.previous_state = state

                if self.previous_move is not None:
                    self.update_value(self.previous_move, state)
                self.previous_move = self.state_for_action(state, choice[0],
                                                           choice[1])
            return TicTacToeAction(self.symbol, choice[0], choice[1])
        else:
            self.was_exploratory = False

        max_options = {}
        max_value = float("-inf")
        for option in options:
            value = self.value_of_action_in_state(state, option[0], option[1])
            if value > max_value:
                max_value = value
                max_options = [option]
            elif value == max_value:
                max_options.append(option)

        assert max_options[0] is not None

        if self.random_tie_breaking:
            max_option = random.choice(max_options)
        else:
            max_option = max_options[0]


        self.update_value(self.previous_state, state)
        self.previous_state = state

        if self.previous_move is not None:
            self.update_value(self.previous_move, state)
        self.previous_move = self.state_for_action(state, max_option[0],
                                                   max_option[1])

        return TicTacToeAction(self.symbol, max_option[0], max_option[1])

    def update_value(self, state, state_prime):
        if self.was_exploratory and not self.update_exploratory:
            return
        prev_value = self.value_of_state(state)
        prime_value = self.value_of_state(state_prime)

        error = prime_value - prev_value
        self.table[state] = prev_value + self.alpha * error

    def prepare_for_new_episode(self, state):
        self.previous_state = state

    def see_result(self, state: State):
        assert state != self.previous_state
        self.update_value(self.previous_state, state)
        self.update_value(self.previous_move, state)
        self.previous_state = None
        self.previous_move = None
