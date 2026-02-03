"""
DFA (Deterministic Finite Automaton) Engine
Implements state machines for pattern detection
"""

import re


class BaseDFA:
    """
    Base class for DFA implementations
    Each DFA represents a state machine for pattern recognition
    """
    
    def __init__(self):
        self.states = []
        self.transitions = {}
        
    def match(self, text):
        """
        Check if text matches the DFA pattern
        
        Returns:
            {
                'matched': bool,
                'states': [list of states traversed]
            }
        """
        raise NotImplementedError


class CurrencyDFA(BaseDFA):
    """
    DFA for detecting currency patterns in Hindi
    
    Patterns recognized:
    - ₹500
    - ₹500.50
    - रु500
    - 500 रुपये
    - Rs. 500
    
    State Machine:
    START → CURRENCY_SYMBOL → INTEGER_PART → [DECIMAL_POINT → DECIMAL_PART] → END
    """
    
    def __init__(self):
        super().__init__()
        
        # Define states
        self.states = [
            'START',
            'CURRENCY_SYMBOL',
            'INTEGER_PART',
            'DECIMAL_POINT',
            'DECIMAL_PART',
            'END'
        ]
        
        # Currency symbols and keywords
        self.currency_symbols = ['₹', 'रु', 'Rs', 'Rs.', 'INR']
        
    def match(self, text):
        """
        Match currency patterns using DFA
        
        State transitions:
        1. START → CURRENCY_SYMBOL (if starts with ₹, रु, Rs, etc.)
        2. CURRENCY_SYMBOL → INTEGER_PART (if followed by digits)
        3. INTEGER_PART → DECIMAL_POINT (if followed by .)
        4. DECIMAL_POINT → DECIMAL_PART (if followed by digits)
        5. DECIMAL_PART → END
        """
        states_traversed = ['START']
        
        # Pattern 1: ₹500 or ₹500.50
        pattern1 = r'^[₹रु]|^Rs\.?|^INR'
        if re.match(pattern1, text):
            states_traversed.append('CURRENCY_SYMBOL')
            
            # Extract number part
            number_part = re.sub(r'^[₹रुRsINR.]+\s*', '', text)
            
            # Check for integer part
            if re.match(r'^\d+', number_part):
                states_traversed.append('INTEGER_PART')
                
                # Check for decimal
                if '.' in number_part:
                    parts = number_part.split('.')
                    if len(parts) == 2 and parts[1].isdigit():
                        states_traversed.append('DECIMAL_POINT')
                        states_traversed.append('DECIMAL_PART')
                
                states_traversed.append('END')
                return {'matched': True, 'states': states_traversed}
        
        # Pattern 2: 500 रुपये or 500 (standalone number that could be currency)
        pattern2 = r'^\d+\.?\d*$'
        if re.match(pattern2, text):
            states_traversed.append('INTEGER_PART')
            
            if '.' in text:
                states_traversed.append('DECIMAL_POINT')
                states_traversed.append('DECIMAL_PART')
            
            states_traversed.append('END')
            return {'matched': True, 'states': states_traversed}
        
        return {'matched': False, 'states': states_traversed}


class CardinalDFA(BaseDFA):
    """
    DFA for detecting cardinal numbers
    
    Patterns recognized:
    - 123
    - 1234
    - 12345
    - etc.
    
    State Machine:
    START → DIGIT → [DIGIT]* → END
    """
    
    def __init__(self):
        super().__init__()
        
        self.states = [
            'START',
            'DIGIT',
            'END'
        ]
    
    def match(self, text):
        """
        Match cardinal number patterns
        
        State transitions:
        1. START → DIGIT (if starts with digit)
        2. DIGIT → DIGIT (for each additional digit)
        3. DIGIT → END
        """
        states_traversed = ['START']
        
        # Check if text is a pure number
        if re.match(r'^\d+$', text):
            states_traversed.append('DIGIT')
            
            # Each digit is a state transition
            for _ in text[1:]:
                states_traversed.append('DIGIT')
            
            states_traversed.append('END')
            return {'matched': True, 'states': states_traversed}
        
        return {'matched': False, 'states': states_traversed}
