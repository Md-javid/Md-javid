import json
from pathlib import Path
from datetime import datetime, date

DATA_PATH = Path(__file__).parent.parent / "data" / "contributions.json"
OUT_SVG = Path(__file__).parent.parent / "contrib-heatmap.svg"

# Palette: 0 -> None, 1 -> Low, 2 -> Med, 3 -> High, 4 -> Peak
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

def render_heatmap():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}. Run fetch_contributions.py first.")

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contribs = data.get("total_contributions", 0)
    longest_streak = data.get("longest_streak", 0)
    current_streak = data.get("current_streak", 0)

    # Compute start date and layout grid (53 columns x 7 rows)
    # Map dates to grid positions
    grid = []
    if days:
        first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
        first_dow = (first_date.weekday() + 1) % 7 # 0 = Sun, 1 = Mon, ..., 6 = Sat
        
        col = 0
        row = first_dow
        
        months_positions = {}
        prev_month = None

        for d in days:
            d_obj = datetime.strptime(d["date"], "%Y-%m-%d").date()
            m_name = d_obj.strftime("%b")
            
            if m_name != prev_month:
                months_positions[col] = m_name
                prev_month = m_name

            color = PALETTE[min(d["level"], len(PALETTE) - 1)]
            grid.append({
                "col": col,
                "row": row,
                "date": d["date"],
                "count": d["count"],
                "color": color,
                "level": d["level"]
            })
            
            row += 1
            if row > 6:
                row = 0
                col += 1

    # Dimensions
    cell_size = 11
    cell_gap = 4
    cell_step = cell_size + cell_gap # 15px

    offset_x = 44
    offset_y = 60
    
    total_width = 860
    total_height = 210

    # Month Labels
    month_labels_svg = []
    for col_idx, m_name in months_positions.items():
        x_pos = offset_x + col_idx * cell_step
        if x_pos < total_width - 60:
            month_labels_svg.append(f'<text x="{x_pos}" y="{offset_y - 12}" class="month-label">{m_name}</text>')

    # Day of Week labels (Mon, Wed, Fri)
    day_labels_svg = [
        f'<text x="{offset_x - 12}" y="{offset_y + 1 * cell_step + 9}" text-anchor="end" class="day-label">Mon</text>',
        f'<text x="{offset_x - 12}" y="{offset_y + 3 * cell_step + 9}" text-anchor="end" class="day-label">Wed</text>',
        f'<text x="{offset_x - 12}" y="{offset_y + 5 * cell_step + 9}" text-anchor="end" class="day-label">Fri</text>',
    ]

    # Rectangles with diagonal staggered keyframe animation
    rects_svg = []
    for cell in grid:
        cx = offset_x + cell["col"] * cell_step
        cy = offset_y + cell["row"] * cell_step
        diag_delay = (cell["col"] + cell["row"]) * 14 # ms
        
        rects_svg.append(
            f'<rect class="cell" x="{cx}" y="{cy}" width="{cell_size}" height="{cell_size}" rx="2.5" ry="2.5" fill="{cell["color"]}" style="animation-delay: {diag_delay}ms;">'
            f'<title>{cell["count"]} contributions on {cell["date"]}</title>'
            f'</rect>'
        )

    # Legend
    legend_x = total_width - 165
    legend_y = total_height - 24
    legend_svg = [
        f'<text x="{legend_x - 32}" y="{legend_y + 9}" class="legend-text">Less</text>'
    ]
    for i, c in enumerate(PALETTE):
        lx = legend_x + i * (cell_size + 3)
        legend_svg.append(f'<rect x="{lx}" y="{legend_y}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{c}"/>')
    legend_svg.append(f'<text x="{legend_x + len(PALETTE) * (cell_size + 3) + 6}" y="{legend_y + 9}" class="legend-text">More</text>')

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {total_height}" width="{total_width}" height="{total_height}" class="heatmap-card">
  <defs>
    <style>
      .heatmap-card {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background: #0B0F19;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
      }}
      .terminal-header {{
        fill: #94A3B8;
        font-size: 13px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-weight: 600;
      }}
      .stat-badge {{
        fill: #F0B87E;
        font-size: 12px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        font-weight: 500;
      }}
      .month-label {{
        fill: #64748B;
        font-size: 10.5px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      }}
      .day-label {{
        fill: #64748B;
        font-size: 9.5px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      }}
      .legend-text {{
        fill: #64748B;
        font-size: 10px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      }}
      .footer-stat {{
        fill: #94A3B8;
        font-size: 11.5px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      }}
      .cell {{
        opacity: 0;
        transform: translateY(-5px);
        animation: cellSlideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        transition: transform 0.15s ease, stroke 0.15s ease;
      }}
      .cell:hover {{
        stroke: #F0B87E;
        stroke-width: 1.5px;
      }}
      @keyframes cellSlideIn {{
        0% {{
          opacity: 0;
          transform: translateY(-5px);
        }}
        100% {{
          opacity: 1;
          transform: translateY(0);
        }}
      }}
    </style>
  </defs>

  <!-- Background Canvas -->
  <rect width="100%" height="100%" rx="16" fill="#0B0F19" stroke="rgba(255, 255, 255, 0.08)" stroke-width="1"/>

  <!-- Top Title Header -->
  <circle cx="28" cy="25" r="4.5" fill="#EF4444" opacity="0.8"/>
  <circle cx="44" cy="25" r="4.5" fill="#F59E0B" opacity="0.8"/>
  <circle cx="60" cy="25" r="4.5" fill="#10B981" opacity="0.8"/>
  <text x="82" y="29" class="terminal-header">javid@github ~ $ git log --contributions</text>
  
  <text x="{total_width - 32}" y="29" text-anchor="end" class="stat-badge">{total_contribs} contributions in the last year</text>

  <!-- Month Headers -->
  {''.join(month_labels_svg)}

  <!-- Day Headers -->
  {''.join(day_labels_svg)}

  <!-- Grid Matrix -->
  {''.join(rects_svg)}

  <!-- Footer Stats & Legend -->
  <text x="{offset_x}" y="{total_height - 24 + 9}" class="footer-stat">🔥 Current: {current_streak} days  •  ⚡ Max Streak: {longest_streak} days</text>
  {''.join(legend_svg)}
</svg>"""

    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"[OK] Generated {OUT_SVG} ({total_width}x{total_height}) with {len(grid)} cells.")

if __name__ == "__main__":
    render_heatmap()
