from enum import Enum


class AuthProtocol:
    def __init__(self):
        pass


class AuthState(Enum):
    not_connected = 0
    connected = 1
    logging_in = 2
    logged_in = 3
    realmlist_ready = 4
    disconnected = 5


class AuthAction(Enum):
    connect = 0


_transitions = dict((AuthState.not_connected))


class AuthStateMachine:
    def __init__(self):
        self._state = AuthState.not_connected

    # def process_action(self, action):
    #     self._
