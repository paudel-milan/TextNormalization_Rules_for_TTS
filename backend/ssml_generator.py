"""
SSML Generator Module
Generates Speech Synthesis Markup Language output for TTS
"""


class SSMLGenerator:
    """
    Generates SSML markup for normalized text
    Adds appropriate tags and prosody hints for different categories
    """
    
    def __init__(self):
        """Initialize SSML generator"""
        self.ssml_version = "1.1"
    
    def generate(self, tokens):
        """
        Generate SSML from normalized tokens
        
        Args:
            tokens: List of token dictionaries with 'original', 'normalized', 'category'
            
        Returns:
            SSML string
        """
        ssml_parts = []
        ssml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
        ssml_parts.append('<speak version="1.1" xmlns="http://www.w3.org/2001/10/synthesis"')
        ssml_parts.append('        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        ssml_parts.append('        xsi:schemaLocation="http://www.w3.org/2001/10/synthesis')
        ssml_parts.append('                            http://www.w3.org/TR/speech-synthesis11/synthesis.xsd"')
        ssml_parts.append('        xml:lang="hi-IN">')
        
        for token in tokens:
            category = token['category']
            normalized = token['normalized']
            original = token['original']
            
            if category == 'currency':
                # Currency with emphasis and slight pause
                ssml_parts.append(f'  <say-as interpret-as="currency" format="long">')
                ssml_parts.append(f'    <emphasis level="moderate">{normalized}</emphasis>')
                ssml_parts.append(f'  </say-as>')
                
            elif category == 'cardinal':
                # Cardinal number with clear pronunciation
                ssml_parts.append(f'  <say-as interpret-as="cardinal">')
                ssml_parts.append(f'    {normalized}')
                ssml_parts.append(f'  </say-as>')
                
            else:
                # Regular text
                ssml_parts.append(f'  {normalized}')
        
        ssml_parts.append('</speak>')
        
        return '\n'.join(ssml_parts)
    
    def generate_inline(self, tokens):
        """
        Generate inline SSML (without XML declaration)
        Useful for embedding in larger SSML documents
        
        Args:
            tokens: List of token dictionaries
            
        Returns:
            SSML string without XML declaration
        """
        parts = []
        
        for token in tokens:
            category = token['category']
            normalized = token['normalized']
            
            if category == 'currency':
                parts.append(f'<say-as interpret-as="currency">{normalized}</say-as>')
            elif category == 'cardinal':
                parts.append(f'<say-as interpret-as="cardinal">{normalized}</say-as>')
            else:
                parts.append(normalized)
        
        return ' '.join(parts)
