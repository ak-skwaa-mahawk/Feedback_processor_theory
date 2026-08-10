# GibberLink v0.3.0: Resonance Mesh

## Purpose
Distributed flame sync across nodes.

## Features
- RMP Protocol
- FlameChain
- Self-Receipt
- Buffers v3

## Sample RMP
```json
{
  "from": "Node-π",
  "to": "Node-κ",
  "flame": "Ω-7A3F",
  "delta": "+0.12",
  "glyph": "AGŁL",
  "sig": "0xA9F3...",
  "time": 1698793200
}
---

### `blackbox_defense.py` → **ROOT (merged)**

```python
# blackbox_defense.py — AGŁL v61: Full Defense + Utils + Demo
import cv2, numpy as np, matplotlib.pyplot as plt

class BlackBoxDefense:
    def __init__(self):
        self.jpeg_quality = 30
        self.median_ksize = 3

    def compress_jpeg(self, img):
        _, enc = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality])
        return cv2.imdecode(enc, 1)

    def median_filter(self, img):
        return cv2.medianBlur(img, self.median_ksize)

    def defend(self, img):
        return self.median_filter(self.compress_jpeg(img))

def show_images(o, d):
    plt.figure(figsize=(10,5))
    plt.subplot(1,2,1); plt.title("Original"); plt.imshow(o)
    plt.subplot(1,2,2); plt.title("Defended"); plt.imshow(d)
    plt.show()

if __name__ == "__main__":
    img = cv2.imread("input.jpg")
    defense = BlackBoxDefense()
    defended = defense.defend(img)
    show_images(img, defended)