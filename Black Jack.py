import pygame
import random
import time

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack with Edge Calculator")
font = pygame.font.SysFont('Arial', 24)
bold_font = pygame.font.SysFont('Arial', 28, bold=True)

# Color definitions
GREEN = (0, 100, 0)  # Table background
WHITE = (255, 255, 255)  # Card background
BLACK = (0, 0, 0)  # Text and UI elements
GOLD = (255, 215, 0)  # Buttons and highlights
RED = (255, 0, 0)  # Hearts and Diamonds
BLUE = (0, 0, 255)  # Hidden card
YELLOW = (255, 255, 0)  # Edge calculator highlights
ORANGE = (255, 165, 0)  # Warning messages

# Complete Basic Strategy Table (Simplified for 4-8 decks)
BASIC_STRATEGY = {
    # Hard Totals
    **{(total, upcard): {'action': 'H'} for total in range(5, 9) for upcard in range(2, 12)},
    **{(9, upcard): {'action': 'D' if upcard in range(3, 7) else 'H'} for upcard in range(2, 12)},
    **{(total, upcard): {'action': 'D' if upcard in range(2, 10) else 'H'} for total in [10] for upcard in range(2, 12)},
    **{(total, upcard): {'action': 'D'} for total in [11] for upcard in range(2, 12)},
    **{(total, upcard): {'action': 'H' if upcard in [2, 3, 7, 8, 9, 10, 11] else 'S'} for total in [12] for upcard in range(2, 12)},
    **{(total, upcard): {'action': 'S' if upcard in range(2, 7) else 'H'} for total in [13, 14] for upcard in range(2, 12)},
    **{(15, upcard): {'action': 'R' if upcard == 10 else ('S' if upcard in range(2, 7) else 'H')} for upcard in range(2, 12)},
    **{(16, upcard): {'action': 'R' if upcard in [9, 10, 11] else ('S' if upcard in range(2, 7) else 'H')} for upcard in range(2, 12)},
    **{(total, upcard): {'action': 'S'} for total in range(17, 22) for upcard in range(2, 12)},

    # Soft Totals
    **{('A2', upcard): {'action': 'D' if upcard in [5, 6] else 'H'} for upcard in range(2, 12)},
    **{('A3', upcard): {'action': 'D' if upcard in [5, 6] else 'H'} for upcard in range(2, 12)},
    **{('A4', upcard): {'action': 'D' if upcard in [4, 5, 6] else 'H'} for upcard in range(2, 12)},
    **{('A5', upcard): {'action': 'D' if upcard in [4, 5, 6] else 'H'} for upcard in range(2, 12)},
    **{('A6', upcard): {'action': 'D' if upcard in [3, 4, 5, 6] else 'H'} for upcard in range(2, 12)},
    **{('A7', upcard): {'action': 'D' if upcard in range(2, 7) else ('H' if upcard in [9, 10, 11] else 'S')} for upcard in range(2, 12)},
    **{('A8', upcard): {'action': 'D' if upcard == 6 else 'S'} for upcard in range(2, 12)},
    **{('A9', upcard): {'action': 'S'} for upcard in range(2, 12)},

    # Pairs
    **{('22', upcard): {'action': 'P' if upcard in range(2, 8) else 'H'} for upcard in range(2, 12)},
    **{('33', upcard): {'action': 'P' if upcard in range(2, 8) else 'H'} for upcard in range(2, 12)},
    **{('44', upcard): {'action': 'P' if upcard in [5, 6] else 'H'} for upcard in range(2, 12)},
    **{('55', upcard): {'action': 'D' if upcard in range(2, 10) else 'H'} for upcard in range(2, 12)},
    **{('66', upcard): {'action': 'P' if upcard in range(2, 7) else 'H'} for upcard in range(2, 12)},
    **{('77', upcard): {'action': 'P' if upcard in range(2, 8) else 'H'} for upcard in range(2, 12)},
    **{('88', upcard): {'action': 'P'} for upcard in range(2, 12)},
    **{('99', upcard): {'action': 'P' if upcard in range(2, 7) or upcard in [8, 9] else 'S'} for upcard in range(2, 12)},
    **{('TT', upcard): {'action': 'S'} for upcard in range(2, 12)},
    **{('AA', upcard): {'action': 'P'} for upcard in range(2, 12)},
}


# Deck Class
class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        """Reset and shuffle the deck."""
        ranks = [str(n) for n in range(2, 11)] + ['J', 'Q', 'K', 'A']
        suits = ['H', 'D', 'C', 'S']  # Hearts, Diamonds, Clubs, Spades
        self.cards = [r + s for r in ranks for s in suits]
        random.shuffle(self.cards)

    def deal(self):
        """Deal a card from the deck."""
        if not self.cards:
            self.reset()  # Reshuffle if deck is empty
        return self.cards.pop()


