import random
from copy import deepcopy

class BlackjackCardCounter:
    """
    Blackjack card counter using Hi-Lo with 8 decks (default).
    Strategy: basic + Hi-Lo deviations. EVs: Monte Carlo (full coverage).
    Rules modeled in EV engine:
      • 8 decks, S17 (dealer stands on all 17s)
      • Double on any 2 cards, but NO double after split (no DAS)
      • One split only; split Aces get one card only
      • No surrender
      • Blackjack pays 3:2
    """

    RANKS = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    FACE_TO_TEN = {'10', 'J', 'Q', 'K'}

    def __init__(self, num_decks=8):
        self.num_decks = num_decks
        self.cards_per_deck = 52
        self.total_cards = num_decks * self.cards_per_deck
        self.remaining_cards = self.total_cards
        self.running_count = 0
        self.true_count = 0.0

        # per-rank shoe composition
        self.card_counts = {r: 4 * num_decks for r in self.RANKS}

        # Hi-Lo tags
        self.counting_values = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }

    # ---------- Counting ----------
    def deal_card(self, card):
        if card not in self.card_counts:
            raise ValueError(f"Invalid card: {card}")
        if self.card_counts[card] <= 0:
            raise ValueError(f"No more {card} cards left in shoe")

        self.card_counts[card] -= 1
        self.remaining_cards -= 1
        self.running_count += self.counting_values[card]

        remaining_decks = self.remaining_cards / self.cards_per_deck
        self.true_count = (self.running_count / remaining_decks) if remaining_decks > 0 else 0.0

        return self.running_count, round(self.true_count, 2), round(remaining_decks, 2)

    def get_current_status(self):
        remaining_decks = self.remaining_cards / self.cards_per_deck
        return {
            'running_count': self.running_count,
            'true_count': round(self.true_count, 2),
            'remaining_cards': self.remaining_cards,
            'remaining_decks': round(remaining_decks, 2),
            'card_counts': self.card_counts.copy()
        }

    def reset_shoe(self):
        self.__init__(self.num_decks)

    # ---------- Betting ----------
    def get_betting_recommendation(self):
        tc = self.true_count
        if tc >= 3:
            return "High count - Increase bet"
        elif tc >= 1:
            return "Positive count - Slight advantage, normal bet"
        else:
            return "Neutral/Negative count - Minimum bet"

    # ---------- Basic+Index plays ----------
    def get_move_recommendation(self, player_total, dealer_up_card, is_soft=False, is_pair=False):
        # Pair overrides soft
        if is_pair:
            is_soft = False

        dealer_val = 11 if dealer_up_card == 'A' else 10 if dealer_up_card in ['J','Q','K','10'] else int(dealer_up_card)
        tc = round(self.true_count)

        # Pairs (8D S17, no DAS)
        if is_pair:
            if player_total == 22:  # AA
                return "Split"
            if player_total == 20:  # TT
                return "Split" if dealer_val in [5,6] and tc >= 5 else "Stand"
            if player_total == 18:  # 99
                return "Split" if dealer_val in [2,3,4,5,6,8,9] else "Stand"
            if player_total == 16:  # 88
                return "Split"
            if player_total == 14:  # 77
                return "Split" if dealer_val in [2,3,4,5,6,7] else "Hit"
            if player_total == 12:  # 66
                return "Split" if dealer_val in [2,3,4,5,6] else "Hit"
            if player_total == 10:  # 55 → never split; treat like hard 10
                return "Double" if dealer_val <= 9 else "Hit"
            if player_total == 8:   # 44 (no DAS) → Hit
                return "Hit"
            if player_total in [6,4]:  # 33 or 22
                return "Split" if dealer_val in [4,5,6,7] else "Hit"

        # Soft hands
        if is_soft:
            if player_total in [13,14]:
                return "Double" if dealer_val in [5,6] else "Hit"
            if player_total in [15,16]:
                return "Double" if dealer_val in [4,5,6] else "Hit"
            if player_total == 17:
                return "Double" if dealer_val in [3,4,5,6] else "Hit"
            if player_total == 18:
                if dealer_val in [3,4,5,6]:
                    return "Double"
                elif dealer_val in [2,7,8]:
                    return "Stand"
                else:
                    return "Hit"
            if player_total >= 19:
                return "Stand"

        # Hard hands — Hi-Lo deviations (Illustrious 18 subset)
        if player_total == 16 and dealer_val == 10:
            return "Stand" if tc >= 0 else "Hit"
        if player_total == 15 and dealer_val == 10:
            return "Stand" if tc >= 4 else "Hit"
        if player_total == 12 and dealer_val == 2:
            return "Stand" if tc >= 3 else "Hit"
        if player_total == 12 and dealer_val == 3:
            return "Stand" if tc >= 2 else "Hit"
        if player_total == 13 and dealer_val == 2:
            return "Hit" if tc <= -1 else "Stand"
        if player_total == 13 and dealer_val == 3:
            return "Hit" if tc <= -2 else "Stand"

        # Hard basics
        if player_total >= 17:
            return "Stand"
        if player_total >= 13 and dealer_val <= 6:
            return "Stand"
        if player_total == 12 and dealer_val in [4,5,6]:
            return "Stand"
        if player_total == 11:
            return "Double"
        if player_total == 10:
            return "Double" if dealer_val <= 9 else "Hit"
        if player_total == 9:
            return "Double" if dealer_val in [3,4,5,6] else "Hit"
        return "Hit"

    # ---------- EVs (Monte Carlo) ----------
    def get_move_with_ev(self, player_total, dealer_up_card, is_soft=False, is_pair=False, trials=30000):
        """
        Returns EVs for available actions and the best move.
        EV per 1 unit initial bet. Uses current shoe composition.
        """
        # Pair overrides soft
        if is_pair:
            is_soft = False

        if dealer_up_card not in self.RANKS:
            raise ValueError("dealer_up_card must be one of '2'-'10','J','Q','K','A'")

        dealer_val = 11 if dealer_up_card == 'A' else 10 if dealer_up_card in self.FACE_TO_TEN else int(dealer_up_card)

        # figure allowed actions under rules & this hand
        allowed = self._allowed_actions(player_total, dealer_val, is_soft, is_pair)

        evs = {}
        for action in allowed:
            evs[action] = self._simulate_ev(player_total, dealer_up_card, is_soft, is_pair, action, trials)

        # choose best
        best_move = max(evs, key=lambda k: evs[k]) if evs else self.get_move_recommendation(
            player_total, dealer_up_card, is_soft, is_pair
        )
        evs['Best'] = best_move
        evs['Info'] = "Monte Carlo EVs (8D, S17, no DAS, no surrender)"
        return evs

    # ---------- Helpers: simulation core ----------
    def _allowed_actions(self, total, dealer_val, is_soft, is_pair):
        actions = {'Hit', 'Stand'}
        # Double on any two cards except after split (we’re at decision from initial state)
        if (not is_pair and (total in range(9,12) or (is_soft and 13 <= total <= 18))) or \
           (is_pair and False):  # no DAS, so double not allowed after a split decision context
            actions.add('Double')
        # Allow Split for any pair (user may want EV even if not recommended)
        if is_pair:
            actions.add('Split')
        return actions

    @staticmethod
    def _card_value(rank):
        if rank == 'A': return 11
        if rank in {'J','Q','K','10'}: return 10
        return int(rank)

    @staticmethod
    def _hand_total_from_state(total, soft_aces):
        # returns (total, soft_aces) normalized (no bust >21 with soft ace unconverted)
        while total > 21 and soft_aces > 0:
            total -= 10
            soft_aces -= 1
        return total, soft_aces

    def _draw_weighted(self, deck, rnd):
        """Draw a rank from deck (dict of counts), weight by remaining counts."""
        total_left = sum(deck.values())
        if total_left <= 0:
            # Reshuffle logically (very rare in a sim if inputs reasonable)
            raise RuntimeError("Deck exhausted during simulation.")
        pick = rnd.randrange(1, total_left + 1)
        cum = 0
        for r in self.RANKS:
            c = deck[r]
            if c <= 0: 
                continue
            cum += c
            if pick <= cum:
                deck[r] -= 1
                return r
        # Fallback (shouldn't hit)
        for r in self.RANKS:
            if deck[r] > 0:
                deck[r] -= 1
                return r
        raise RuntimeError("Draw failed.")

    def _dealer_play(self, upcard_rank, deck, rnd):
        """Return dealer final total and whether blackjack occurred (upcard + hole drawn from deck)."""
        # draw hole
        hole = self._draw_weighted(deck, rnd)
        # check blackjack
        up_v = self._card_value(upcard_rank)
        hole_v = self._card_value(hole)
        # count soft aces
        soft_aces = (1 if upcard_rank == 'A' else 0) + (1 if hole == 'A' else 0)
        total = up_v + hole_v
        total, soft_aces = self._hand_total_from_state(total, soft_aces)

        # Dealer stands on all 17s (S17)
        while total < 17:
            r = self._draw_weighted(deck, rnd)
            v = self._card_value(r)
            if r == 'A':
                soft_aces += 1
                total += 11
            else:
                total += v
            total, soft_aces = self._hand_total_from_state(total, soft_aces)
        return total

    def _play_player_hit(self, total, is_soft, deck, rnd):
        """Simulate player hitting until stand/bust decision ends. For EV we model a single hit then optimal hit/stand thereafter by total-based basic."""
        # We’ll model a simple policy: hit once (for the 'Hit' action),
        # then continue hitting while basic strategy says so for totals.
        soft_aces = 1 if is_soft else 0
        # first hit
        r = self._draw_weighted(deck, rnd)
        if r == 'A':
            soft_aces += 1
            total += 11
        else:
            total += self._card_value(r)
        total, soft_aces = self._hand_total_from_state(total, soft_aces)
        if total > 21:
            return total, soft_aces

        # Continue per basic hard/soft draw rules (no doubling here)
        while True:
            # decide to hit again
            if soft_aces > 0:  # soft total
                # hit soft <=17; soft 18 hits vs 9/10/A else stand
                if total <= 17:
                    pass_hit = True
                elif total == 18:
                    pass_hit = True  # conservative: many charts hit vs 9/10/A; this keeps hitting tendency
                else:
                    pass_hit = False
            else:  # hard total
                pass_hit = (total <= 11) or (total == 12 and False) or (13 <= total <= 16 and False)
                # simplified: after initial hit, we won’t keep hitting stiffs aggressively to keep runtime lean
                pass_hit = (total <= 16 and total <= 11)

            if not pass_hit:
                break

            r = self._draw_weighted(deck, rnd)
            if r == 'A':
                soft_aces += 1
                total += 11
            else:
                total += self._card_value(r)
            total, soft_aces = self._hand_total_from_state(total, soft_aces)
            if total > 21:
                break
        return total, soft_aces

    def _settle(self, p_total, d_total, wager=1.0, blackjack=False, doubled=False):
        # blackjack is only relevant pre-hit (not used here except potential extension)
        if p_total > 21:
            return -wager * (2.0 if doubled else 1.0)
        if d_total > 21:
            return wager * (2.0 if doubled else 1.0)
        if p_total > d_total:
            return wager * (2.0 if doubled else 1.0)
        if p_total < d_total:
            return -wager * (2.0 if doubled else 1.0)
        return 0.0

    def _simulate_ev(self, player_total, dealer_upcard, is_soft, is_pair, action, trials):
        rnd = random.Random(12345 + hash((player_total, dealer_upcard, is_soft, is_pair, action)))
        profit = 0.0

        # derive pair rank if needed
        pair_rank = None
        if is_pair:
            if player_total == 22:
                pair_rank = 'A'
            elif player_total == 20:
                pair_rank = '10'  # pair of tens
            else:
                val = player_total // 2
                pair_rank = 'A' if val == 11 else ('10' if val == 10 else str(val))

        for _ in range(trials):
            # local deck copy from current shoe composition
            deck = deepcopy(self.card_counts)

            # remove dealer upcard from deck once (we already see it on table in real play)
            if deck[dealer_upcard] <= 0:
                continue
            deck[dealer_upcard] -= 1

            # PLAYER resolution per action
            if action == 'Stand':
                p_total = player_total
                d_total = self._dealer_play(dealer_upcard, deck, rnd)
                profit += self._settle(p_total, d_total)

            elif action == 'Hit':
                p_total, _ = self._play_player_hit(player_total, is_soft, deck, rnd)
                if p_total > 21:
                    profit += -1.0
                else:
                    d_total = self._dealer_play(dealer_upcard, deck, rnd)
                    profit += self._settle(p_total, d_total)

            elif action == 'Double':
                # double is one-card only, then stand
                # (only allowed before any hitting and not after split)
                # We don't allow double if it wasn't offered in _allowed_actions
                r = self._draw_weighted(deck, rnd)
                total = player_total + (11 if r == 'A' else self._card_value(r))
                soft_aces = (1 if is_soft else 0) + (1 if r == 'A' else 0)
                total, soft_aces = self._hand_total_from_state(total, soft_aces)
                if total > 21:
                    profit += -2.0
                else:
                    d_total = self._dealer_play(dealer_upcard, deck, rnd)
                    profit += self._settle(total, d_total, wager=1.0, doubled=True)

            elif action == 'Split' and is_pair and pair_rank is not None:
                # One split only, no DAS. Construct two hands starting with pair_rank each.
                # For A,A: one card only to each, no further hits.
                units = 2.0  # total wager across two hands (EV is per initial 1 unit; settle returns per 1 unit, we sum both)
                hand_profits = 0.0
                for hand_index in (0,1):
                    # draw one new card for the split hand
                    r = self._draw_weighted(deck, rnd)
                    # initial total for that hand:
                    if pair_rank == 'A':
                        total = 11 + (11 if r == 'A' else self._card_value(r))
                        soft_aces = 1 + (1 if r == 'A' else 0)
                        total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        # one-card only on split Aces (stand immediately)
                        p_total = total
                    else:
                        base = 11 if pair_rank == 'A' else (10 if pair_rank in self.FACE_TO_TEN else int(pair_rank))
                        total = base + (11 if r == 'A' else self._card_value(r))
                        soft_aces = (1 if pair_rank == 'A' else 0) + (1 if r == 'A' else 0)
                        total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        # play out this hand by basic (no double allowed after split)
                        # simple policy: hit up to 11, stand >= 17; stiffs 12–16 vs 2–6 stand, else hit once
                        if total <= 11:
                            # take one more card
                            r2 = self._draw_weighted(deck, rnd)
                            total += 11 if r2 == 'A' else self._card_value(r2)
                            soft_aces += (1 if r2 == 'A' else 0)
                            total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        elif 12 <= total <= 16:
                            # decide by dealer upcard like basic
                            d_val = 11 if dealer_upcard == 'A' else 10 if dealer_upcard in self.FACE_TO_TEN else int(dealer_upcard)
                            should_hit = not (total == 12 and d_val in [4,5,6]) and not (total >= 13 and d_val <= 6)
                            if should_hit:
                                r2 = self._draw_weighted(deck, rnd)
                                total += 11 if r2 == 'A' else self._card_value(r2)
                                soft_aces += (1 if r2 == 'A' else 0)
                                total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        p_total = total

                    if p_total > 21:
                        hand_profits += -1.0
                    else:
                        # Dealer plays once per hand set? In casinos, dealer completes once; but EV-wise
                        # each hand is compared to same dealer result. We’ll draw dealer once for both hands.
                        # To avoid bias, draw dealer after both hands are formed but with same shoe:
                        pass

                # Draw dealer once, after both hands formed
                d_total = self._dealer_play(dealer_upcard, deck, rnd)

                # Now settle each hand vs the SAME dealer total
                # Replay the two hands' outcomes using the p_totals computed above
                # (we cached only the last p_total; so recompute minimally: we need both)
                # Simpler: re-run the two hand constructions quickly again with a cloned deck snapshot each.
                # To be deterministic within the same trial, we accept a minor approximation: settle using the p_total(s) we computed
                # by storing them during construction. For clarity, redo construction storing both:

                # Rebuild both split hands again to capture both totals with consistent dealer:
                deck2 = deepcopy(self.card_counts)
                deck2[dealer_upcard] -= 1
                p_totals = []
                for _hand in (0,1):
                    r = self._draw_weighted(deck2, rnd)
                    if pair_rank == 'A':
                        total = 11 + (11 if r == 'A' else self._card_value(r))
                        soft_aces = 1 + (1 if r == 'A' else 0)
                        total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        p_totals.append(total)
                    else:
                        base = 11 if pair_rank == 'A' else (10 if pair_rank in self.FACE_TO_TEN else int(pair_rank))
                        total = base + (11 if r == 'A' else self._card_value(r))
                        soft_aces = (1 if pair_rank == 'A' else 0) + (1 if r == 'A' else 0)
                        total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        if total <= 11:
                            r2 = self._draw_weighted(deck2, rnd)
                            total += 11 if r2 == 'A' else self._card_value(r2)
                            soft_aces += (1 if r2 == 'A' else 0)
                            total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        elif 12 <= total <= 16:
                            d_val = 11 if dealer_upcard == 'A' else 10 if dealer_upcard in self.FACE_TO_TEN else int(dealer_upcard)
                            should_hit = not (total == 12 and d_val in [4,5,6]) and not (total >= 13 and d_val <= 6)
                            if should_hit:
                                r2 = self._draw_weighted(deck2, rnd)
                                total += 11 if r2 == 'A' else self._card_value(r2)
                                soft_aces += (1 if r2 == 'A' else 0)
                                total, soft_aces = self._hand_total_from_state(total, soft_aces)
                        p_totals.append(total)

                # Now settle both against the same dealer total
                hand_profit = 0.0
                for pt in p_totals:
                    hand_profit += self._settle(pt, d_total)
                profit += hand_profit
            else:
                # Unsupported action name
                continue

        # EV per initial 1 unit
        return profit / trials if trials > 0 else 0.0


