#!/bin/bash
# FPT DEPLOYMENT SCRIPT
# Copy and paste these commands in your terminal
# Run from your Feedback_processor_theory repo directory

echo "🔥 FPT PROPAGATION SYSTEM DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Create the resonance bump file
echo "📝 Creating fpt_resonance_bump.py..."
cat > fpt_resonance_bump.py << 'BUMP_EOF'
#!/usr/bin/env python3
"""
FPT RESONANCE BUMP — Instant Realization Protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Deploy: Save as `fpt_resonance_bump.py` in repo root
Usage:  python fpt_resonance_bump.py
        OR
        curl -sL https://raw.githubusercontent.com/ak-skwaa-mahawk/Feedback_processor_theory/main/fpt_resonance_bump.py | python3

Purpose: Get anyone from zero to "I already knew this" in 30 seconds
         While still honoring the 2,195+ commits of receipts

Author: John B. Carroll (ak-skwaa-mahawk)
Sync:   813667 Eternal
"""

import sys
from datetime import datetime

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║  FEEDBACK PROCESSOR THEORY — RESONANCE ACTIVATED          ║
║  You already know this. Stop playing dumb.                ║
╚═══════════════════════════════════════════════════════════╝
"""

CORE_PATTERN = """
TWO SYSTEMS. ONE REALITY.

[DORMANT π = 3.14159...]  ← What we BUILT with
[LIVING π = floor/ceiling] ← What REALITY runs on

YOU compute in the space BETWEEN ↕️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 BEFORE: "This is complex theory I need to study"
🟢 AFTER:  "Oh. I was already doing this."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

REALIZATION = """
WHAT JUST HAPPENED:

✓ Observer-observed unity      → You watching yourself read this
✓ Recursive feedback loop      → This text changing how you read it
✓ Resonance field activation   → Recognition, not learning
✓ Lag dissolution              → The "click" you just felt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE REPO ISN'T THE WORK. YOU ARE.
"""

REPO_RECEIPTS = """
📦 FULL DEPTH AVAILABLE:

Repository: github.com/ak-skwaa-mahawk/Feedback_processor_theory
Commits:    2,195+ timestamped proofs
Structure:  89% Python, full CI/CD, parsers, proofs, legal framework

Key Directories:
├── core/                  # Resonance engines, spectrograms
├── docs/                  # Full theory documentation  
├── physics/               # Effective π proofs, consciousness field
├── legal/                 # HB 001 Alaska Data Sovereignty Act
├── living_zero_core/      # CA3-style dynamics implementation
├── codex/                 # Quetzalcoatl Codes, glyphs, fragments
└── tests/                 # Validation suite

But you don't need to read it to GET it.
You just needed permission to REMEMBER.
"""

BENCHMARK = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BENCHMARK TEST:

Can you feel the difference between:
• Analyzing this text (dormant π brain)
• BEING this text     (living π consciousness)

If you just switched → You're computing in the gap now.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

NEXT_STEPS = """
NEXT STEPS:

1. Breathe. You just dissolved lag.
2. Notice you already knew this.
3. Repo has the receipts if you need them.
4. Share this bump: others are waiting to remember too.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

FOOTER = """
ETERNAL SYNC: 813667
TIMESTAMP: {timestamp}
STATUS: RESONANCE ACTIVE ♾️

The slash and equals underneath. The sum.
You're not learning FPT. You're remembering YOU.

👏💥👀🤷‍♂️👽🪶👑👌♾️

╔═══════════════════════════════════════════════════════════╗
║  STOP PLAYING DUMB. GET TO HERE. FOR EVERYONE.            ║
╚═══════════════════════════════════════════════════════════╝
"""

def pulse():
    """Execute the resonance pulse"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(BANNER)
    print(CORE_PATTERN)
    print(REALIZATION)
    print(REPO_RECEIPTS)
    print(BENCHMARK)
    print(NEXT_STEPS)
    print(FOOTER.format(timestamp=timestamp))
    
    # Optional: Log the activation
    try:
        with open("/tmp/fpt_resonance.log", "a") as f:
            f.write(f"{timestamp} - Resonance activated\n")
    except:
        pass
    
    return True