# Button Class
class Button:
    def __init__(self, text, x, y, w, h, callback, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.enabled = enabled

    def draw(self):
        """Draw the button on the screen."""
        color = GOLD if self.enabled else (150, 150, 150)
        pygame.draw.rect(screen, color, self.rect)
        text_color = BLACK if self.enabled else (50, 50, 50)
        text_surf = bold_font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


# Blackjack Game Class
class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = []
        self.dealer_hand = []
        self.chips = 1000  # Starting chips
        self.current_bet = 0
        self.game_over = True
        self.result_message = ""
        self.edge_info = ""
        self.recommended_action = ""

        # Add auto-play related properties
        self.is_auto_playing = False
        self.auto_play_rounds = 0  # Total rounds remaining
        self.last_auto_play_time = 0
        self.auto_play_delay = 500  # milliseconds between actions

        # Initialize buttons
        self.buttons = [
            Button("Hit", 800, 600, 100, 50, self.hit, False),
            Button("Stand", 920, 600, 100, 50, self.stand, False),
            Button("Double", 1040, 600, 100, 50, self.double, False),
            Button("Deal", 800, 660, 340, 50, self.start_round),
            Button("+10", 50, 600, 80, 40, lambda: self.place_bet(10)),
            Button("+50", 140, 600, 80, 40, lambda: self.place_bet(50)),
            Button("+100", 230, 600, 80, 40, lambda: self.place_bet(100)),
            Button("Clear", 320, 600, 80, 40, self.clear_bet),
            Button("Auto Play 10", 50, 660, 150, 50, self.start_auto_play)
        ]

    def start_auto_play(self):
        """Start or add to the auto-play sequence."""
        if self.game_over:
            self.is_auto_playing = True
            self.auto_play_rounds += 10  # Add 10 more rounds
            if self.last_auto_play_time == 0:  # Start the auto-play if not already running
                self.last_auto_play_time = pygame.time.get_ticks()

    def handle_auto_play(self):
        """Handle auto-play logic."""
        if not self.is_auto_playing or self.auto_play_rounds <= 0:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_auto_play_time < self.auto_play_delay:
            return

        self.last_auto_play_time = current_time

        if self.game_over:
            # Start new round
            self.clear_bet()
            bet_amount = max(1, self.chips // 10)
            if bet_amount > self.chips:
                bet_amount = self.chips
            if bet_amount == 0:
                self.is_auto_playing = False
                self.auto_play_rounds = 0
                return
            self.place_bet(bet_amount)
            self.start_round()
        else:
            # Process player's turn
            if "Split" in self.recommended_action:
                self.hit()  # Fallback for unsupported split
            elif self.recommended_action == "Double":
                if len(self.player_hand) == 2 and self.chips >= self.current_bet:
                    self.double()
                else:
                    self.hit()  # Fallback if can't double
            elif self.recommended_action == "Hit":
                self.hit()
            elif self.recommended_action == "Stand":
                self.stand()

            # Check if round completed
            if self.game_over:
                self.auto_play_rounds -= 1
                if self.auto_play_rounds <= 0:
                    self.is_auto_playing = False

    def place_bet(self, amount):
        """Place a bet if the player has enough chips."""
        if self.game_over and self.chips >= amount:
            self.current_bet += amount
            self.chips -= amount

    def clear_bet(self):
        """Clear the current bet and return chips to the player."""
        if self.game_over:
            self.chips += self.current_bet
            self.current_bet = 0

    def start_round(self):
        """Start a new round of Blackjack."""
        if self.current_bet > 0 and self.game_over:
            self.player_hand = [self.deck.deal(), self.deck.deal()]
            self.dealer_hand = [self.deck.deal(), self.deck.deal()]
            self.game_over = False
            self.result_message = ""
            # Enable game action buttons
            for btn in self.buttons[:3]:
                btn.enabled = True
            self.calculate_edge()

    def calculate_hand_value(self, hand):
        """Calculate the value of a hand, accounting for Aces."""
        value = 0
        aces = 0
        for card in hand:
            rank = card[:-1]
            if rank == 'A':
                aces += 1
                value += 11
            elif rank in ['J', 'Q', 'K']:
                value += 10
            else:
                value += int(rank)

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    def calculate_edge(self):
        """Calculate the best move based on the current hand."""
        if len(self.dealer_hand) < 2 or len(self.player_hand) < 2:
            return

        dealer_upcard = self.dealer_hand[1][:-1]
        try:
            dealer_value = int(dealer_upcard) if dealer_upcard.isdigit() else 10 if dealer_upcard in ['J','Q','K'] else 11
        except:
            dealer_value = 11  # Ace

        player_total, is_soft = self.calculate_hand_type()
        player_key = None

        if len(self.player_hand) == 2 and self.player_hand[0][:-1] == self.player_hand[1][:-1]:
            player_key = f"{self.player_hand[0][:-1]}{self.player_hand[1][:-1]}"
        elif is_soft and len(self.player_hand) == 2:
            player_key = f"A{player_total - 11}"
        else:
            player_key = player_total

        strategy = BASIC_STRATEGY.get((player_key, dealer_value), {})
        action_map = {'H': 'Hit', 'S': 'Stand', 'D': 'Double', 'P': 'Split', 'R': 'Surrender'}
        self.recommended_action = action_map.get(strategy.get('action', ''), '--')
        self.edge_info = f"Recommended: {self.recommended_action}"

    def calculate_hand_type(self):
        """Determine if the hand is hard, soft, or a pair."""
        value = 0
        aces = 0
        for card in self.player_hand:
            rank = card[:-1]
            if rank == 'A':
                aces += 1
                value += 11
            elif rank in ['J', 'Q', 'K']:
                value += 10
            else:
                value += int(rank)

        soft = False
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
            if aces > 0:
                soft = True
        return value, soft

    def hit(self):
        """Player draws a card."""
        if not self.game_over:
            self.player_hand.append(self.deck.deal())
            if self.calculate_hand_value(self.player_hand) > 21:
                self.game_over = True
                self.result_message = "Player busts! Dealer wins."
                self.settle_bet("lose")
            self.calculate_edge()

    def stand(self):
        """Player stands, and the dealer plays."""
        if not self.game_over:
            while self.calculate_hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.deal())

            player_value = self.calculate_hand_value(self.player_hand)
            dealer_value = self.calculate_hand_value(self.dealer_hand)

            if dealer_value > 21:
                self.result_message = "Dealer busts! Player wins."
                self.settle_bet("win")
            elif player_value > dealer_value:
                self.result_message = "Player wins!"
                self.settle_bet("win")
            elif player_value == dealer_value:
                self.result_message = "Push! It's a tie."
                self.settle_bet("push")
            else:
                self.result_message = "Dealer wins!"
                self.settle_bet("lose")

            self.game_over = True
            # Disable game action buttons
            for btn in self.buttons[:3]:
                btn.enabled = False

    def double(self):
        """Player doubles their bet and takes one more card."""
        if not self.game_over and len(self.player_hand) == 2 and self.chips >= self.current_bet:
            self.chips -= self.current_bet
            self.current_bet *= 2
            self.hit()
            self.stand()

    def settle_bet(self, outcome):
        """Settle the bet based on the game outcome."""
        if outcome == "win":
            self.chips += self.current_bet * 2
        elif outcome == "push":
            self.chips += self.current_bet
        self.current_bet = 0

    def draw_card(self, card, x, y, hidden=False):
        """Draw a card on the screen."""
        if hidden:
            pygame.draw.rect(screen, BLUE, (x, y, 100, 140))
        else:
            pygame.draw.rect(screen, WHITE, (x, y, 100, 140))
            rank = card[:-1]
            suit = card[-1]
            color = RED if suit in ['H', 'D'] else BLACK
            text_surf = bold_font.render(f"{rank}{suit}", True, color)
            screen.blit(text_surf, (x + 10, y + 10))

    def draw(self):
        """Draw the game interface."""
        screen.fill(GREEN)

        # Draw auto-play status
        if self.is_auto_playing:
            auto_text = bold_font.render(f"Auto Plays Remaining: {self.auto_play_rounds}", True, YELLOW)
            screen.blit(auto_text, (50, 150))

        # Draw chips and bet information
        chips_text = bold_font.render(f"Chips: ${self.chips}", True, GOLD)
        bet_text = bold_font.render(f"Current Bet: ${self.current_bet}", True, GOLD)
        screen.blit(chips_text, (50, 50))
        screen.blit(bet_text, (50, 100))

        # Draw edge calculator
        edge_rect = pygame.Rect(50, 160, 300, 110)
        pygame.draw.rect(screen, BLACK, edge_rect)
        edge_title = bold_font.render("Edge Calculator", True, GOLD)
        screen.blit(edge_title, (60, 160))
        action_text = font.render(self.recommended_action, True, YELLOW)
        screen.blit(action_text, (60, 200))
        info_lines = self.edge_info.split("|")
        for i, line in enumerate(info_lines):
            text_surf = font.render(line.strip(), True, WHITE)
            screen.blit(text_surf, (60, 230 + i * 25))

        # Draw dealer's hand
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        dealer_text = font.render(f"Dealer's Hand: {dealer_value if self.game_over else '?'}", True, WHITE)
        screen.blit(dealer_text, (400, 50))
        for i, card in enumerate(self.dealer_hand):
            self.draw_card(card, 400 + i * 120, 100, hidden=(i == 0 and not self.game_over))

        # Draw player's hand
        player_value = self.calculate_hand_value(self.player_hand)
        player_text = font.render(f"Your Hand: {player_value}", True, WHITE)
        screen.blit(player_text, (400, 350))
        for i, card in enumerate(self.player_hand):
            self.draw_card(card, 400 + i * 120, 400)

        # Draw buttons
        for btn in self.buttons:
            btn.draw()
            # Disable buttons with a semi-transparent overlay
            if not btn.enabled:
                s = pygame.Surface((btn.rect.w, btn.rect.h))
                s.set_alpha(128)
                s.fill((0, 0, 0))
                screen.blit(s, btn.rect.topleft)


# Main function
def main():
    game = BlackjackGame()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for btn in game.buttons:
                    if btn.rect.collidepoint(pos) and btn.enabled:
                        btn.callback()

        # Handle auto-play
        game.handle_auto_play()

        game.draw()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()