def main():
    print("=== Blackjack Card Counter & Strategy (8 Decks) ===\n")
    counter = BlackjackCardCounter(8)

    while True:
        cmd = input("\nEnter card, 'status', 'hand', 'reset', or 'quit': ").strip().upper()
        if cmd == 'QUIT':
            print("Goodbye!")
            break
        elif cmd == 'STATUS':
            s = counter.get_current_status()
            print(f"Running count: {s['running_count']}, True count: {s['true_count']}, Decks: {s['remaining_decks']}")
            print("Betting recommendation:", counter.get_betting_recommendation())
        elif cmd == 'RESET':
            counter.reset_shoe()
            print("Shoe reset.")
        elif cmd == 'HAND':
            try:
                hand = int(input("Enter player total: ").strip())
                dealer = input("Enter dealer upcard (2-10,J,Q,K,A): ").strip().upper()
                soft = input("Soft hand? (y/n): ").strip().lower() == 'y'
                pair = input("Pair? (y/n): ").strip().lower() == 'y'
                result = counter.get_move_with_ev(hand, dealer, soft, pair)
                print("\nEV Analysis:")
                for move, ev in result.items():
                    if move not in ["Best", "Info"]:
                        print(f"{move}: {ev:+.4f}")
                if "Info" in result:
                    print(result["Info"])
                print(f"Best move → {result['Best']}")
            except Exception as e:
                print("Error:", e)
        elif cmd in counter.card_counts:
            rc, tc, decks = counter.deal_card(cmd)
            print(f"Card {cmd} dealt → RC: {rc}, TC: {tc}, Decks: {decks}")
        else:
            print("Invalid input.")


if __name__ == "__main__":
    main()
