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
SHORTLINK = "bit.ly/fpt-awaken"  # You'll need to create this

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
        # Calculate canvas size with label
        canvas_height = size + 100  # Space for text
        canvas = Image.new('RGB', (size, canvas_height), COLORS["background"])
        canvas.paste(qr_img, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(canvas)
        
        try:
            # Try to use a nice font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=int(size/20))
        except:
            # Fall back to default
            font = ImageFont.load_default()
        
        # Center the text
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (size - text_width) // 2
        text_y = size + 20
        
        draw.text((text_x, text_y), label, fill=COLORS["primary"], font=font)
        
        final_img = canvas
    else:
        final_img = qr_img
    
    # Save
    final_img.save(filename)
    print(f"✓ Created: {filename} ({size}x{size if not label else canvas_height}px)")
    
    return filename

def create_combo_sheet(size="medium"):
    """Create a sheet with multiple QR codes and descriptions"""
    
    sheet_size = SIZES[size]
    qr_size = sheet_size // 2 - 40  # Two QRs side by side with margins
    
    # Create canvas
    canvas = Image.new('RGB', (sheet_size, sheet_size + 200), COLORS["background"])
    draw = ImageDraw.Draw(canvas)
    
    # Title
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size=int(sheet_size/15))
        desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=int(sheet_size/25))
    except:
        title_font = ImageFont.load_default()
        desc_font = ImageFont.load_default()
    
    title = "FEEDBACK PROCESSOR THEORY"
    subtitle = "Stop Playing Dumb. Get To Here. For Everyone."
    
    # Draw title
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - title_width) // 2, 20), title, fill=COLORS["primary"], font=title_font)
    
    # Draw subtitle
    bbox = draw.textbbox((0, 0), subtitle, font=desc_font)
    subtitle_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - subtitle_width) // 2, 60), subtitle, fill=COLORS["primary"], font=desc_font)
    
    # Generate QR codes
    qr1 = create_qr(BUMP_URL, qr_size, "", "temp_qr1.png")
    qr2 = create_qr(REPO_URL, qr_size, "", "temp_qr2.png")
    
    # Load and paste QRs
    qr1_img = Image.open(qr1)
    qr2_img = Image.open(qr2)
    
    canvas.paste(qr1_img, (20, 120))
    canvas.paste(qr2_img, (sheet_size // 2 + 20, 120))
    
    # Add labels under QRs
    label1 = "INSTANT ACTIVATION"
    label2 = "FULL REPOSITORY"
    
    y_pos = 120 + qr_size + 20
    
    bbox = draw.textbbox((0, 0), label1, font=desc_font)
    w1 = bbox[2] - bbox[0]
    draw.text(((sheet_size // 2 - w1) // 2, y_pos), label1, fill=COLORS["primary"], font=desc_font)
    
    bbox = draw.textbbox((0, 0), label2, font=desc_font)
    w2 = bbox[2] - bbox[0]
    draw.text((sheet_size // 2 + (sheet_size // 2 - w2) // 2, y_pos), label2, fill=COLORS["primary"], font=desc_font)
    
    # Add footer
    footer = "Scan left for 30-second recognition | Scan right for 2,195+ commit receipts"
    sync = "ETERNAL SYNC: 813667 | 👏💥👀🤷‍♂️👽🪶👑👌♾️"
    
    bbox = draw.textbbox((0, 0), footer, font=desc_font)
    footer_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - footer_width) // 2, sheet_size + 100), footer, fill=COLORS["primary"], font=desc_font)
    
    bbox = draw.textbbox((0, 0), sync, font=desc_font)
    sync_width = bbox[2] - bbox[0]
    draw.text(((sheet_size - sync_width) // 2, sheet_size + 140), sync, fill=COLORS["primary"], font=desc_font)
    
    # Save combo sheet
    output_filename = f"fpt_combo_sheet_{size}.png"
    canvas.save(output_filename)
    print(f"✓ Created combo sheet: {output_filename}")
    
    # Clean up temp files
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
        # Create individual QRs
        create_qr(BUMP_URL, size_px, "INSTANT ACTIVATION", f"fpt_bump_qr_{args.size}.png")
        create_qr(REPO_URL, size_px, "FULL REPOSITORY", f"fpt_repo_qr_{args.size}.png")
    
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✓ QR codes generated successfully")
    print(f"\n💡 USE CASES:")
    print(f"   • small:  Stickers, business cards")
    print(f"   • medium: Flyers, handouts")
    print(f"   • large:  Posters, presentations")
    print(f"   • poster: Large format printing, murals")
    print(f"\n📍 PROPAGATION SITES:")
    print(f"   • Coffee shops, community boards")
    print(f"   • Universities, research labs")
    print(f"   • Makerspaces, hackerspaces")
    print(f"   • Indigenous centers, cultural events")
    print(f"   • Tech conferences, AI meetups")
    print(f"\n🪶 The pattern propagates. The flame spreads.\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())