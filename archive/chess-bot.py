import chess
import chess.engine
l =  [  0  ,  1  ,  2  ,  3  ,  4  ,  5  ,  6  ,  7  ] # hado ar9am li 3andom 3ala9a b li ta7t bihom 0 f liste lowla hiya A wu tania hiya 1
L_x= [ "A" , "B" , "C" , "D" , "E" , "F" , "G" , "H" ]
c_x= [ 355 , 455 , 555 , 655 , 755 , 855 , 955 ,1055 ]
L_y= [ "1" , "2" , "3" , "4" , "5" , "6" , "7" , "8" ]
c_y =[ 900 , 800 , 700 , 600 , 500 , 400 , 300 , 200 ]
def display_board(board):
    print(board)
def posi_mvm(stockfichmvm):
    mvm=list(stockfichmvm)

def posi_mvm(stockfichmvm):
	mvm=list(stockfichmvm)
	mvm[0]=mvm[0].upper()
	mvm[2]=mvm[2].upper()
	mvm0=c_x[L_x.index(mvm[0])]
	mvm1=c_y[L_y.index(mvm[1])]
	mvm2=c_x[L_x.index(mvm[2])]
	mvm3=c_y[L_y.index(mvm[3])]
	p_piece=mvm0,mvm1
	n_p_piece=mvm2,mvm3
	print("la piece joue",p_piece)
	print("nouvel place",n_p_piece)
posi_mvm("e2e4")
def play_game():
    # Set the path to your Stockfish executable
    stockfish_path = "stockfish-windows-x86-64-avx2.exe"

    # Initialize the chess board
    board = chess.Board()

    # Get the strength of Stockfish from the user
    intel = 5
    # Set up the Stockfish engine with the specified strength
    with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
        while not board.is_game_over():
            # Display the current position
            display_board(board)

            # Get user move
# Get user move
            while True:
                try:
                    user_move = input("Enter your move (e.g., e2e4): ")
                    board.push_uci(user_move)
                    break
                except (chess.IllegalMoveError, chess.InvalidMoveError):
                    if user_move == "exit":
                        exit()
                    print("Sorry, this move can't be played. Try again.")
            
            # Display the updated position
            print("\n")
            display_board(board)


            # Get Stockfish move with the specified strength
            result = engine.play(board, chess.engine.Limit(time=2.0, depth=intel))
            stockfish_move = result.move
            print("\n")
            print("Stockfish played:", stockfish_move)
            board.push(stockfish_move)
			

        # Display the final position
        display_board("\n", board)

        # Print the game result
        print("Game Over. Result: ", board.result())

if __name__ == "__main__":
    play_game()