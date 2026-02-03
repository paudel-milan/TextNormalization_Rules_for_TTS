"""
Rule-based Normalizers
Convert detected tokens to spoken Hindi form
"""

import re


class NumberToWordsConverter:
    """
    Converts numbers to Hindi words using Indian numbering system
    Supports: ones, tens, hundreds, thousands, lakhs, crores
    """
    
    def __init__(self, resources):
        """
        Initialize with language resources
        
        Args:
            resources: Dictionary containing number mappings
        """
        self.ones = resources['numbers']['ones']
        self.tens = resources['numbers']['tens']
        self.scales = resources['numbers']['scales']
    
    def convert(self, number):
        """
        Convert a number to Hindi words
        
        Args:
            number: Integer to convert
            
        Returns:
            Hindi word representation
        """
        if number == 0:
            return self.ones['0']
        
        if number < 0:
            return 'माइनस ' + self.convert(-number)
        
        # Handle numbers up to 99
        if number < 100:
            return self._convert_below_hundred(number)
        
        # Handle numbers up to 999
        if number < 1000:
            return self._convert_hundreds(number)
        
        # Handle thousands, lakhs, crores (Indian system)
        return self._convert_indian_system(number)
    
    def _convert_below_hundred(self, num):
        """Convert numbers 0-99 to Hindi words"""
        if num < 10:
            return self.ones[str(num)]
        
        if num < 20:
            return self.tens[str(num)]
        
        # For 20-99
        tens_digit = (num // 10) * 10
        ones_digit = num % 10
        
        if ones_digit == 0:
            return self.tens[str(tens_digit)]
        
        # Special compound forms in Hindi
        if str(num) in self.tens:
            return self.tens[str(num)]
        
        return self.tens[str(tens_digit)] + ' ' + self.ones[str(ones_digit)]
    
    def _convert_hundreds(self, num):
        """Convert numbers 100-999 to Hindi words"""
        hundreds_digit = num // 100
        remainder = num % 100
        
        result = self.ones[str(hundreds_digit)] + ' ' + self.scales['hundred']
        
        if remainder > 0:
            result += ' ' + self._convert_below_hundred(remainder)
        
        return result
    
    def _convert_indian_system(self, num):
        """
        Convert large numbers using Indian numbering system
        Indian system: ones, tens, hundreds, thousands, lakhs, crores
        """
        if num >= 10000000:  # Crore (1,00,00,000)
            crores = num // 10000000
            remainder = num % 10000000
            result = self.convert(crores) + ' ' + self.scales['crore']
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        
        if num >= 100000:  # Lakh (1,00,000)
            lakhs = num // 100000
            remainder = num % 100000
            result = self.convert(lakhs) + ' ' + self.scales['lakh']
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        
        if num >= 1000:  # Thousand (1,000)
            thousands = num // 1000
            remainder = num % 1000
            result = self.convert(thousands) + ' ' + self.scales['thousand']
            if remainder > 0:
                result += ' ' + self.convert(remainder)
            return result
        
        return str(num)


class CurrencyNormalizer:
    """
    Normalizes currency amounts to spoken Hindi form
    Handles rupees and paise
    """
    
    def __init__(self, resources):
        """
        Initialize with language resources
        
        Args:
            resources: Dictionary containing currency rules
        """
        self.resources = resources
        self.converter = NumberToWordsConverter(resources)
        self.currency_units = resources['currency']
    
    def normalize(self, text):
        """
        Normalize currency text to spoken form
        
        Examples:
            ₹500 → पाँच सौ रुपये
            ₹500.50 → पाँच सौ रुपये पचास पैसे
            
        Args:
            text: Currency text (e.g., "₹500", "500.50")
            
        Returns:
            Normalized Hindi text
        """
        # Remove currency symbols
        amount_text = re.sub(r'^[₹रुRsINR.\s]+', '', text)
        
        # Split into rupees and paise
        if '.' in amount_text:
            parts = amount_text.split('.')
            rupees = int(parts[0])
            paise = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        else:
            rupees = int(amount_text)
            paise = 0
        
        # Convert rupees
        result = self.converter.convert(rupees)
        
        # Add rupee unit (singular/plural)
        if rupees == 1:
            result += ' ' + self.currency_units['main_unit']['singular']
        else:
            result += ' ' + self.currency_units['main_unit']['plural']
        
        # Add paise if present
        if paise > 0:
            result += ' ' + self.converter.convert(paise)
            if paise == 1:
                result += ' ' + self.currency_units['sub_unit']['singular']
            else:
                result += ' ' + self.currency_units['sub_unit']['plural']
        
        return result


class CardinalNormalizer:
    """
    Normalizes cardinal numbers to spoken Hindi form
    """
    
    def __init__(self, resources):
        """
        Initialize with language resources
        
        Args:
            resources: Dictionary containing number mappings
        """
        self.converter = NumberToWordsConverter(resources)
    
    def normalize(self, text):
        """
        Normalize cardinal number to spoken form
        
        Examples:
            123 → एक सौ तेईस
            1000 → एक हज़ार
            
        Args:
            text: Number text (e.g., "123", "1000")
            
        Returns:
            Normalized Hindi text
        """
        number = int(text)
        return self.converter.convert(number)
