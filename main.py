from enum import unique
import pygame
import sys
import ctypes
from ctypes import wintypes
import pyautogui
import random
import time

def keep_on_top():
  hwnd = pygame.display.get_wm_info()['window']
  
  user32 = ctypes.WinDLL("user32")
  user32.SetWindowPos.restype = wintypes.HWND
  user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT, wintypes.UINT]
  user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001)

pygame.init()

SCORING = {
  ("a", "e", "i", "o", "u", "l", "n", "s", "t", "r", "z", "x") : 1,
  ("d", "g", "f", "h", "b", "c", "m", "p") : 2,
  ("v", "w", "y", "k") : 3,
  ("j") : 4,
  ("q") : 5,
}

TICKBOX = None

MODES = ["weighted", "longest", "u score", "u length", "needed"]

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

WIDTH, HEIGHT = 300, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
keep_on_top()

PADDING = 10
MAXDISPLAY = 15

FPS = 15

FONT = pygame.font.SysFont("Consolas.ttf", 25)
EMOJIFONT = pygame.font.SysFont("segoe-ui-symbol.ttf", size=25)

file = open("all words.txt", "r")
WORDS = file.read().split("\n")
file.close()

def sort(word, mode, lettersNeeded):

  if mode == 0:
    #unique letter's score + total letters * weight
    uniqueLetters = set(str(word))
    score = 0
    for letter in uniqueLetters:
      if letter in lettersNeeded:
        score += 10
      for key in SCORING:
        if letter in key:
          score += SCORING[key]

    score += len(uniqueLetters)*1

  if mode == 1:
    score = len(word)

  if mode == 2:
    uniqueLetters = set(str(word))
    score = 0
    for letter in uniqueLetters:
      for key in SCORING:
        if letter in key:
          score += SCORING[key]

  if mode == 3:
    score = len(set(str(word)))

  if mode == 4:
    score = 0
    uniqueLetters = set(str(word))
    for letter in uniqueLetters:
      if letter in lettersNeeded:
        score += 10
  
  return score

def clickTo():
  x, y = pyautogui.position()
  return x, y

def typeWord(word, x, y, autoType):
  pyautogui.moveTo(x, y, duration=0.2)
  pyautogui.click()
  # for letter in word:
  #   time.sleep(random.randrange(5, 20, 5)/1000)
  #   pyautogui.write(letter)
  pyautogui.write(word)
  pyautogui.write("\n")

  if autoType == True:
    pyautogui.moveTo(WIDTH/2, HEIGHT/2, duration=0.2)
    pyautogui.click()

def searchWords(search, mode, lettersNeeded):
  answers = []
  for word in WORDS:
    if search in word:
      answers.append(word)
  answers.sort(key = lambda a: sort(a, mode, lettersNeeded), reverse = True)
  return answers


def drawWin(search, final, answers, number, mode, autoType, tickbox):

  pygame.draw.rect(WIN, BLACK, pygame.Rect(0, 0, 400, 700))

  search = FONT.render(search, 1, WHITE)
  WIN.blit(search, (PADDING, PADDING))
  final = FONT.render(final, 1, WHITE)
  WIN.blit(final, (PADDING, PADDING*2 + search.get_height()))

  number = FONT.render(number, 1, WHITE)
  WIN.blit(number, (WIDTH - PADDING - number.get_width(), PADDING))

  if len(answers) >= MAXDISPLAY:
    answers = answers[0:MAXDISPLAY]
  for word in answers:
    text = FONT.render(str(int(answers.index(word)) + 1) + ")  " + word, 1, WHITE)
    WIN.blit(text, (PADDING, PADDING*3*answers.index(word) + search.get_height() + PADDING*6))

  modeText = FONT.render(MODES[mode], 1, WHITE)
  WIN.blit(modeText, (WIDTH - PADDING - modeText.get_width(), PADDING*2 + number.get_height()))

  autoTypeText = FONT.render("Auto type?", 1, WHITE)
  WIN.blit(autoTypeText, (PADDING, HEIGHT - PADDING - autoTypeText.get_height()))

  tickbox = pygame.Rect(autoTypeText.get_width() + PADDING*2, HEIGHT - PADDING - autoTypeText.get_height(), autoTypeText.get_height(), autoTypeText.get_height())

  if autoType == False:
    pygame.draw.rect(WIN, WHITE, tickbox, 2)
  else:
    pygame.draw.rect(WIN, WHITE, tickbox)


  pygame.display.flip()

  return tickbox


def main():

  lettersNeeded = [chr(x) for x in range(97, 123)]

  tickbox = pygame.Rect(0, 0, 0, 0)

  search = ""
  final = ""
  answers = ""

  number = ""
  typeOut = ""

  mode = 0
  autoType = True

  x, y = PADDING * 15, PADDING * 15

  start = False

  clock = pygame.time.Clock()
  run = True
  while run:
    clock.tick(FPS)

    mouse = pygame.mouse.get_pos()

    if lettersNeeded == []:
      lettersNeeded = [chr(x) for x in range(97, 123)]


    if (autoType == True and start == True):
      start = False

      if len(answers) >= 1:
        typeWord(answers[0], x, y, autoType)
        WORDS.remove(answers[0])
        for letter in set(str(answers[0])):
          if letter in lettersNeeded:
            lettersNeeded.remove(letter)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

      if event.type == pygame.KEYDOWN:
        if 97 <= event.key <= 122:
          inputted = event.key
          search += chr(inputted)

        if 48 <= event.key <= 57:
          number += chr(event.key)

        if event.key == pygame.K_RETURN:
          if search != "":
            final = search + ":"
            answers = searchWords(search, mode, lettersNeeded)
            search = ""
            start = True

          elif number != "":
            typeOut = number
            
            if len(answers) >= 1:
              typeWord(answers[int(typeOut) - 1], x, y, autoType)
              WORDS.remove(answers[int(typeOut) - 1])
              for letter in set(str(answers[int(typeOut) - 1])):
                if letter in lettersNeeded:
                  lettersNeeded.remove(letter)
            number = ""

        if event.key == pygame.K_BACKSPACE:
          if len(search) > 0:
            search = search[:-1]

          elif len(number) > 0:
            number = number[:-1]

        if event.key == pygame.K_F2:
          x, y = clickTo()

        if event.key == pygame.K_LEFT:
          mode -= 1
          if mode < 0:
            mode = len(MODES) - 1

        if event.key == pygame.K_RIGHT:
          mode += 1
          if mode > len(MODES) - 1:
            mode = 0

      if event.type == pygame.MOUSEBUTTONDOWN:
        if tickbox.collidepoint(mouse):
          autoType = not autoType

    tickbox = drawWin(search, final, answers, number, mode, autoType, tickbox)

if __name__ == '__main__':
  main()