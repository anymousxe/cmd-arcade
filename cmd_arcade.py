from __future__ import annotations

import os
import random
import string
from collections import deque
from functools import lru_cache


# ======================
# Shared utilities
# ======================

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def press_enter(msg: str = "Press Enter to continue...") -> None:
    safe_input(msg)


def prompt_int(prompt: str, *, min_value: int | None = None, max_value: int | None = None) -> int:
    while True:
        raw = safe_input(prompt).strip()
        try:
            val = int(raw)
        except ValueError:
            print("Please enter a valid integer.")
            continue

        if min_value is not None and val < min_value:
            print(f"Please enter a number >= {min_value}.")
            continue
        if max_value is not None and val > max_value:
            print(f"Please enter a number <= {max_value}.")
            continue
        return val


def prompt_choice(prompt: str, choices: list[str]) -> str:
    lowered = {c.lower(): c for c in choices}
    while True:
        raw = safe_input(prompt).strip().lower()
        if raw in lowered:
            return lowered[raw]
        print(f"Choose one of: {', '.join(choices)}")


# ======================
# Game 1: Guess the Number
# ======================

def game_guess_number() -> None:
    print("Guess the Number")
    print("-" * 40)

    mode = prompt_choice("Difficulty (easy/normal/hard): ", ["easy", "normal", "hard"])
    if mode == "easy":
        lo, hi, max_tries = 1, 50, 10
    elif mode == "normal":
        lo, hi, max_tries = 1, 100, 8
    else:
        lo, hi, max_tries = 1, 500, 9

    secret = random.randint(lo, hi)
    tries = 0

    print(f"I'm thinking of a number between {lo} and {hi}.")
    print(f"You have {max_tries} tries.")

    while tries < max_tries:
        guess = prompt_int(f"Guess #{tries + 1}: ", min_value=lo, max_value=hi)
        tries += 1

        if guess == secret:
            print(f"Correct. You got it in {tries} tries.")
            return
        print("Too low." if guess < secret else "Too high.")

    print(f"Out of tries. The number was {secret}.")


# ======================
# Game 2: Rock Paper Scissors
# ======================

def game_rps() -> None:
    print("Rock Paper Scissors")
    print("-" * 40)

    rounds = prompt_int("Best of how many rounds? (odd number like 3/5/7): ", min_value=1)
    if rounds % 2 == 0:
        rounds += 1
        print(f"Using {rounds} (must be odd).")

    needed = rounds // 2 + 1
    user_score = 0
    cpu_score = 0
    options = ["rock", "paper", "scissors"]

    def winner(u: str, c: str) -> int:
        if u == c:
            return 0
        if (u, c) in {("rock", "scissors"), ("paper", "rock"), ("scissors", "paper")}:
            return 1
        return -1

    while user_score < needed and cpu_score < needed:
        print(f"\nScore: You {user_score} - CPU {cpu_score} (first to {needed})")
        u = prompt_choice("Choose rock/paper/scissors: ", options)
        c = random.choice(options)
        print(f"CPU chose: {c}")

        w = winner(u, c)
        if w == 1:
            user_score += 1
            print("You win this round.")
        elif w == -1:
            cpu_score += 1
            print("CPU wins this round.")
        else:
            print("Tie.")

    print("\nFinal:", f"You {user_score} - CPU {cpu_score}")
    print("You win!" if user_score > cpu_score else "CPU wins!")


# ======================
# Game 3: Hangman
# ======================

HANGMAN_WORDS = [
    "python", "terminal", "github", "variable", "function", "iteration",
    "compiler", "debugging", "algorithm", "minimax", "protocol", "database",
]


def game_hangman() -> None:
    print("Hangman")
    print("-" * 40)

    word = random.choice(HANGMAN_WORDS).lower()
    guessed: set[str] = set()
    wrong: set[str] = set()
    lives = 6

    def display() -> str:
        return " ".join(c if c in guessed else "_" for c in word)

    while lives > 0:
        print("\nWord:", display())
        print(f"Wrong: {' '.join(sorted(wrong)) if wrong else '(none)'}")
        print(f"Lives: {lives}")

        if all(c in guessed for c in word):
            print("You guessed it!")
            return

        raw = safe_input("Guess a letter (or type 'word' to guess the whole thing): ").strip().lower()
        if not raw:
            continue

        if raw == "word":
            attempt = safe_input("Your word guess: ").strip().lower()
            if attempt == word:
                print("Correct! You win.")
                return
            lives -= 1
            print("Nope.")
            continue

        if len(raw) != 1 or raw not in string.ascii_lowercase:
            print("Please guess a single letter a-z.")
            continue

        ch = raw
        if ch in guessed or ch in wrong:
            print("Already tried that.")
            continue

        if ch in word:
            guessed.add(ch)
            print("Good guess.")
        else:
            wrong.add(ch)
            lives -= 1
            print("Wrong.")

    print(f"You lost. The word was: {word}")


