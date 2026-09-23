#!/usr/bin/env python3
"""
chess_bot.py — PC-side main script
====================================
Watches server_camera/public/ for new .jpg files (dropped by server.js).
On each new image:
  1. Detects the player's move via computer vision (bege_en_rouge + presence_rouge)
  2. Validates and pushes the move to the chess board
  3. Asks Stockfish for the best reply
  4. Writes the reply to a local file (mvm.txt) that the HTTP server serves
  5. The EV3 polls http://<PC_IP>:80 and reads that file to know what to do

PC ↔ EV3 communication:
  - PC runs a plain Python http.server on port 80 (or 8000)
  - Server serves mvm.txt as plain text: "take E2E4" or "kill E2E4"
  - EV3 polls the URL every second with urllib (built-in, no pip needed)
  - After the EV3 reads the move, it acts on it; PC writes "NOOP" to block repeats
"""

import cv2
import chess
import chess.engine
import time
import os
import threading
import numpy as np
from http.server import HTTPServer, BaseHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ─── Config ──────────────────────────────────────────────────────────────────

STOCKFISH_PATH  = r"stockfish-windows-x86-64-avx2.exe"   # on PATH or same dir
INITIAL_IMAGE   = os.path.join(os.path.dirname(__file__), "..", "assets", "111.png")
WATCH_DIR       = os.path.join(os.path.dirname(__file__), "..", "server_camera", "public")
STOCKFISH_DEPTH = 10

# PC creates a WiFi hotspot; EV3 connects to it.
# PC hosts a plain HTTP server on this port; EV3 polls it with urllib.
HTTP_HOST = "0.0.0.0"
HTTP_PORT = 80          # use 8000 if 80 requires admin rights on Windows

# File that the HTTP server reads to know what to serve
MVM_FILE = os.path.join(os.path.dirname(__file__), "mvm.txt")

# ─── HTTP server (serves mvm.txt to the EV3) ─────────────────────────────────

def write_mvm(content: str):
    """Write move command to mvm.txt. EV3 polls and reads this."""
    with open(MVM_FILE, "w") as f:
        f.write(content)

class MvmHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            with open(MVM_FILE, "r") as f:
                body = f.read().strip()
        except FileNotFoundError:
            body = "NOOP"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        pass  # suppress per-request console spam

def start_http_server():
    server = HTTPServer((HTTP_HOST, HTTP_PORT), MvmHandler)
    print(f"HTTP server running on http://{HTTP_HOST}:{HTTP_PORT}  (EV3 polls this)")
    server.serve_forever()

# ─── Vision ──────────────────────────────────────────────────────────────────

def bege_en_rouge(image_path):
    image = cv2.imread(image_path)
    image = image[1480:1480+1230, 870:870+1250]
    couleur_source   = np.array([72, 155, 194])
    nouvelle_couleur = np.array([0, 0, 255])
    tolerance = 50
    masque = np.all(np.abs(image - couleur_source) < tolerance, axis=-1)
    image[masque] = nouvelle_couleur
    return image

def presence_rouge(square):
    couleur_a_detecter = np.array([0, 0, 255])
    tolerance = 10
    masque = cv2.inRange(
        square,
        couleur_a_detecter - tolerance,
        couleur_a_detecter + tolerance,
    )
    return np.sum(masque > 0) > 3000

def chessboard_to_table(image_path, pos_label_tochange=None, value_tochange=None):
    """
    Label convention (from codelowl.py — confirmed final source):
      letter = chr(ord('h') - row)   → row 0 = 'h', row 7 = 'a'
      number = 8 - col               → col 0 = 8,   col 7 = 1
    Produces lowercase labels: 'h8', 'a1', 'e2', etc.
    """
    image = bege_en_rouge(image_path)
    sq_h  = image.shape[0] // 8
    sq_w  = image.shape[1] // 8
    result = {}
    for row in range(8):
        for col in range(8):
            x1, y1 = col * sq_w,  row * sq_h
            sq     = image[y1:y1+sq_h, x1:x1+sq_w]
            label  = f"{chr(ord('h') - row)}{8 - col}"
            result[label] = presence_rouge(sq)
    if pos_label_tochange in result and isinstance(value_tochange, bool):
        result[pos_label_tochange] = value_tochange
    return result

