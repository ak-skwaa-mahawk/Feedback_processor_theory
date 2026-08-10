# blackbox_defense_utils.py — Helper Functions
import matplotlib.pyplot as plt

def show_images(original, defended):
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Original")
    plt.imshow(original)
    plt.subplot(1, 2, 2)
    plt.title("Defended")
    plt.imshow(defended)
    plt.show()