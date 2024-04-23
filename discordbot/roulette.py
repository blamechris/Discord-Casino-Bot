from database import *
from math import *
from random import randint

class roulette:
    # Creation of Roulette Table Roules
    # Straight-up
    # Split
    # Basket
    # Street
    # Corner
    # Six-Line
    # 1st Column
    # 2nd Column
    # 3rd Column
    # 1st Dozen
    # 2nd Dozen
    # 3rd Dozen
    # Odd
    # Even
    # Red
    # Black
    # 1 to 18
    # 19 to 36

    def __init__(self, db) -> None:
        self.selection = {
        "Straight-up"   : 35,
        "Split"         : 17,
        "Street"        : 11,
        "Corner"        : 8,
        "Six-line"      : 5,
        "1st-Column"    : 2,
        "2nd-Column"    : 2,
        "3rd-Column"    : 2,
        "1st-Dozen"     : 2,
        "2nd-Dozen"     : 2,
        "3rd-Dozen"     : 2,
        "Odd"           : 1,
        "Even"          : 1,
        "Red"           : 1,
        "Black"         : 1,
        "1-18"          : 1,
        "19-36"         : 1
        }
        self.player = {
        "user_id"   : 0,
        "Selection" : "",
        "Selection2" : 0,
        "wager"     : 0,
        "outcome"   : ""
        }
        self.players = []
        self.rouletteID = 1
        self.result = 0
        self.red = (32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3)
        self.black = (15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 26)
        self.database = db
        pass  

    # Roulette Spin
    def spin_roulette(self):
        self.result = randint(1, 38)
        self.database.update_roulette(self.result)
        self.determine_winners()
        self.next_round()
        return (self.players, self.result)
    
    def determine_winners(self):
        for roulette_player in self.players:   
            choice = roulette_player["Selection2"]
            match roulette_player["Selection"]:
                case "Straight-up":
                    if(self.result == choice):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Split":
                    if(self.result == choice or 
                       self.result == choice + 3):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Street":
                    if(self.result == choice or 
                       self.result == choice + 3 or
                       self.result == choice - 3):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Corner":
                    # Value X is player's input
                    # Equation
                    # Determine Row R, and Column C
                    # R = 1 + ⌊(x-1)/2⌋
                    # C = 1 + (x-1) mod 2
                    # Getting top left square and then determine remaining values
                    # Formula for top left, TL
                    # TL = (3(R-1)) + C
                    # TR = TL + 1
                    # BL = TL + 3
                    # BR = TR + 3
                    R = 1 + floor((choice)/2)
                    C = 1 + ((choice - 1) % 2)
                    TL = (3(R-1) + C)
                    TR = TL + 1
                    BL = TL + 3
                    BR = BR + 3
                    if(self.result == TL or
                       self.result == TR or
                       self.result == BL or
                       self.result == BR):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Five":
                    if(self.result in (1, 2, 3, 37, 38)):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Six-Line":
                    # Value X is player's input
                    # Equation
                    # Determine Row R, and Column C
                    # R = 1 + ⌊(x-1)/2⌋
                    # C = 1 + (x-1) mod 2
                    # Getting top left square and then determine remaining values
                    # Formula for top left, TL
                    # TL = (3(R-1)) + C
                    # TM = TL + 1
                    # TR = TL + 2
                    # BL = TL + 3
                    # BM = TM + 3
                    # BR = TR + 3
                    R = choice
                    TL = ((3*R)+1)
                    TM = TL + 1
                    TR = TL + 2
                    BL = TL + 3
                    BM = TM + 3
                    BR = BR + 3
                    if(self.result == TL or
                       self.result == TM or
                       self.result == TR or
                       self.result == BL or
                       self.result == BM or
                       self.result == BR):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "1st-Dozen":
                    if(self.result < 13):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "2nd-Dozen":
                    if(self.result > 12 and self.result < 25):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "3rd-Dozen":
                    if(self.result > 24 and self.result < 37):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "1st-Dozen":
                    if((self.result % 3)==1):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "2nd-Dozen":
                    if((self.result % 3)==2):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "3rd-Dozen":
                    if((self.result % 3)==0):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "1-18":
                    if(self.result < 19):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "19-36":
                    if(self.result > 18):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Red":
                    if(self.result in self.red):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Black":
                    if(self.result in self.black):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Even":
                    if((self.result % 2) == 0):
                        # win
                        roulette_player["outcome"] = "WIN"
                case "Odd":
                    if((self.result %2) == 1):
                        roulette_player["outcome"] = "WIN"
            # Lose
            if not (roulette_player["outcome"] == "WIN"):
                roulette_player["outcome"] = "LOSE"
            self.database.roulette_results(roulette_player["outcome"], roulette_player["user_id"])
        return
    
    def add_player(self, user_id, wager, bet, option):
        self.database.input_user_bet_roulette(user_id, wager, bet, option)
        self.players.append({
            "user_id"   : user_id,
            "Selection" : bet,
            "Selection2": option,
            "wager"     : bet,
            "outcome"   : ""
        })
        return
        
    def next_round(self):
        self.database.start_next_roulette_round()