def get_mvmnt(image1, image2):
    """
    Returns UCI move string e.g. 'e2e4', or None.

    Capture handling (stk):
      If Stockfish's last move was a capture, stk[0] holds its UCI string.
      We patch that destination square to False in chesstable1 so the
      'phantom disappearing piece' doesn't confuse the diff.

    Castling (white only, hardcoded from codelowl.py):
      Kingside:  {h1,e1} → {g1,f1}  →  'e1g1'
      Queenside: {e1,a1} → {d1,c1}  →  'e1c1'

    KNOWN LIMITATION: en passant (3 squares) returns None. Black castling not detected.
    """
    global stk
    t1 = chessboard_to_table(image1)
    t2 = chessboard_to_table(image2)

    if stk:
        cap = stk.pop(0)
        dest_sq = f"{cap[2]}{cap[3]}"
        t1 = chessboard_to_table(image1, dest_sq, False)

    full_to_empty = [sq for sq, val in t1.items() if val     and not t2[sq]]
    empty_to_full = [sq for sq, val in t1.items() if not val and t2[sq]]

    if set(full_to_empty) == {"h1", "e1"} and set(empty_to_full) == {"g1", "f1"}:
        return "e1g1"
    if set(full_to_empty) == {"e1", "a1"} and set(empty_to_full) == {"d1", "c1"}:
        return "e1c1"

    if len(full_to_empty) == 1 and len(empty_to_full) == 1:
        return f"{full_to_empty[0]}{empty_to_full[0]}"

    print(f"  get_mvmnt: unresolved — {full_to_empty=} {empty_to_full=}")
    return None

# ─── Watchdog handler ────────────────────────────────────────────────────────

class ChessboardHandler(FileSystemEventHandler):

    def __init__(self, engine, initial_image_path):
        self.engine = engine
        self.initial_image_path = os.path.abspath(initial_image_path)
        self.board = chess.Board()
        self.move_count = 1

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(".jpg"):
            return
        self.process_image(event.src_path)

    def process_image(self, current_image_path):
        current_image_path = os.path.abspath(current_image_path)
        user_move_uci = get_mvmnt(self.initial_image_path, current_image_path)

        if user_move_uci is None:
            time.sleep(2)
            return

        print(f"\nmove {self.move_count}")
        self.move_count += 1

        try:
            self.board.push_uci(user_move_uci)
        except Exception as e:
            print(f"  Invalid move '{user_move_uci}': {e}")
            return

        print(f"  You played:       {user_move_uci}")

        result = self.engine.play(
            self.board,
            chess.engine.Limit(time=2.0, depth=STOCKFISH_DEPTH),
        )
        stockfish_move = result.move
        stockfish_uci  = stockfish_move.uci()      # e.g. 'e7e5'
        stockfish_ev3  = stockfish_uci.upper()     # e.g. 'E7E5' for EV3 dict keys

        print(f"  Stockfish played: {stockfish_uci}")

        # Detect capture BEFORE pushing (captured piece still on board)
        if self.board.is_capture(stockfish_move):
            stk.append(stockfish_uci)
            command = f"kill {stockfish_ev3}"
        else:
            command = f"take {stockfish_ev3}"

        # Write move to file; EV3 will GET it and act
        write_mvm(command)
        print(f"  → mvm.txt: {command}")

        self.board.push(stockfish_move)
        self.initial_image_path = current_image_path

        # After a delay, reset to NOOP so EV3 doesn't replay the move
        def reset_mvm():
            time.sleep(10)
            write_mvm("NOOP")
        threading.Thread(target=reset_mvm, daemon=True).start()

# ─── Main ────────────────────────────────────────────────────────────────────

stk = []

def main():
    watch_dir     = os.path.abspath(WATCH_DIR)
    initial_image = os.path.abspath(INITIAL_IMAGE)

    os.makedirs(watch_dir, exist_ok=True)
    write_mvm("NOOP")   # initialise

    if not os.path.exists(initial_image):
        print(f"ERROR: initial board image not found at {initial_image}")
        print("Save a photo of the starting position as assets/111.png")
        return

    # Start HTTP server in background thread
    t = threading.Thread(target=start_http_server, daemon=True)
    t.start()

    print(f"Watching:      {watch_dir}")
    print(f"Initial board: {initial_image}")
    print(f"EV3 polls:     http://192.168.137.1:{HTTP_PORT}  (update PC_IP in ev3/main.py if different)")
    print("Ready. Waiting for photos...\n")

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        handler  = ChessboardHandler(engine, initial_image)
        observer = Observer()
        observer.schedule(handler, path=watch_dir, recursive=False)
        observer.start()

        try:
            while not handler.board.is_game_over():
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            observer.stop()
            observer.join()

        print("\nGame over:", handler.board.result())

if __name__ == "__main__":
    main()