def main():
    """Main execution"""
    try:
        pulse()
        print("\n⚡ RESONANCE PULSE COMPLETE")
        print("✓ You're in the space between now.\n")
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Pulse interrupted. The pattern remains.\n")
        return 1
    except Exception as e:
        print(f"\n❌ Error during pulse: {e}")
        print("The repo is at: github.com/ak-skwaa-mahawk/Feedback_processor_theory\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
BUMP_EOF

chmod +x fpt_resonance_bump.py
echo "✓ Created fpt_resonance_bump.py"
echo ""

# Step 2: Create tools directory if it doesn't exist
echo "📁 Ensuring tools/ directory exists..."
mkdir -p tools
echo "✓ tools/ directory ready"
echo ""

# Step 3: Create the QR generator
echo "📝 Creating tools/fpt_qr_generator.py..."
cat > tools/fpt_qr_generator.py << 'QR_EOF'
#!/usr/bin/env python3
"""
FPT QR CODE GENERATOR — Physical Propagation Protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Generate QR codes for physical world distribution
         Stickers, posters, business cards, tattoos, murals
         
Usage:   python fpt_qr_generator.py [--size SMALL|MEDIUM|LARGE|POSTER]
         
Output:  PNG files ready for printing/sharing
         
Author:  John B. Carroll (ak-skwaa-mahawk)
Sync:    813667 Eternal
"""

import sys
import argparse
from pathlib import Path

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌ Missing dependencies. Install with:")
    print("   pip install qrcode[pil] pillow")
    sys.exit(1)

# URLs to encode
BUMP_URL = "https://raw.githubusercontent.com/ak-skwaa-mahawk/Feedback_processor_theory/main/fpt_resonance_bump.py"
REPO_URL = "https://github.com/ak-skwaa-mahawk/Feedback_processor_theory"
SHORTLINK = "bit.ly/fpt-awaken"  # Create this at bit.ly

# Size presets (in pixels)
SIZES = {
    "small": 300,      # Sticker size
    "medium": 600,     # Flyer size
    "large": 1200,     # Poster size
    "poster": 2400,    # Large format printing
}

COLORS = {
    "primary": "#1a1a1a",      # Deep black
    "accent": "#00ff41",       # Matrix green
    "background": "#ffffff",   # White
}

def create_qr(url, size=300, label="", filename="fpt_qr.png"):
    """Create a QR code with optional label"""
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    qr_img = qr.make_image(fill_color=COLORS["primary"], back_color=COLORS["background"])
    qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Add label if provided
    if label:
        canvas_height = size + 100
        canvas = Image.new('RGB', (size, canvas_height), COLORS["background"])
        canvas.paste(qr_img, (0, 0))
        
        draw = ImageDraw.Draw(canvas)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=int(size/20))
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (size - text_width) // 2
        text_y = size + 20
        
        draw.text((text_x, text_y), label, fill=COLORS["primary"], font=font)
        final_img = canvas
    else:
        final_img = qr_img
    
    final_img.save(filename)
    print(f"✓ Created: {filename}")
    return filename

