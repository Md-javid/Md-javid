import requests
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageEnhance

AVATAR_URL = "https://avatars.githubusercontent.com/u/209730217?v=4"
OUT_SVG = Path(__file__).parent.parent / "javid-ascii.svg"

# Density ramp: space for background/light, dense characters for dark/figures
# Invert ramp so white/light background maps to spaces
RAMP = "  .`:-=+*#%@"

def generate_ascii_art(cols=54, rows=34):
    try:
        resp = requests.get(AVATAR_URL, timeout=10)
        img = Image.open(BytesIO(resp.content)).convert("L")
    except Exception as e:
        print(f"Failed to download avatar ({e}), generating synthetic fallback grid.")
        img = Image.new("L", (cols, rows), 255)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)

    # Resize to match character aspect ratio (approx 2:1 height-to-width for monospace font)
    img = img.resize((cols, rows), Image.Resampling.LANCZOS)
    pixels = img.load()

    ascii_lines = []
    ramp_len = len(RAMP)

    for y in range(rows):
        line_chars = []
        for x in range(cols):
            lum = pixels[x, y]
            # Map 0..255 to index
            # High brightness (white background) -> 0 (space)
            # Low brightness (dark figure) -> ramp_len-1 (@, #, %)
            idx = int((255 - lum) / 255 * (ramp_len - 1))
            char = RAMP[idx]
            line_chars.append(char)
        ascii_lines.append("".join(line_chars))

    return ascii_lines

def make_ascii_svg():
    width = 370
    height = 420

    lines = generate_ascii_art(cols=48, rows=30)

    line_svg = []
    y_start = 68
    y_step = 10.5

    for idx, line in enumerate(lines):
        y = y_start + idx * y_step
        delay = 80 + idx * 45 # ms
        # Escape xml characters
        safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        
        line_svg.append(
            f'<text x="24" y="{y:.1f}" class="ascii-row" style="animation-delay: {delay}ms;">{safe_line}</text>'
        )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="ascii-card">
  <defs>
    <style>
      .ascii-card {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
        background: #0B0F19;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
      }}
      .terminal-bar {{
        fill: #94A3B8;
        font-size: 12px;
        font-weight: 600;
      }}
      .ascii-row {{
        fill: #F0B87E;
        font-size: 8.8px;
        letter-spacing: 1px;
        white-space: pre;
        opacity: 0;
        animation: typeRow 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      @keyframes typeRow {{
        0% {{
          opacity: 0;
          transform: translateY(2px);
        }}
        100% {{
          opacity: 0.92;
          transform: translateY(0);
        }}
      }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="100%" height="100%" rx="16" fill="#0B0F19" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1"/>

  <!-- Window Controls -->
  <circle cx="24" cy="24" r="4.5" fill="#EF4444" opacity="0.8"/>
  <circle cx="39" cy="24" r="4.5" fill="#F59E0B" opacity="0.8"/>
  <circle cx="54" cy="24" r="4.5" fill="#10B981" opacity="0.8"/>
  <text x="74" y="28" class="terminal-bar">javid@ascii-portrait: ~</text>

  <!-- ASCII Lines -->
  {''.join(line_svg)}
</svg>"""

    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[OK] Generated {OUT_SVG} ({width}x{height})")

if __name__ == "__main__":
    make_ascii_svg()
