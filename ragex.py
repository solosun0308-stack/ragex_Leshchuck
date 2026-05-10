from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current state
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):
    next_states: list[State] = []

    def __init__(self):
        self.next_states = []
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):
    next_states: list[State] = []

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """
    next_states: list[State] = []

    def __init__(self):
        self.next_states = []
        super().__init__()

    def check_self(self, char: str):
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """
    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.next_states = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class PlusState(State):
    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:
    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        parent_state = self.curr_state
        last_state = self.curr_state

        for char in regex_expr:
            new_state = self.__init_next_state(char, parent_state, last_state)
            if char not in ("*", "+"):
                last_state.next_states.append(new_state)
                parent_state = last_state
                last_state = new_state
            else:
                parent_state = last_state
                last_state = new_state

        term = TerminationState()
        last_state.next_states.append(term)

    def __init_next_state(
        self, next_token: str, parent_state: State, last_state: State
    ) -> State:
        new_state = None
        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()

            case next_token if next_token == "*":
                new_state = StarState(last_state)
                if last_state in parent_state.next_states:
                    parent_state.next_states.remove(last_state)
                parent_state.next_states.append(new_state)
                new_state.next_states.append(new_state)

            case next_token if next_token == "+":
                new_state = PlusState(last_state)
                last_state.next_states.append(new_state)
                new_state.next_states.append(new_state)

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string: str) -> bool:
        def dfs(state, pos, visited=None):
            if visited is None:
                visited = set()
            key = (id(state), pos)
            if key in visited:
                return False
            visited = visited | {key}

            if pos == len(string):
                if isinstance(state, TerminationState):
                    return True
                for ns in state.next_states:
                    if isinstance(ns, TerminationState):
                        return True
                    if isinstance(ns, (StarState, PlusState)) and dfs(ns, pos, visited):
                        return True
                return False

            char = string[pos]
            for ns in state.next_states:
                if isinstance(ns, (StarState, PlusState)):
                    if dfs(ns, pos, visited):
                        return True
                    if ns.check_self(char) and dfs(ns, pos + 1, visited):
                        return True
                elif isinstance(ns, TerminationState):
                    pass
                else:
                    if ns.check_self(char) and dfs(ns, pos + 1, visited):
                        return True

            if isinstance(state, (StarState, PlusState)):
                if state.check_self(char) and dfs(state, pos + 1, visited):
                    return True

            return False

        return dfs(self.curr_state, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)
    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))        # True
    print(regex_compiled.check_string("meow"))        # False

    fsm = RegexFSM("a*b")
    print(fsm.check_string("b"))      # True
    print(fsm.check_string("aaab"))   # True
    print(fsm.check_string("c"))      # False

    fsm = RegexFSM("a+b")
    print(fsm.check_string("ab"))     # True
    print(fsm.check_string("aaab"))   # True
    print(fsm.check_string("b"))      # False

    fsm = RegexFSM("a.c")
    print(fsm.check_string("abc"))    # True
    print(fsm.check_string("a1c"))    # True
    print(fsm.check_string("ac"))     # False

    fsm = RegexFSM("ab*c")
    print(fsm.check_string("ac"))     # True
    print(fsm.check_string("abbc"))   # True
    print(fsm.check_string("aXc"))    # False

    fsm = RegexFSM("hello")
    print(fsm.check_string("hello"))  # True
    print(fsm.check_string("hell"))   # False
    print(fsm.check_string("helloo")) # False
