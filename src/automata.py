from typing import List, Tuple, Dict, Set

def load_automata(filename: str) -> Tuple[List[str], List[str], List[Tuple[str, str, str]], str, List[str]]:
    """
    Lê os dados de um autômato finito a partir de um arquivo.

    A estsrutura do arquivo deve ser:

    <lista de símbolos do alfabeto, separados por espaço (' ')>
    <lista de nomes de estados>
    <lista de nomes de estados finais>
    <nome do estado inicial>
    <lista de regras de transição, com "origem símbolo destino">

    Um exemplo de arquivo válido é:

    ```
    a b
    q0 q1 q2 q3
    q0 q3
    q0
    q0 a q1
    q0 b q2
    q1 a q0
    q1 b q3
    q2 a q3
    q2 b q0
    q3 a q1
    q3 b q2
    ```

    Caso o arquivo seja inválido uma exceção Exception é gerada.

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
    Processa a lista de palavras e retora o resultado.

    Os resultados válidos são ACEITA, REJEITA, INVALIDA.
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
    """Converte um NFA num DFA."""
    states, alphabet, delta, initial_state, final_states = automaton

    def handle_closure(state: str, delta: List[Tuple[str, str, str]]) -> Set[str]:
        """Retorna o fecho de um estado em um NFA."""
        closure = {state}
        stack = [state]

        while stack:
            current = stack.pop()
            for (origin, sym, dest) in delta:
                if origin == current and sym == '&' and dest not in closure:
                    closure.add(dest)
                    stack.append(dest)

        return closure

    def find_transitions(states: Set[str], symbol: str) -> Set[str]:
        """Encontra o conjunto de estados alcançáveis a partir de um conjunto de estados e um símbolo."""
        result = set()
        for state in states:
            for (origin, sym, dest) in delta:
                if origin == state and sym == symbol:
                    result.add(dest)
        return result

    def epsilon_closure(states: Set[str]) -> Set[str]:
        """Retorna o fecho epsilon de um conjunto de estados."""
        epsilon_closure_set = set(states)
        stack = list(states)

        while stack:
            current_state = stack.pop()
            for (origin, sym, dest) in delta:
                if origin == current_state and sym == '&':
                    if dest not in epsilon_closure_set:
                        epsilon_closure_set.add(dest)
                        stack.append(dest)

        return epsilon_closure_set

    def state_to_str(state_set: Set[str]) -> str:
        """Converte um conjunto de estados em uma string ordenada."""
        return ','.join(sorted(state_set))

    new_states = []
    new_delta = []
    new_final_states = []
    new_initial_state = epsilon_closure({initial_state})

    queue = [new_initial_state]
    visited = []

    while queue:
        current_states = queue.pop()
        visited.append(current_states)

        for symbol in alphabet:
            next_states = epsilon_closure(find_transitions(current_states, symbol))
            if next_states:
                new_delta.append((state_to_str(current_states), symbol, state_to_str(next_states)))
                if next_states not in visited:
                    visited.append(next_states)
                    queue.append(next_states)

    for state_set in visited:
        if any(state in final_states for state in state_set):
            new_final_states.append(state_to_str(state_set))

    new_states = [state_to_str(state_set) for state_set in visited]

    return new_states, alphabet, new_delta, state_to_str(new_initial_state), new_final_states