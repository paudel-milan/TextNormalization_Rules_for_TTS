"""
Named Entity DFA — detects known abbreviations and titles (rule-based, NOT ML NER).
"""

from .base import BaseDFA


class NamedEntityDFA(BaseDFA):
    """
    DFA for detecting known abbreviations and titles.

    Patterns recognised:
        Hindi titles : डॉ., श्री, श्रीमती, प्रो., मो.
        English titles: Dr., Mr., Mrs., Prof.
        Abbreviations : भा.ज.पा., कां., आ.आ.पा.

    The lookup table comes from the language resource file.

    State Machine:
        START → ENTITY_MATCH → END
    """

    _DEFAULT_ENTITIES = {
        'डॉ.', 'डॉ', 'श्री', 'श्रीमती', 'सुश्री',
        'प्रो.', 'प्रो', 'मो.',
        'Dr.', 'Mr.', 'Mrs.', 'Ms.', 'Prof.',
        'Sr.', 'Jr.', 'St.', 'Smt.', 'Shri', 'Km.',
        'भा.ज.पा.', 'कां.', 'आ.आ.पा.', 'रा.स्व.सं.',
    }

    def __init__(self, known_entities=None):
        super().__init__()
        self.states = ['START', 'ENTITY_MATCH', 'END']
        self._entities = set(known_entities) if known_entities else self._DEFAULT_ENTITIES

    def match(self, text):
        states_traversed = ['START']
        if text in self._entities:
            states_traversed.extend(['ENTITY_MATCH', 'END'])
            return {
                'matched': True,
                'states': states_traversed,
                'entity': text,
            }
        return {'matched': False, 'states': states_traversed}
