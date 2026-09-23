"""
chessboard_mvmnt_detection.py
==============================
Standalone vision class — same logic as chess_bot.py but importable separately.
Useful for testing vision independently of the full game loop.

Label convention: lowercase 'h8'..'a1'  (matches chess_bot.py and codelowl.py)
Crop:             image[1480:1480+1230, 870:870+1250]
"""
import cv2
import numpy as np


class chessboard_mvmnt_detection:

    @staticmethod
    def bege_en_rouge(image_path: str) -> np.ndarray:
        image = cv2.imread(image_path)
        image = image[1480:1480+1230, 870:870+1250]
        couleur_source   = np.array([72, 155, 194])
        nouvelle_couleur = np.array([0, 0, 255])
        tolerance = 50
        masque = np.all(np.abs(image - couleur_source) < tolerance, axis=-1)
        image[masque] = nouvelle_couleur
        return image

    @staticmethod
    def presence_rouge(square: np.ndarray) -> bool:
        couleur_a_detecter = np.array([0, 0, 255])
        tolerance = 10
        masque = cv2.inRange(
            square,
            couleur_a_detecter - tolerance,
            couleur_a_detecter + tolerance,
        )
        return np.sum(masque > 0) > 3000

    @staticmethod
    def chessboard_to_table(image_path: str,
                             pos_label_tochange=None,
                             value_tochange=None) -> dict:
        """
        Returns {label: bool} for all 64 squares.
        Labels: 'h8' (top-left of crop) .. 'a1' (bottom-right).
        chr(ord('h') - row), 8 - col  — matches codelowl.py final source.
        """
        image = chessboard_mvmnt_detection.bege_en_rouge(image_path)
        sq_h  = image.shape[0] // 8
        sq_w  = image.shape[1] // 8
        result = {}
        for row in range(8):
            for col in range(8):
                x1, y1 = col * sq_w,  row * sq_h
                sq     = image[y1:y1+sq_h, x1:x1+sq_w]
                label  = f"{chr(ord('h') - row)}{8 - col}"
                result[label] = chessboard_mvmnt_detection.presence_rouge(sq)
        if pos_label_tochange in result and isinstance(value_tochange, bool):
            result[pos_label_tochange] = value_tochange
        return result

    @staticmethod
    def get_mvmnt(image1: str, image2: str, stk: list = None) -> str | None:
        """
        Returns UCI move string e.g. 'e2e4', or None.
        stk: optional capture stack (same as chess_bot.py global stk).
        """
        if stk is None:
            stk = []

        t1 = chessboard_mvmnt_detection.chessboard_to_table(image1)
        t2 = chessboard_mvmnt_detection.chessboard_to_table(image2)

        if stk:
            captured_dest = stk.pop(0)
            dest_sq = f"{captured_dest[2]}{captured_dest[3]}"
            t1 = chessboard_mvmnt_detection.chessboard_to_table(image1, dest_sq, False)

        full_to_empty = [sq for sq, val in t1.items() if val     and not t2[sq]]
        empty_to_full = [sq for sq, val in t1.items() if not val and t2[sq]]

        # White castling
        if set(full_to_empty) == {"h1", "e1"} and set(empty_to_full) == {"g1", "f1"}:
            return "e1g1"
        if set(full_to_empty) == {"e1", "a1"} and set(empty_to_full) == {"d1", "c1"}:
            return "e1c1"

        if len(full_to_empty) == 1 and len(empty_to_full) == 1:
            return f"{full_to_empty[0]}{empty_to_full[0]}"

        print(f"get_mvmnt: unresolved — {full_to_empty=} {empty_to_full=}")
        return None
