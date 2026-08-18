from pathlib import Path

OUT_SVG = Path(__file__).parent.parent / "info-card.svg"

def make_info_card():
    width = 490
    height = 420

    rows = [
        ("USER", "javid@portfolio", "#F0B87E", True),
        ("SEPARATOR", "------------------------", "#475569", False),
        ("OS", "Ubuntu 24.04 LTS (AWS EC2 Production)", "#E2E8F0", False),
        ("HOST", "mohamedjavid.dev (Live Next.js + FastAPI)", "#38BDF8", False),
        ("UPTIME", "3rd Year B.Tech IT (SNS College • CGPA 8.47)", "#E2E8F0", False),
        ("ROLE", "AI & Automation Intern @ Kauvery Hospitals", "#4ADE80", False),
        ("SPECIALTY", "Multi-Agent Graphs, GraphRAG, Web Scraping", "#F0B87E", False),
        ("AGENTIC", "LangGraph, Model Context Protocol (MCP), CrewAI", "#E2E8F0", False),
        ("SCRAPING", "Playwright, Scrapy, BeautifulSoup, Selenium", "#E2E8F0", False),
        ("STACK", "Python 3.11+, Next.js 16, React 19, TypeScript", "#E2E8F0", False),
        ("CLOUD/DB", "PostgreSQL, MongoDB, FAISS, Docker, Nginx, AWS", "#E2E8F0", False),
        ("AWARDS", "GDG Delhi Winner • AI Agentathon 4th • AMD Slingshot", "#FBBF24", False),
        ("CONTACT", "connectjavid27@gmail.com • in/javidsiast", "#94A3B8", False),
    ]

    svg_rows = []
    y_start = 68
    y_step = 24

    for idx, (label, val, val_color, is_title) in enumerate(rows):
        y = y_start + idx * y_step
        delay = 120 + idx * 70 # ms

        if label == "SEPARATOR":
            svg_rows.append(
                f'<text x="24" y="{y}" class="row" style="animation-delay: {delay}ms; fill: {val_color};">{val}</text>'
            )
        elif is_title:
            svg_rows.append(
                f'<text x="24" y="{y}" class="row user-title" style="animation-delay: {delay}ms;">'
                f'<tspan fill="#F0B87E">{label}: </tspan>'
                f'<tspan fill="#FFFFFF" font-weight="700">{val}</tspan>'
                f'</text>'
            )
        else:
            svg_rows.append(
                f'<text x="24" y="{y}" class="row" style="animation-delay: {delay}ms;">'
                f'<tspan fill="#64748B" font-weight="600">{label:<10}</tspan> '
                f'<tspan fill="{val_color}">{val}</tspan>'
                f'</text>'
            )

    # Color block palette
    palette_colors = ["#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6", "#F0B87E", "#F8FAFC"]
    palette_svg = []
    px_start = 24
    py_start = height - 26
    for i, c in enumerate(palette_colors):
        palette_svg.append(f'<rect x="{px_start + i * 26}" y="{py_start}" width="20" height="12" rx="3" fill="{c}"/>')

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="info-card">
  <defs>
    <style>
      .info-card {{
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
      .row {{
        font-size: 11.5px;
        opacity: 0;
        transform: translateY(6px);
        animation: rowFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      .user-title {{
        font-size: 13.5px;
      }}
      @keyframes rowFadeIn {{
        0% {{
          opacity: 0;
          transform: translateY(6px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
    </style>
  </defs>

  <!-- Card Background -->
  <rect width="100%" height="100%" rx="16" fill="#0B0F19" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1"/>

  <!-- Terminal Window Bar -->
  <circle cx="24" cy="24" r="4.5" fill="#EF4444" opacity="0.8"/>
  <circle cx="39" cy="24" r="4.5" fill="#F59E0B" opacity="0.8"/>
  <circle cx="54" cy="24" r="4.5" fill="#10B981" opacity="0.8"/>
  <text x="74" y="28" class="terminal-bar">neofetch --profile</text>

  <!-- Neofetch Rows -->
  {''.join(svg_rows)}

  <!-- Terminal Color Palette Bar -->
  {''.join(palette_svg)}
</svg>"""

    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[OK] Generated {OUT_SVG} ({width}x{height})")

if __name__ == "__main__":
    make_info_card()
