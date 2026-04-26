import re
from typing import List, Tuple
from dfa import QuantityDFA
from units import ACCEPTED_UNITS

def build_dfa() -> QuantityDFA:
    """Builds the DFA tree for the accepted units."""
    dfa = QuantityDFA()
    for unit in ACCEPTED_UNITS:
        dfa.insert_unit(unit) 
    return dfa

def scan_paragraph(
    paragraph: str, dfa: QuantityDFA
) -> tuple[List[Tuple[str, bool]], str]:
    
    verdicts: list[tuple[str, bool]] = []
    found_patterns = []
    
    # Machine Variables
    phase = 0 
    current_node = dfa._unit_root
    start_index = -1
    
    i = 0
    while i < len(paragraph):
        char = paragraph[i]
        
        # --- NUMBER PROCESSING LOGIC ---
        if phase == 0:
            if char.isdigit():
                phase = 1
                start_index = i
                
        elif phase == 1: # Reading whole numbers
            if char.isdigit() or char == ',': 
                pass
            elif char == '.':
                phase = 3 
            elif char == '/':
                phase = 5 
            elif char == ' ':
                phase = 2 
                current_node = dfa._unit_root
            else:
                phase = 0 
                
        elif phase == 3: # Saw a decimal point
            if char.isdigit():
                phase = 4
            else:
                phase = 0 
                start_index = -1
                
        elif phase == 4: # Reading decimal digits
            if char.isdigit():
                pass
            elif char == ' ':
                phase = 2
                current_node = dfa._unit_root
            else:
                phase = 0
                start_index = -1
                
        elif phase == 5: # Saw a fraction slash
            if char.isdigit():
                phase = 6
            else:
                phase = 0 
                start_index = -1
                
        elif phase == 6: # Reading fraction denominator
            if char.isdigit():
                pass
            elif char == ' ':
                phase = 2
                current_node = dfa._unit_root
            else:
                phase = 0
                start_index = -1

        # --- UNIT PROCESSING LOGIC ---        
        elif phase == 2:
            if char in current_node.children:
                current_node = current_node.children[char]
                
                if current_node.is_final:
                    next_char = paragraph[i+1] if i + 1 < len(paragraph) else ' '
                    if not next_char.isalpha():
                        word = paragraph[start_index:i+1]
                        found_patterns.append({"word": word, "start": start_index, "end": i+1})
                        verdicts.append((word, True))
                        
                        phase = 0
                        start_index = -1
            else:
                phase = 0
                start_index = -1
                if char.isdigit():
                    phase = 1
                    start_index = i
        
        i += 1

    # Add all single words to verdicts as "Rejected" for the UI Dataframe
    clean_words = paragraph.replace("\n", " ").split(" ")
    for word in clean_words:
        clean_word = word.strip(".,!?()[]{}")
        if clean_word and clean_word not in [p["word"] for p in found_patterns]:
            verdicts.append((clean_word, False))

    # Build the highlighted text
    bold_para = paragraph
    offset = 0
    span_start = '<span style="background-color: rgba(99,102,241,0.18); color: #a5b4fc; font-weight: 600; border-radius: 6px; padding: 2px 8px; border: 1px solid rgba(99,102,241,0.25);">'
    span_end = '</span>'
    
    for p in found_patterns:
        start = p["start"] + offset
        end = p["end"] + offset
        bold_para = bold_para[:start] + span_start + bold_para[start:end] + span_end + bold_para[end:]
        offset += len(span_start) + len(span_end)
        
    return verdicts, bold_para