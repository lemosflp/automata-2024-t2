from typing import List, Tuple, Dict, Set


def load_automata(filename: str) -> Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]]:
    """
    Carrega os dados de um autômato finito a partir de um arquivo.

    Estrutura do arquivo esperada:
    - Linha 1: Lista de símbolos do alfabeto separados por espaço.
    - Linha 2: Lista de nomes de estados.
    - Linha 3: Lista de nomes de estados finais.
    - Linha 4: Nome do estado inicial.
    - Linhas subsequentes: Regras de transição no formato "origem símbolo destino".

    Retorna uma tupla (Q, Sigma, delta, q0, F).
    """
    with open(filename, "rt", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines()]

        if len(lines) < 5:
            raise ValueError("Arquivo inválido: número insuficiente de linhas.")

        alphabet = lines[0].split()
        states = lines[1].split()
        final_states = lines[2].split()
        initial_state = lines[3]
        transitions = lines[4:]

        for state in final_states:
            if state not in states:
                raise ValueError("Estado final inválido.")

        delta = []
        for transition in transitions:
            parts = transition.split()
            if len(parts) != 3:
                raise ValueError(f"Transição inválida: {transition}")
            if parts[0] not in states or parts[2] not in states:
                raise ValueError(f"Estado na transição inválido: {transition}")
            if parts[1] != '&' and parts[1] not in alphabet:
                raise ValueError(f"Símbolo na transição inválido: {transition}")
            delta.append(tuple(parts))

        if initial_state not in states:
            raise ValueError("Estado inicial inválido.")

    return states, alphabet, delta, initial_state, final_states


def process(automaton: Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]], words: List[str]) -> \
Dict[str, str]:
    """
    Processa uma lista de palavras utilizando o autômato dado e retorna um dicionário associando cada palavra ao seu resultado (ACEITA, REJEITA, INVALIDA).
    """
    states, alphabet, delta, initial_state, final_states = automaton
    results = {}

    def is_valid_word(word: str) -> bool:
        return all(char in alphabet for char in word)

    def transition(state: str, symbol: str) -> str:
        for (origin, sym, dest) in delta:
            if origin == state and sym == symbol:
                return dest
        return None

    for word in words:
        if not is_valid_word(word):
            results[word] = "INVALIDA"
            continue

        current_state = initial_state
        for symbol in word:
            next_state = transition(current_state, symbol)
            if next_state:
                current_state = next_state
            else:
                break

        if current_state in final_states:
            results[word] = "ACEITA"
        else:
            results[word] = "REJEITA"

    return results


def handle_closure(state: str, delta: List[Tuple[str, str, str]]) -> Set[str]:
    """
    Retorna o fecho de um estado em um NFA.
    """
    closure = {state}
    stack = [state]

    while stack:
        current = stack.pop()
        for (origin, sym, dest) in delta:
            if origin == current and sym == '&' and dest not in closure:
                closure.add(dest)
                stack.append(dest)

    return closure


def convert_to_dfa(automaton: Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]]) -> Tuple[
    List[str], List[str], List[Tuple[str, str, str]], str, List[str]]:
    """
    Converte um NFA em um DFA.
    """
    states, alphabet, delta, initial_state, final_states = automaton

    new_states = []
    new_delta = []
    new_final_states = []
    new_initial_state = handle_closure(initial_state, delta)

    queue = [new_initial_state]
    visited = []

    while queue:
        current_states = queue.pop()
        visited.append(current_states)

        for symbol in alphabet:
            next_states = set()
            for state in current_states:
                for (origin, sym, dest) in delta:
                    if origin == state and sym == symbol:
                        next_states.update(handle_closure(dest, delta))
            if next_states:
                new_delta.append((current_states, symbol, frozenset(next_states)))
                if frozenset(next_states) not in visited:
                    visited.append(frozenset(next_states))
                    queue.append(frozenset(next_states))

    for state_set in visited:
        if any(state in final_states for state in state_set):
            new_final_states.append(state_set)

    new_states = [list(state_set) for state_set in visited]

    return new_states, alphabet, new_delta, frozenset(new_initial_state), new_final_states
