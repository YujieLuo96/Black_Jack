import pygame
import random
from collections import defaultdict

# 初始化Pygame
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack with Betting System")
font = pygame.font.SysFont('Arial', 24)
bold_font = pygame.font.SysFont('Arial', 28, bold=True)

# 颜色定义
GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


class Deck:
    def __init__(self):
        self.cards = []
        self.reset()

    def reset(self):
        ranks = [str(n) for n in range(2, 11)] + ['J', 'Q', 'K', 'A']
        suits = ['H', 'D', 'C', 'S']
        self.cards = [r + s for r in ranks for s in suits]
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            self.reset()
        return self.cards.pop()


class Button:
    def __init__(self, text, x, y, w, h, callback, enabled=True):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback
        self.enabled = enabled

    def draw(self):
        color = GOLD if self.enabled else (150, 150, 150)
        pygame.draw.rect(screen, color, self.rect)
        text_color = BLACK if self.enabled else (50, 50, 50)
        text_surf = bold_font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player_hand = []
        self.dealer_hand = []
        self.chips = 1000  # 初始筹码
        self.current_bet = 0
        self.game_over = True  # 初始状态为等待下注
        self.result_message = ""

        # 创建操作按钮
        self.buttons = [
            Button("Hit", 800, 600, 100, 50, self.hit, False),
            Button("Stand", 920, 600, 100, 50, self.stand, False),
            Button("Double", 1040, 600, 100, 50, self.double, False),
            Button("Deal", 800, 660, 340, 50, self.start_round),
            Button("+10", 50, 600, 80, 40, lambda: self.place_bet(10)),
            Button("+50", 140, 600, 80, 40, lambda: self.place_bet(50)),
            Button("+100", 230, 600, 80, 40, lambda: self.place_bet(100)),
            Button("Clear", 320, 600, 80, 40, self.clear_bet)
        ]

    def place_bet(self, amount):
        if self.game_over and self.chips >= amount:
            self.current_bet += amount
            self.chips -= amount

    def clear_bet(self):
        if self.game_over:
            self.chips += self.current_bet
            self.current_bet = 0

    def start_round(self):
        if self.current_bet > 0 and self.game_over:
            self.player_hand = [self.deck.deal(), self.deck.deal()]
            self.dealer_hand = [self.deck.deal(), self.deck.deal()]
            self.game_over = False
            self.result_message = ""
            # 启用游戏操作按钮
            for btn in self.buttons[:3]:
                btn.enabled = True

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        for card in hand:
            rank = card[:-1]
            if rank in ['J', 'Q', 'K']:
                value += 10
            elif rank == 'A':
                value += 11
                aces += 1
            else:
                value += int(rank)

        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    def settle_bet(self, outcome):
        if outcome == "win":
            self.chips += self.current_bet * 2
        elif outcome == "push":
            self.chips += self.current_bet
        self.current_bet = 0

    def hit(self):
        if not self.game_over:
            self.player_hand.append(self.deck.deal())
            if self.calculate_hand_value(self.player_hand) > 21:
                self.game_over = True
                self.result_message = "Player Bust！"
                self.settle_bet("lose")

    def stand(self):
        if not self.game_over:
            while self.calculate_hand_value(self.dealer_hand) < 17:
                self.dealer_hand.append(self.deck.deal())

            player_value = self.calculate_hand_value(self.player_hand)
            dealer_value = self.calculate_hand_value(self.dealer_hand)

            if dealer_value > 21:
                self.result_message = "Bank Bust，Player Win！"
                self.settle_bet("win")
            elif player_value > dealer_value:
                self.result_message = "Player Win！"
                self.settle_bet("win")
            elif player_value == dealer_value:
                self.result_message = "Draw！"
                self.settle_bet("push")
            else:
                self.result_message = "Banker Win！"
                self.settle_bet("lose")

            self.game_over = True
            # 禁用游戏操作按钮
            for btn in self.buttons[:3]:
                btn.enabled = False

    def double(self):
        if not self.game_over and len(self.player_hand) == 2 and self.chips >= self.current_bet:
            self.chips -= self.current_bet
            self.current_bet *= 2
            self.hit()
            self.stand()

    def draw_card(self, card, x, y, hidden=False):
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
        screen.fill(GREEN)

        # 绘制筹码信息
        chips_text = bold_font.render(f"chips: ${self.chips}", True, GOLD)
        bet_text = bold_font.render(f"current bet: ${self.current_bet}", True, GOLD)
        screen.blit(chips_text, (50, 50))
        screen.blit(bet_text, (50, 100))

        # 绘制结果信息
        result_surf = bold_font.render(self.result_message, True, WHITE)
        screen.blit(result_surf, (400, 300))

        # 绘制庄家手牌
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        dealer_text = font.render(f"Banker: {dealer_value if self.game_over else '?'}", True, WHITE)
        screen.blit(dealer_text, (400, 50))
        for i, card in enumerate(self.dealer_hand):
            self.draw_card(card, 400 + i * 120, 100, hidden=(i == 0 and not self.game_over))

        # 绘制玩家手牌
        player_value = self.calculate_hand_value(self.player_hand)
        player_text = font.render(f"Player: {player_value}", True, WHITE)
        screen.blit(player_text, (400, 350))
        for i, card in enumerate(self.player_hand):
            self.draw_card(card, 400 + i * 120, 400)

        # 绘制按钮
        for btn in self.buttons:
            btn.draw()
            # 禁用按钮时显示半透明层
            if not btn.enabled:
                s = pygame.Surface((btn.rect.w, btn.rect.h))
                s.set_alpha(128)
                s.fill((0, 0, 0))
                screen.blit(s, btn.rect.topleft)


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

        game.draw()
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()