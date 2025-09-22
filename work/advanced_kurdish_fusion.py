#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Advanced Kurdish Character Fusion Engine
========================================
Sophisticated algorithm for combining Arabic and Persian model outputs
with character-level confidence scoring and Unicode-aware corrections
"""

import json
import re
import math
from typing import Dict, List, Tuple, Any

class AdvancedKurdishFusion:
    def __init__(self):
        """Initialize with Kurdish character mappings and strategies"""
        
        # Kurdish character groups based on Unicode analysis
        self.character_groups = {
            'persian_optimal': {
                'chars': ['ژ', 'گ', 'ۆ', 'ێ'],
                'reason': 'Better diacritic and vowel handling in Persian',
                'confidence_boost': 0.2
            },
            'arabic_optimal': {
                'chars': ['ڕ', 'ڵ'],
                'reason': 'Closer to Arabic base characters',
                'confidence_boost': 0.15
            },
            'hybrid_fusion': {
                'chars': ['ڤ', 'ە'],
                'reason': 'Requires special pattern-based fusion',
                'confidence_boost': 0.0
            }
        }
        
        # Unicode-based character relationships
        self.unicode_mappings = {
            'ڕ': {'base': 'ر', 'unicode': 'U+0695', 'persian_similar': ['ر'], 'arabic_similar': ['ر']},
            'ژ': {'base': 'ز', 'unicode': 'U+0698', 'persian_similar': ['ز', 'ژ'], 'arabic_similar': ['ز']},
            'ڤ': {'base': 'ف', 'unicode': 'U+06A4', 'persian_similar': ['ف'], 'arabic_similar': ['ف']},
            'گ': {'base': 'ك/ک', 'unicode': 'U+06AF', 'persian_similar': ['گ', 'ک'], 'arabic_similar': ['ك']},
            'ڵ': {'base': 'ل', 'unicode': 'U+06B5', 'persian_similar': ['ل'], 'arabic_similar': ['ل']},
            'ێ': {'base': 'ی', 'unicode': 'U+06CE', 'persian_similar': ['ی', 'ئ'], 'arabic_similar': ['ي', 'ئ']},
            'ۆ': {'base': 'و', 'unicode': 'U+06C6', 'persian_similar': ['و', 'ؤ'], 'arabic_similar': ['و']},
            'ە': {'base': 'ه', 'unicode': 'U+06D5', 'persian_similar': ['ه'], 'arabic_similar': ['ه']}
        }
        
        # Pattern-based error detection
        self.error_patterns = {
            'arabic_errors': ['رر', 'زر', 'ول', 'ال'],
            'persian_errors': ['رره‌', 'فی', 'وو', 'وه'],
            'common_mistakes': ['كو', 'رو', 'فا']
        }
    
    def calculate_model_confidence(self, text: str, model: str) -> float:
        """Calculate confidence score for a model's output"""
        
        base_confidence = 0.5
        
        # Count Kurdish characters (positive indicator)
        kurdish_chars = list(self.unicode_mappings.keys())
        kurdish_count = sum(text.count(char) for char in kurdish_chars)
        kurdish_bonus = min(kurdish_count * 0.08, 0.3)
        
        # Count error patterns (negative indicator)
        all_errors = []
        for error_list in self.error_patterns.values():
            all_errors.extend(error_list)
        
        error_count = sum(text.count(pattern) for pattern in all_errors)
        error_penalty = min(error_count * 0.12, 0.4)
        
        # Model-specific adjustments
        model_adjustments = {
            'persian': 0.1,   # Generally better for Kurdish
            'arabic': -0.05,  # Sometimes struggles with Kurdish
            'kurdish': 0.0    # Reference model
        }
        
        model_bonus = model_adjustments.get(model, 0.0)
        
        # Text length normalization
        length_factor = 1.0 if len(text) > 5 else 0.8
        
        final_confidence = (base_confidence + kurdish_bonus - error_penalty + model_bonus) * length_factor
        return max(0.1, min(0.95, final_confidence))
    
    def calculate_character_confidence(self, text: str, char: str, model: str) -> float:
        """Calculate confidence for specific character recognition"""
        
        # Base confidence based on character presence
        base_confidence = 0.8 if char in text else 0.1
        
        # Get character group information
        char_group = None
        group_bonus = 0.0
        
        for group_name, group_info in self.character_groups.items():
            if char in group_info['chars']:
                char_group = group_name
                # Apply model-specific bonus
                if (group_name == 'persian_optimal' and model == 'persian') or \
                   (group_name == 'arabic_optimal' and model == 'arabic'):
                    group_bonus = group_info['confidence_boost']
                break
        
        # Unicode similarity bonus
        unicode_info = self.unicode_mappings.get(char, {})
        similar_chars = unicode_info.get(f'{model}_similar', [])
        similarity_bonus = 0.1 if any(sim_char in text for sim_char in similar_chars) else 0.0
        
        # Context bonus (surrounding Kurdish characters)
        context_bonus = 0.0
        if char in text:
            for other_char in self.unicode_mappings.keys():
                if other_char != char and other_char in text:
                    context_bonus += 0.05
        context_bonus = min(context_bonus, 0.2)
        
        final_confidence = base_confidence + group_bonus + similarity_bonus + context_bonus
        return max(0.1, min(0.95, final_confidence))
    
    def apply_character_fusion(self, persian_text: str, arabic_text: str, kurdish_text: str) -> Tuple[str, Dict[str, Any]]:
        """Apply character-level fusion with confidence scoring"""
        
        # Calculate overall model confidences
        model_confidences = {
            'persian': self.calculate_model_confidence(persian_text, 'persian'),
            'arabic': self.calculate_model_confidence(arabic_text, 'arabic'),
            'kurdish': self.calculate_model_confidence(kurdish_text, 'kurdish')
        }
        
        # Start with the highest confidence model
        best_base_model = max(model_confidences, key=model_confidences.get)
        
        if best_base_model == 'persian':
            result_text = persian_text
        elif best_base_model == 'arabic':
            result_text = arabic_text
        else:
            result_text = persian_text  # Default to Persian if Kurdish wins
        
        # Character-level fusion decisions
        fusion_decisions = {}
        
        for char in self.unicode_mappings.keys():
            char_confidences = {
                'persian': self.calculate_character_confidence(persian_text, char, 'persian'),
                'arabic': self.calculate_character_confidence(arabic_text, char, 'arabic'),
                'kurdish': self.calculate_character_confidence(kurdish_text, char, 'kurdish')
            }
            
            best_char_model = max(char_confidences, key=char_confidences.get)
            confidence_diff = char_confidences[best_char_model] - char_confidences[best_base_model]
            
            fusion_decisions[char] = {
                'confidences': char_confidences,
                'best_model': best_char_model,
                'confidence_diff': confidence_diff,
                'action': 'switch' if confidence_diff > 0.15 else 'keep_base'
            }
        
        # Apply Unicode-aware corrections
        result_text = self.apply_unicode_corrections(result_text, persian_text, arabic_text, fusion_decisions)
        
        return result_text, {
            'model_confidences': model_confidences,
            'base_model': best_base_model,
            'character_decisions': fusion_decisions
        }
    
    def apply_unicode_corrections(self, text: str, persian_text: str, arabic_text: str, decisions: Dict) -> str:
        """Apply Unicode-aware pattern corrections"""
        
        # Character-specific correction patterns
        corrections = {
            # ڕ (U+0695) corrections
            'ڕ': [
                ('رر', 'ڕ'),
                ('رره‌?', 'ڕە'),
                ('زر', 'ڕ'),
                (r'\bرز\b', 'ڕ'),
            ],
            
            # ژ (U+0698) corrections  
            'ژ': [
                ('زی', 'ژی'),
                ('زا', 'ژا'),
                ('زایان', 'ژیان'),
                (r'ز(?=[یاو])', 'ژ'),
            ],
            
            # ڤ (U+06A4) corrections
            'ڤ': [
                ('فی', 'ڤی'),
                ('فا', 'ڤا'),
                ('فو', 'ڤو'),
                ('فیدیو', 'ڤیدیۆ'),
                (r'ف(?=[یاوە])', 'ڤ'),
            ],
            
            # گ (U+06AF) corrections - usually good in Persian
            'گ': [
                ('كو', 'گو'),
                ('كر', 'گر'),
            ],
            
            # ڵ (U+06B5) corrections
            'ڵ': [
                ('ول', 'وڵ'),
                ('گول', 'گوڵ'),
                ('ال', 'اڵ'),
            ],
            
            # ێ (U+06CE) corrections
            'ێ': [
                ('وه', 'ێوە'),
                ('یه', 'ێ'),
                ('ئێ', 'ێ'),
            ],
            
            # ۆ (U+06C6) corrections
            'ۆ': [
                ('وو', 'ۆ'),
                ('و ', 'ۆ '),
                ('وز', 'ۆز'),
                ('بو', 'بۆ'),
                (r'و(?=\s|$)', 'ۆ'),
            ],
            
            # ە (U+06D5) corrections
            'ە': [
                ('ه ', 'ە '),
                ('نك', 'نگ'),
                (' نگ', ' ەنگ'),
            ],
        }
        
        # Apply corrections based on character confidence
        for char, patterns in corrections.items():
            char_decision = decisions.get(char, {})
            if char_decision.get('action') == 'switch' or char in text:
                for pattern, replacement in patterns:
                    if isinstance(pattern, str):
                        text = text.replace(pattern, replacement)
                    else:  # regex pattern
                        text = re.sub(pattern, replacement, text)
        
        return text
    
    def generate_detailed_report(self, analysis: Dict[str, Any]) -> str:
        """Generate detailed fusion analysis report"""
        
        report = []
        report.append("Advanced Kurdish Character Fusion Report")
        report.append("=" * 45)
        
        # Model confidence scores
    report.append("\nModel Confidence Scores:")
        model_conf = analysis['model_confidences']
        for model, conf in model_conf.items():
            report.append(f"  {model.capitalize():8}: {conf:.3f}")
        
    report.append(f"\nBase Model Selected: {analysis['base_model'].upper()}")
        
        # Character-level decisions
    report.append("\nCharacter-Level Fusion Decisions:")
        char_decisions = analysis['character_decisions']
        
        for char, decision in char_decisions.items():
            best_model = decision['best_model']
            conf_diff = decision['confidence_diff']
            action = decision['action']
            
            conf_str = " ".join(f"{model[0].upper()}:{conf:.2f}" 
                               for model, conf in decision['confidences'].items())
            
            status = "🔄" if action == 'switch' else "✓"
            report.append(f"  {char} {status} {best_model.upper():7} ({conf_str}) Δ{conf_diff:+.2f}")
        
    return "\n".join(report)

if __name__ == "__main__":
    fusion_engine = AdvancedKurdishFusion()
    
    # Example usage
    print("Advanced Kurdish Character Fusion Engine")
    print("========================================")
    print("Ready for hybrid OCR processing!")
    print()
    print("Character Groups:")
    for group, info in fusion_engine.character_groups.items():
        chars = " ".join(info['chars'])
        print(f"  {group:15}: {chars} | {info['reason']}")