# ======================
# Game 4: Tic-Tac-Toe (minimax)
# ======================

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def game_tic_tac_toe() -> None:
    print("Tic-Tac-Toe (You = X, AI = O)")
    print("-" * 40)

    board = [" "] * 9
    human = "X"
    ai = "O"

    def show() -> None:
        def cell(i: int) -> str:
            return board[i] if board[i] != " " else str(i + 1)
        print()
        print(f" {cell(0)} | {cell(1)} | {cell(2)} ")
        print("---+---+---")
        print(f" {cell(3)} | {cell(4)} | {cell(5)} ")
        print("---+---+---")
        print(f" {cell(6)} | {cell(7)} | {cell(8)} ")
        print()

    def winner(b: tuple[str, ...]) -> str | None:
        for a, c, d in WIN_LINES:
            if b[a] != " " and b[a] == b[c] == b[d]:
                return b[a]
        if " " not in b:
            return "draw"
        return None

    @lru_cache(maxsize=None)
    def minimax(b: tuple[str, ...], turn: str) -> int:
        w = winner(b)
        if w == ai:
            return 1
        if w == human:
            return -1
        if w == "draw":
            return 0

        moves = [i for i, v in enumerate(b) if v == " "]
        if turn == ai:
            best = -10
            for i in moves:
                bb = list(b)
                bb[i] = ai
                best = max(best, minimax(tuple(bb), human))
            return best
        else:
            best = 10
            for i in moves:
                bb = list(b)
                bb[i] = human
                best = min(best, minimax(tuple(bb), ai))
            return best

    def best_ai_move() -> int:
        b = tuple(board)
        moves = [i for i, v in enumerate(board) if v == " "]
        best_score = -10
        best_move = moves[0]
        for i in moves:
            bb = list(b)
            bb[i] = ai
            score = minimax(tuple(bb), human)
            if score > best_score:
                best_score = score
                best_move = i
        return best_move

    while True:
        show()
        w = winner(tuple(board))
        if w is not None:
            if w == "draw":
                print("It's a draw.")
            else:
                print(f"{w} wins!")
            return

        # human move
        while True:
            pos = prompt_int("Pick a square (1-9): ", min_value=1, max_value=9) - 1
            if board[pos] == " ":
                board[pos] = human
                break
            print("That square is taken.")

        w = winner(tuple(board))
        if w is not None:
            show()
            if w == "draw":
                print("It's a draw.")
            else:
                print(f"{w} wins!")
            return

        # ai move
        move = best_ai_move()
        board[move] = ai
        print(f"AI plays: {move + 1}")


# ======================
# Game 5: Blackjack
# ======================

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♠", "♥", "♦", "♣"]


def card_value(rank: str) -> int:
    if rank in {"J", "Q", "K"}:
        return 10
    if rank == "A":
        return 11
    return int(rank)


def hand_value(hand: list[tuple[str, str]]) -> int:
    total = sum(card_value(r) for r, _ in hand)
    aces = sum(1 for r, _ in hand if r == "A")
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total


def game_blackjack() -> None:
    print("Blackjack")
    print("-" * 40)

    deck = [(r, s) for r in RANKS for s in SUITS]
    random.shuffle(deck)

    def draw() -> tuple[str, str]:
        return deck.pop()

    player = [draw(), draw()]
    dealer = [draw(), draw()]

    while True:
        p_val = hand_value(player)
        print("\nDealer shows:", f"{dealer[0][0]}{dealer[0][1]}", "(hidden)")
        print("Your hand:", " ".join(f"{r}{s}" for r, s in player), f"= {p_val}")

        if p_val > 21:
            print("Bust. You lose.")
            return
        if p_val == 21:
            print("21! Dealer's turn...")
            break

        move = prompt_choice("Hit or stand? ", ["hit", "stand"])
        if move == "hit":
            player.append(draw())
        else:
            break

    print("\nDealer reveals:", " ".join(f"{r}{s}" for r, s in dealer), f"= {hand_value(dealer)}")
    while hand_value(dealer) < 17:
        dealer.append(draw())
        print("Dealer hits:", f"{dealer[-1][0]}{dealer[-1][1]}", f"(total {hand_value(dealer)})")

    p_val = hand_value(player)
    d_val = hand_value(dealer)

    if d_val > 21:
        print("Dealer busts. You win.")
    elif p_val > d_val:
        print("You win.")
    elif p_val < d_val:
        print("You lose.")
    else:
        print("Push (tie).")