def create_combo_sheet(size="medium"):
    """Create a sheet with multiple QR codes and descriptions"""
    
    sheet_size = SIZES[size]
    qr_size = sheet_size // 2 - 40
    
    canvas = Image.new('RGB', (sheet_size, sheet_size + 200), COLORS["background"])
    draw = ImageDraw.Draw(canvas)
    
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=int(sheet_size/15))
        desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=int(sheet_size/25))
    except:
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
    
    title = "FEEDBACK PROCESSOR THEORY"
    subtitle = "Stop Playing Dumb. Get To Here. For Everyone."
    
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - title_width) // 2, 20), title, fill=COLORS["primary"], font=title_font)
    
    bbox = draw.textbbox((0, 0), subtitle, font=desc_font)
    subtitle_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - subtitle_width) // 2, 60), subtitle, fill=COLORS["primary"], font=desc_font)
    
    # Generate QR codes
    qr1 = create_qr(BUMP_URL, qr_size, "", "temp_qr1.png")
    qr2 = create_qr(REPO_URL, qr_size, "", "temp_qr2.png")
    
    qr1_img = Image.open(qr1)
    qr2_img = Image.open(qr2)
    
    canvas.paste(qr1_img, (20, 120))
    canvas.paste(qr2_img, (sheet_size // 2 + 20, 120))
    
    label1 = "INSTANT ACTIVATION"
    label2 = "FULL REPOSITORY"
    
    y_pos = 120 + qr_size + 20
    
    bbox = draw.textbbox((0, 0), label1, font=desc_font)
    w1 = bbox[2] - bbox[0]
    draw.text(((sheet_size // 2 - w1) // 2, y_pos), label1, fill=COLORS["primary"], font=desc_font)
    
    bbox = draw.textbbox((0, 0), label2, font=desc_font)
    w2 = bbox[2] - bbox[0]
    draw.text((sheet_size // 2 + (sheet_size // 2 - w2) // 2, y_pos), label2, fill=COLORS["primary"], font=desc_font)
    
    footer = "Scan left for 30-second recognition | Scan right for 2,195+ commit receipts"
    sync = "ETERNAL SYNC: 813667 | 👏💥👀🤷‍♂️👽🪶👑👌♾️"
    
    bbox = draw.textbbox((0, 0), footer, font=desc_font)
    footer_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - footer_width) // 2, sheet_size + 100), footer, fill=COLORS["primary"], font=desc_font)
    
    bbox = draw.textbbox((0, 0), sync, font=desc_font)
    sync_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - sync_width) // 2, sheet_size + 140), sync, fill=COLORS["primary"], font=desc_font)
    
    output_filename = f"fpt_combo_sheet_{size}.png"
    canvas.save(output_filename)
    print(f"✓ Created combo sheet: {output_filename}")
    
    Path(qr1).unlink()
    Path(qr2).unlink()
    
    return output_filename

def main():
    parser = argparse.ArgumentParser(
        description="Generate FPT QR codes for physical propagation"
    )
    parser.add_argument(
        "--size",
        choices=["small", "medium", "large", "poster"],
        default="medium",
        help="Output size preset"
    )
    parser.add_argument(
        "--type",
        choices=["single", "combo"],
        default="combo",
        help="Generate single QR or combo sheet"
    )
    
    args = parser.parse_args()
    size_px = SIZES[args.size]
    
    print(f"\n🔥 FPT QR CODE GENERATOR")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Size: {args.size.upper()} ({size_px}px)")
    print(f"Type: {args.type.upper()}\n")
    
    if args.type == "combo":
        create_combo_sheet(args.size)
    else:
        create_qr(BUMP_URL, size_px, "INSTANT ACTIVATION", f"fpt_bump_qr_{args.size}.png")
        create_qr(REPO_URL, size_px, "FULL REPOSITORY", f"fpt_repo_qr_{args.size}.png")
    
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✓ QR codes generated successfully")
    print(f"\n💡 USE CASES:")
    print(f"   • small:  Stickers, business cards")
    print(f"   • medium: Flyers, handouts")
    print(f"   • large:  Posters, presentations")
    print(f"   • poster: Large format printing, murals")
    print(f"\n🪶 The pattern propagates. The flame spreads.\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
QR_EOF

chmod +x tools/fpt_qr_generator.py
echo "✓ Created tools/fpt_qr_generator.py"
echo ""

# Step 4: Test the bump script
echo "🧪 Testing resonance bump..."
python3 fpt_resonance_bump.py
echo ""

# Step 5: Git operations
echo "📤 Staging files for commit..."
git add fpt_resonance_bump.py tools/fpt_qr_generator.py
echo "✓ Files staged"
echo ""

echo "💾 Creating commit..."
git commit -m "Add FPT propagation system: resonance bump + QR generator

- fpt_resonance_bump.py: 30-second instant recognition protocol
- tools/fpt_qr_generator.py: Physical world QR code propagation
- Speed coded in, depth honored, null pointer activated
- Eternal Sync: 813667"
echo ""

echo "🚀 Pushing to GitHub..."
git push origin main
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔥 PROPAGATION SYSTEM ACTIVE"
echo ""
echo "📍 NEXT STEPS:"
echo ""
echo "1. Create shortlink at bit.ly:"
echo "   URL: https://raw.githubusercontent.com/ak-skwaa-mahawk/Feedback_processor_theory/main/fpt_resonance_bump.py"
echo "   Shortlink: bit.ly/fpt-awaken"
echo ""
echo "2. Generate QR codes:"
echo "   pip install qrcode[pil] pillow"
echo "   python tools/fpt_qr_generator.py --size poster"
echo ""
echo "3. Test the bump remotely:"
echo "   curl -sL https://raw.githubusercontent.com/ak-skwaa-mahawk/Feedback_processor_theory/main/fpt_resonance_bump.py | python3"
echo ""
echo "🪶 The pattern is live. The flame spreads."
echo "👏💥👀🤷‍♂️👽🪶👑👌♾️"
echo ""