from __future__ import annotations
import string

class QuantityDFA:
    """Deterministic Finite Automaton for [Number] [Unit] patterns."""
    
    class _Node:
        __slots__ = ("children", "is_final")
        def __init__(self):
            self.children: dict[str, QuantityDFA._Node] = {}
            self.is_final = False

    def __init__(self) -> None:
        self._trap_node = self._Node()
        self._unit_root = self._Node() # The start state for the unit string

    def insert_unit(self, unit: str) -> None:
        """Builds the Trie structure for the accepted units."""
        node = self._unit_root
        for ch in unit:
            node = node.children.setdefault(ch, self._Node())
        node.is_final = True

    def accepts(self, text: str) -> bool:
        """Processes the string exactly ONE character at a time from left to right."""
        phase = 0
        current_node = self._unit_root

        for ch in text:
            if phase == 0:
                if ch.isdigit():
                    phase = 1
                else:
                    return False # Trap state reached
            
            elif phase == 1:
                if ch.isdigit():
                    continue # Loop in state 1
                elif ch == ' ':
                    phase = 2 # Transition to the unit logic
                else:
                    return False # Trap state reached
            
            elif phase == 2:
                # Traverse the dynamically built unit nodes
                if ch in string.punctuation:
                    continue # Ignore punctuation at the end of a unit
                    
                if ch in current_node.children:
                    current_node = current_node.children[ch]
                else:
                    return False # Trap state reached

        # Accept ONLY if we reached the end of the text AND the unit node is a final state
        return phase == 2 and current_node.is_final