# ======================
# Game 6: Word Scramble
# ======================

SCRAMBLE_WORDS = [
    "repository", "terminal", "interface", "encryption", "recursion",
    "framework", "optimization", "dependency", "exception", "iteration",
]


def scramble(word: str) -> str:
    chars = list(word)
    while True:
        random.shuffle(chars)
        s = "".join(chars)
        if s != word:
            return s


def game_word_scramble() -> None:
    print("Word Scramble")
    print("-" * 40)

    word = random.choice(SCRAMBLE_WORDS)
    mixed = scramble(word)

    print("Unscramble this word:")
    print(" ", mixed)

    max_tries = 5
    for i in range(max_tries):
        guess = safe_input(f"Guess ({max_tries - i} left), or 'hint': ").strip().lower()
        if not guess:
            continue
        if guess == "hint":
            reveal = prompt_int("Reveal how many starting letters? (1-5): ",
                                min_value=1, max_value=min(5, len(word)))
            print("Hint:", word[:reveal] + "_" * (len(word) - reveal))
            continue
        if guess == word:
            print("Correct!")
            return
        print("Nope.")

    print(f"Out of tries. The word was: {word}")


# ======================
# Game 7: Minesweeper
# ======================

def game_minesweeper() -> None:
    print("Minesweeper (small grid)")
    print("-" * 40)

    size = prompt_choice("Board size (small/medium): ", ["small", "medium"])
    if size == "small":
        h, w, mines = 6, 8, 8
    else:
        h, w, mines = 8, 10, 14

    all_cells = [(r, c) for r in range(h) for c in range(w)]
    mine_set = set(random.sample(all_cells, mines))
    revealed: set[tuple[int, int]] = set()
    flagged: set[tuple[int, int]] = set()

    def in_bounds(r: int, c: int) -> bool:
        return 0 <= r < h and 0 <= c < w

    def neighbors(r: int, c: int):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr, cc = r + dr, c + dc
                if in_bounds(rr, cc):
                    yield (rr, cc)

    def adj_mines(r: int, c: int) -> int:
        return sum((nr, nc) in mine_set for nr, nc in neighbors(r, c))

    def flood_reveal(start: tuple[int, int]) -> None:
        q = deque([start])
        while q:
            r, c = q.popleft()
            if (r, c) in revealed or (r, c) in flagged:
                continue
            revealed.add((r, c))
            if (r, c) in mine_set:
                continue
            if adj_mines(r, c) == 0:
                for nb in neighbors(r, c):
                    if nb not in revealed and nb not in flagged:
                        q.append(nb)

    def draw_board(show_mines: bool = False) -> None:
        header = "    " + " ".join(f"{i+1:2d}" for i in range(w))
        print(header)
        print("   +" + "---" * w + "+")
        for r in range(h):
            row_label = chr(ord("A") + r)
            line = []
            for c in range(w):
                pos = (r, c)
                if pos in flagged:
                    ch = "F"
                elif pos in revealed:
                    if pos in mine_set:
                        ch = "*"
                    else:
                        n = adj_mines(r, c)
                        ch = str(n) if n > 0 else " "
                else:
                    ch = "*" if show_mines and pos in mine_set else "·"
                line.append(f" {ch}")
            print(f" {row_label} |" + "".join(line) + " |")
        print("   +" + "---" * w + "+")
        print(f"Revealed: {len(revealed)} / {h*w - mines}   Flags: {len(flagged)} / {mines}")

    def parse_cell(cell: str) -> tuple[int, int] | None:
        cell = cell.strip().upper()
        if len(cell) < 2:
            return None
        row_char = cell[0]
        if not ("A" <= row_char <= chr(ord("A") + h - 1)):
            return None
        try:
            col = int(cell[1:]) - 1
        except ValueError:
            return None
        row = ord(row_char) - ord("A")
        if not (0 <= col < w):
            return None
        return (row, col)

    while True:
        print()
        draw_board()

        action = prompt_choice("Action: reveal / flag / unflag / quit: ", ["reveal", "flag", "unflag", "quit"])
        if action == "quit":
            print("Quitting.")
            return

        raw = safe_input(f"Cell (e.g. A1..{chr(ord('A')+h-1)}{w}): ")
        pos = parse_cell(raw)
        if pos is None:
            print("Invalid cell.")
            continue

        if action == "flag":
            if pos not in revealed:
                flagged.add(pos)
            continue
        if action == "unflag":
            flagged.discard(pos)
            continue

        if pos in flagged:
            print("Cell is flagged. Unflag it first.")
            continue

        if pos in mine_set:
            revealed.add(pos)
            print("\nBoom. You hit a mine.")
            draw_board(show_mines=True)
            return

        flood_reveal(pos)

        if len(revealed) >= (h * w - mines):
            print("\nYou cleared the board!")
            draw_board(show_mines=True)
            return


