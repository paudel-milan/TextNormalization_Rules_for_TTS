"""
Base DFA class — all category-specific DFAs inherit from this.
"""


class BaseDFA:
    """
    Base class for DFA implementations.
    Each DFA represents a state machine for pattern recognition.
    """

    def __init__(self):
        self.states = []
        self.transitions = {}

    def match(self, text):
        """
        Check if text matches the DFA pattern.

        Returns:
            dict with at minimum:
                'matched': bool
                'states': list of states traversed
        """
        raise NotImplementedError
