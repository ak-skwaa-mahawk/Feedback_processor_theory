# blackbox_defense_demo.py — Demo Script
import cv2
from blackbox_defense_defense import BlackBoxDefense
from blackbox_defense_utils import show_images

def main():
    img = cv2.imread("examples/input.jpg")
    defense = BlackBoxDefense()
    defended = defense.defend(img)
    show_images(img, defended)

if __name__ == "__main__":
    main()