# ======================
# Game 8: Quiz
# ======================

QUIZ_QUESTIONS = [
    ("What does CPU stand for?",
     {"a": "Central Processing Unit", "b": "Computer Primary Utility", "c": "Core Program Uplink", "d": "Control Processing User"},
     "a"),
    ("Which data structure uses FIFO?",
     {"a": "Stack", "b": "Queue", "c": "Tree", "d": "Heap"},
     "b"),
    ("What does 'git commit' primarily do?",
     {"a": "Uploads code to a server", "b": "Deletes untracked files", "c": "Records a snapshot in local history", "d": "Renames a branch"},
     "c"),
    ("In Big-O, which grows fastest?",
     {"a": "O(n)", "b": "O(log n)", "c": "O(n^2)", "d": "O(1)"},
     "c"),
    ("Which port is commonly used for HTTPS?",
     {"a": "21", "b": "22", "c": "80", "d": "443"},
     "d"),
]


def game_quiz() -> None:
    print("Quiz Bowl")
    print("-" * 40)

    score = 0
    for i, (q, choices, ans) in enumerate(QUIZ_QUESTIONS, start=1):
        print(f"\nQ{i}. {q}")
        for k in ["a", "b", "c", "d"]:
            print(f"  {k}) {choices[k]}")
        user = prompt_choice("Your answer (a/b/c/d): ", ["a", "b", "c", "d"]).lower()
        if user == ans:
            print("Correct.")
            score += 1
        else:
            print(f"Wrong. Correct was {ans}) {choices[ans]}")

    print(f"\nFinal score: {score} / {len(QUIZ_QUESTIONS)}")


# ======================
# Game 9: Bulls and Cows
# ======================

def game_bulls_and_cows() -> None:
    print("Bulls and Cows")
    print("-" * 40)
    print("I picked a 4-digit number with all unique digits.")
    print("Bulls = correct digit in correct position.")
    print("Cows  = correct digit in wrong position.")

    digits = random.sample("0123456789", 4)
    if digits[0] == "0":
        digits[0], digits[1] = digits[1], digits[0]
    secret = "".join(digits)

    tries = 0
    while True:
        guess = safe_input("Your guess (4 unique digits) or 'quit': ").strip()
        if not guess:
            continue
        if guess.lower() in {"q", "quit", "exit"}:
            print("Secret was:", secret)
            return

        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            print("Invalid guess. Example valid guess: 1234 (4 digits, no repeats).")
            continue
        if guess[0] == "0":
            print("No leading zero (e.g. 0123 not allowed).")
            continue

        tries += 1
        bulls = sum(guess[i] == secret[i] for i in range(4))
        cows = sum((ch in secret) for ch in guess) - bulls

        if bulls == 4:
            print(f"4 bulls. You win in {tries} guesses!")
            return
        print(f"{bulls} bulls, {cows} cows")


# ======================
# Main menu
# ======================

GAMES = [
    ("1", "Guess the Number", game_guess_number),
    ("2", "Rock Paper Scissors", game_rps),
    ("3", "Hangman", game_hangman),
    ("4", "Tic-Tac-Toe (minimax AI)", game_tic_tac_toe),
    ("5", "Blackjack", game_blackjack),
    ("6", "Word Scramble", game_word_scramble),
    ("7", "Minesweeper (small grid)", game_minesweeper),
    ("8", "Quiz Bowl", game_quiz),
    ("9", "Bulls and Cows", game_bulls_and_cows),
]


def main() -> None:
    while True:
        clear_screen()
        print("CMD Arcade")
        print("=" * 40)
        for key, name, _fn in GAMES:
            print(f"{key}. {name}")
        print("Q. Quit")
        print("=" * 40)

        choice = safe_input("Select a game: ").strip().lower()
        if choice in {"q", "quit", "exit"}:
            print("Bye.")
            return

        match = next((g for g in GAMES if g[0] == choice), None)
        if match is None:
            print("Invalid selection.")
            press_enter()
            continue

        clear_screen()
        try:
            match[2]()
        except KeyboardInterrupt:
            print("\n(Interrupted)")
        press_enter()


if __name__ == "__main__":
    main()
