from collections import Counter
from os import remove
from copy import deepcopy

import torch
import random
import doctest

deck_value={
    10:'Straight Flush', 9:'Four of a Kind', 8:'Full House',
    7:'Flush', 6:'Straight', 5:'Three of a Kind', 4:'Two Pair', 3:'One Pair', 2:'High Card',
}

max_players = 8

total_bet=0
copy_deck= {}
deck={
    "Hearts":[1,2,3,4,5,6,7,8,9,10,11,12,13],
    "Clubs":[1,2,3,4,5,6,7,8,9,10,11,12,13],
    "Spades":[1,2,3,4,5,6,7,8,9,10,11,12,13],
    "Diamonds":[1,2,3,4,5,6,7,8,9,10,11,12,13]
}
player={"1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[], "9":[]}
copy_player={"1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[], "9":[]}

copy_table=[]
table=[]

hand=[]


def full_deal_player(player_num):
    """
        Deals cards to all players and sets up the game.
        """

    for i in range(1,player_num):
        copy_player[str(i)].extend(copy_table)



def deal_player(player_num):
    """
        Deals cards to a single player.
        """
    for i in range(1,player_num):
        rd_card=r_choice(2)
        copy_player[str(i)]=rd_card

def complete_table():
    """
    Prepares and finalizes the communal cards on the table.
    """
    global copy_table, table
    copy_table=deepcopy(table)
    remaining=5-len(table)
    if remaining==0:
        copy_table=deepcopy(table)
    else:
        rem=r_choice(remaining)
        copy_table.extend(rem)


def r_choice(repeat):
    """
    Randomly selects a value or choice.
    """
    chosen_card_num=[]
    chosen_card_type=[]
    for _ in range(repeat):
        card_type=random.choice(list(copy_deck))
        chosen_card_type.append(card_type)

        random_value = random.choice(copy_deck[card_type])
        chosen_card_num.append(random_value)
        copy_deck[card_type].remove(random_value)

    chosen_card=list(zip(chosen_card_type,chosen_card_num))
    return chosen_card

def table_known(ct,cn):
    """
        Determines the known state of the table.
        """

    table.append((ct, cn))
    deck[ct].remove(cn)

def known(ct,cn):
    """
        Checks which cards or states are known in the game.
        """

    hand.append((ct,cn))
    deck[ct].remove(cn)

def straight(f_hand):
    """
       Checks if there is a straight in the current hand/cards.
       """
    final=[t[1] for t in f_hand]
    serial=set(final)

    if len(serial)<5:
        return False, None

    if 1 in serial:
        serial.add(14)

    serial=sorted(serial)
    serial=list(serial)

    checks = {
        5: [(4, 0)],
        6: [(5, 1), (4, 0)],
        7: [(6, 2), (5, 1), (4, 0)],
        8: [(7, 2), (6, 2), (5, 1), (4, 0)]
    }

    if len(serial) in checks:
        for i, j in checks[len(serial)]:
            if serial[i] - serial[j] == 4:
                serial=serial[j:i+1]
                return True, serial
    return False, None

def flush(f_hand):
    """
    Checks if there is a flush in the current hand/cards.
    """

    final=[t[0] for t in f_hand]
    unique=Counter(final)

    for item,cnt in unique.items():
        if cnt >= 5:
            return True, item
    return False, None

def straight_flush(f_hand):
    """
    Checks if there is a straight flush in the current hand/cards.
    """

    tff, goal_type = flush(f_hand)
    if not tff:
        return False, None


    chek_straight = [(goal_type, item[1]) for item in f_hand if item[0] == goal_type]

    tfs, goal_hand = straight(chek_straight)
    if tfs:
        return True, goal_hand

    return False, None

def same_card(f_hand):
    """
    Checks if there are cards with the same value.
    """
    final = [t[1] for t in f_hand]
    final = [14 if i == 1 else i for i in final]
    counts = Counter(final)
    count_values = sorted(counts.values(), reverse=True)

    if 4 in count_values:
        four_card = [card for card, cnt in counts.items() if cnt == 4][0]
        return 'Four of a Kind', four_card
    elif 3 in count_values and 2 in count_values:
        three_card= [card for card, cnt in counts.items() if cnt == 3][0]
        two_card = [card for card, cnt in counts.items() if cnt == 2][0]
        return 'Full House', (three_card, two_card)
    elif 3 in count_values:
        three_card= [card for card, cnt in counts.items() if cnt == 3][0]
        return 'Three of a Kind', three_card
    elif 2 in count_values:
        pairs = [card for card, count in counts.items() if count == 2]
        if len(pairs) == 2 or len(pairs) == 3:
            return 'Two Pair', sorted(pairs, reverse=True)
        two_card = [card for card, cnt in counts.items() if cnt == 2][0]
        return 'One Pair', two_card
    else:
        return 'High Card', max(final)

def worth(f_hand):
    """
    Calculates the worth of a hand or combination of cards.
    """
    final = sorted([t[1] for t in f_hand], reverse=True)
    def kicking(fulllist,base):
        kick = sorted([i for i in fulllist if base != i], reverse=True)
        kick=[14 if i == 1 else i for i in kick]
        return kick

    sfbool,sftype=straight_flush(f_hand)

    if sfbool:
        return 10, sorted(sftype, reverse=True)

    hand_type,numb=same_card(f_hand)


    if hand_type=='Four of a Kind':
        kick=kicking(final,numb)
        best_hand=[numb]*4 + [kick[0]]
        return 9, best_hand

    elif hand_type=='Full House':
        best_hand = [numb[0]] * 3 + [numb[1]] * 2
        return 8, best_hand

    fbool,ftype=flush(f_hand)
    if fbool:
        sorted_hand = sorted(f_hand, key=lambda x: x[1])
        flush_numbers=[i[1] for i in sorted_hand if ftype == i[0]]
        return 7, sorted(flush_numbers, reverse=True)

    sbool,stype=straight(f_hand)
    if sbool:
        return 6, sorted(stype, reverse=True)

    elif hand_type=='Three of a Kind':
        kick=kicking(final,numb)
        best_hand=[numb]*3 + kick[:2]
        return 5, best_hand
    elif hand_type=='Two Pair':
        kick=kicking(final,numb[0])
        kick2=kicking(kick,numb[1])
        best_hand=[numb[0]]*2 + [numb[1]]*2 + [kick2[0]]
        return 4, best_hand
    elif hand_type=='One Pair':
        kick=kicking(final,numb)
        best_hand=[numb]*2 + kick[:3]
        return 3, best_hand
    elif hand_type=='High Card':
        best_hand = final[:5]
        return 2, best_hand

def winlose(me, otherdict):
    """
    Determines the result of the game (win or lose).
    """


    if me>otherdict:
        return True, True
    elif me==otherdict:
        return True, False
    elif me<otherdict:
        return False, False

def questions():
    """
        Processes player's questions or decisions during the game.
        """
    global max_players
     # Initial maximum allowed players
    players = int(input("How many players are playing: "))
    if players < max_players:
        max_players = players
    while players > max_players:
        print(f"Error: The maximum number of players allowed is {max_players}. Please enter a valid number.")
        players = int(input("How many players are playing: "))
    bet = int(input("How much bets per person "))

    return players, bet


def table_questions():
    """
        Handles table-specific questions or actions.
        Verifies if the card type is valid, then checks if the card already exists on the table.
        If the card type is invalid or the card already exists, users are asked to re-enter.
    """
    while True:
        tctype = input("What is table card suit? ").capitalize()
        if tctype not in deck:
            print("Error: Invalid card type. Please enter a valid card type (e.g., Spades, Diamonds, etc.).")
            continue

        try:
            tcnum = int(input("What is table card rank? "))
        except ValueError:
            print("Error: Card number must be an integer. Please try again.")
            continue

        if tcnum not in deck[tctype]:
            print("Error: Invalid card number for the selected card type. Please try again.")
            continue

        if (tctype, tcnum) in table:
            print("Warning: This card is already on the table. Please enter a different card.")
        else:
            return tctype, tcnum


def simulate_games(players, bet):
    """
    Simulates a series of games for analysis or testing.
    """

    global copy_deck

    def result():
        global copy_player, player
        global copy_deck
        global hand
        global copy_table

        sumbet = 0

        mutable_hand = deepcopy(hand[:2])

        copy_deck=deepcopy(deck)

        copy_player=deepcopy(player)
        deal_player(players)
        copy_table=deepcopy(table)
        complete_table()

        mutable_hand.extend(copy_table)
        full_deal_player(players)


        best_rival = (0, [0,0,0,0,0])


        for i in range(1, players):
            mainval,handval=worth(copy_player[str(i)])
            if mainval > best_rival[0]:
                best_rival = mainval,handval
            elif mainval == best_rival[0] and handval > best_rival[1]:
                best_rival = mainval,handval
        my_power = worth(mutable_hand)
        comp = winlose(my_power, best_rival)

        sumbet = sumbet + (players * bet)

        if comp[0] and comp[1] :
            return ('win', my_power[0], sumbet)
        elif comp[0] and not comp[1]:
            return ('draw', my_power[0], bet / players)
        elif not comp[0] and not comp[1]:
            return ('lose', my_power[0], bet * (-1))



    return result()


def run_simulate(num_sim=10, player_num=4, bet=100):
    """
        Performs a full simulation of the game with multiple iterations.
    """

    global total_bet
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    outcomes = []
    card_values = []
    bet_results = []

    for _ in range(num_sim):
        result, card_value, bet_result = simulate_games(player_num, bet)
        outcomes.append(result)
        card_values.append(card_value)
        bet_results.append(bet_result)

    outcomes_tensor = torch.tensor([1 if outcome == 'win' else 2 if outcome == 'draw' else 0 for outcome in outcomes],
                                   device=device)
    card_values_tensor = torch.tensor(card_values, device=device)
    bet_results_tensor = torch.tensor(bet_results, device=device)

    outcomes_tensor = outcomes_tensor.repeat(1000)
    card_values_tensor = card_values_tensor.repeat(1000)
    bet_results_tensor = bet_results_tensor.repeat(1000)

    win_count = (outcomes_tensor == 1).sum().item()
    draw_count = (outcomes_tensor == 2).sum().item()
    total_bet += bet_results_tensor.sum().item()

    card_value_count = {i: (card_values_tensor == i).sum().item() for i in range(2, 11)}
    card_value_win_count = {i: ((card_values_tensor == i) & (outcomes_tensor == 1)).sum().item() for i in range(2, 11)}
    card_value_draw_count = {i: ((card_values_tensor == i) & (outcomes_tensor == 2)).sum().item() for i in range(2, 11)}

    print(f"Win rate: {win_count / (num_sim * 1000) * 100:.2f}%")
    print(f"Draw rate: {draw_count / (num_sim * 1000) * 100:.2f}%")
    print(f"Expected value (average win/loss): {total_bet / (num_sim * 1000):.2f}")

    for value in range(2, 11):
        value_name = deck_value[value]
        count = card_value_count[value]
        if count > 0:
            win_percentage = card_value_win_count[value] / count * 100
            draw_percentage = card_value_draw_count[value] / count * 100
            print(f"{value_name} appearing: {count / (num_sim * 1000) * 100:.2f}%")
            print(f"{value_name} win rate: {win_percentage:.2f}%")
            print(f"{value_name} draw rate: {draw_percentage:.2f}%")
        else:
            print(f"{value_name} Suitable cards did not arrive.")


for i in range(2):
    while True:
        cardkind = input("What is your card suit? ")
        cardnum = input("What is your card rank? ")

        if cardkind not in deck or not cardnum.isdigit() or int(cardnum) not in deck[cardkind]:
            print("Invalid input. Please enter a valid card suit and rank.")
        else:
            cardnum = int(cardnum)
            known(cardkind, cardnum)
            break

for i in range(4):
    np,b=questions()
    if i==1:
        for _ in range(3):
            tt, tn = table_questions()
            table_known(tt, tn)

    elif i==2:
        tt,tn=table_questions()
        table_known(tt, tn)

    elif i==3:
        tt,tn=table_questions()
        table_known(tt, tn)


    run_simulate(num_sim=50000,player_num=np, bet=b)



"""if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)"""

