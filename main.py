from machine import Pin
import random

led = Pin(25, Pin.OUT)  # 確認用LED

"""
インデックス

[0, 1*2, 2*2, 3*2, 4*2, 5*2, 6*2, 7*2, 8*2, 9*2, DrawTwo*2, Reverse*2, Skip*2]
00 ~ 24: Red
25 ~ 49: Green
50 ~ 74: Yellow
75 ~ 99: Blue

100 ~ 103: Wild
104 ~ 107: WildDrawFour

状態
0: ひかれた
1: まだひかれていない
"""

def is_not_chosen(index: int):
  return index == 999

def index_to_num(index: int):
  num = int((index % 25 + 1) / 2)
  if index <= 99 and num <= 9:
    return num

def is_draw_two(index: int):
  return int((index % 25 + 1) / 2) == 10 and index <= 99

def is_reverse(index: int):
  return int((index % 25 + 1) / 2) == 11 and index <= 99

def is_skip(index: int):
  return int((index % 25 + 1) / 2) == 12 and index <= 99

def is_wild(index: int):
  return index >= 100 and index <= 103

def is_wild_draw_four(index: int):
  return index >= 104 and index <= 107

def index_to_color_and_name(index: int):
  color = ''
  name = ''
  
  if index <= 24:
    color = 'Red'
  elif index <= 49:
    color = 'Green'
  elif index <= 74:
    color = 'Yellow'
  elif index <= 99:
    color = 'Blue'

  if index_to_num(index) is not None:
    name = str(index_to_num(index))
  if is_draw_two(index):
    name = 'DrawTwo'
  if is_reverse(index):
    name = 'Reverse'
  if is_skip(index):
    name = 'Skip'
  if is_wild(index):
    name = 'Wild'
  if is_wild_draw_four(index):
    name = 'WildDrawFour'
  
  return color, name

def calc_next_player(current_player: int, total_players: int, direction: int, skip: bool = False):
  next_player = current_player + direction * (1 + int(skip))
  if direction == 1 and current_player + int(skip) + 1 >= total_players:  # 最初に戻す
    next_player = current_player + int(skip) + 1 - total_players
  if direction == -1 and current_player - int(skip) <= 0:  # 最後に戻す
    next_player = total_players - int(skip) - 1 + current_player
  return next_player

decks = [1] * 108

def pick_cards(count: int, start: int = 0, end: int = 107) -> list[int]:  # decksの状態を直接変える
  cards_picked = []
  while len(cards_picked) < count:
    card_picked = random.randint(start, end)
    if decks[card_picked]:
      cards_picked.append(card_picked)
      decks[card_picked] = 0  # カードをひく
  return cards_picked

total_players = int(input('How many players?: '))
hands_list = [pick_cards(7) for _ in range(total_players)]  # 人数分の手札を用意

current_color, current_name = index_to_color_and_name(pick_cards(1, 0, 99)[0])  # 最初はワイルドカード以外
current_player = 0  # 現在のプレーヤーのインデックス
direction = 1  # リバースしていない状態から開始
while True:
  print(f'Player{current_player} hands')
  for index, hand in enumerate(hands_list[current_player]):
    color, name = index_to_color_and_name(hand)
    print(f'{index}:  {color} {name}')
  print(f'Table card: {current_color} {current_name}')

  card_throwed = 999  # 何も選ばれていない状態
  next_color = ''
  next_name = ''
  while (
    not is_wild(card_throwed) and
    not is_wild_draw_four(card_throwed) and
    next_color != current_color and
    next_name != current_name  # 次に出せないカードなら
  ):
    card_chosen = int(input('Which card? (999: Pick a card): '))
    if is_not_chosen(card_chosen):
      break
    card_throwed = hands_list[current_player][card_chosen]
    next_color, next_name = index_to_color_and_name(card_throwed)
  while not next_color and next_name:  # ワイルドカードなら色を選ばせる
    color_chosen = input('Which color? Red, Green, Yellow, Blue: ').lower()  # すべて小文字にする
    if color_chosen in ['red', 'green', 'yellow', 'blue']:  # 入力したものの中に色があるかどうか
      next_color = color_chosen[0].upper() + color_chosen[1:]  # 最初の文字だけ大文字にする

  led.value(1)  # 処理の間LEDをつける

  direction *= -1 if is_reverse(card_throwed) else 1 # リバースカードが出されたなら
  
  next_player = calc_next_player(
    current_player,
    total_players,
    direction,  
    is_skip(card_throwed)  # スキップカードが出されたなら
  )

  # 次のプレーヤーにカードを加える
  if is_wild_draw_four(card_throwed):
    hands_list[next_player].extend(pick_cards(4))
  if is_draw_two(card_throwed):
    hands_list[next_player].extend(pick_cards(2))

  if is_not_chosen(card_throwed):  # カードを出さなかったら
    hands_list[current_player].extend(pick_cards(1))  # 手札に加える
    next_color = current_color  # 現在の場札を変えない
    next_name = current_name
  else:  # カードを出したなら
    index_card_throwed = hands_list[current_player].index(card_throwed)  # 捨てたカードのインデックスを調べる
    hands_list[current_player].pop(index_card_throwed)  # 手札から減らす

  # ゲームの判定
  if not hands_list[current_player]:  # 手札がなくなったプレーヤーが勝ち
    print(f'Player{current_player} won!')
    break
  if 1 not in decks:  # すべての山札がひかれたら終了
    print('Draw!')
    break

  current_color = next_color  # 場札を出された色にする
  current_name = next_name  # 場札を出されたカードにする
  current_player = next_player  # 次のプレーヤーにする

  led.value(0)  # LEDを消す
