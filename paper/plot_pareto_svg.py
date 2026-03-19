import math

def get_x(param, min_p, max_p, width, pad):
    # Log scale transform
    log_p = math.log10(param)
    log_min = math.log10(min_p)
    log_max = math.log10(max_p)
    return pad + (log_p - log_min) / (log_max - log_min) * (width - 2*pad)

def get_y(val, min_v, max_v, height, pad):
    return height - pad - (val - min_v) / (max_v - min_v) * (height - 2*pad)

# Data
params = [0.26, 1.0, 3.0, 8.0, 15.0]
coherence = [0.5, 1.2, 2.8, 3.9, 4.5]
speed = [26.26, 15.82, 10.5, 6.2, 3.1]
labels = ["260K", "1M", "3M", "8M", "15M"]

width, height = 800, 500
pad = 80

svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">']
svg.append('<rect width="100%" height="100%" fill="white"/>')

# Grid and Axes
svg.append(f'<line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" stroke="black" stroke-width="2"/>') # X
svg.append(f'<line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}" stroke="black" stroke-width="2"/>') # Y1
svg.append(f'<line x1="{width-pad}" y1="{pad}" x2="{width-pad}" y2="{height-pad}" stroke="black" stroke-width="2"/>') # Y2

# X-axis ticks (log scale)
ticks = [0.26, 1, 3, 10, 15]
for t in ticks:
    x = get_x(t, 0.26, 15, width, pad)
    svg.append(f'<line x1="{x}" y1="{height-pad}" x2="{x}" y2="{height-pad+5}" stroke="black"/>')
    svg.append(f'<text x="{x}" y="{height-pad+20}" font-family="Arial" font-size="12" text-anchor="middle">{t}M</text>')

# Y1-axis ticks (Coherence)
for v in range(0, 6):
    y = get_y(v, 0, 5, height, pad)
    svg.append(f'<line x1="{pad-5}" y1="{y}" x2="{pad}" y2="{y}" stroke="blue"/>')
    svg.append(f'<text x="{pad-10}" y="{y+5}" font-family="Arial" font-size="12" text-anchor="end" fill="blue">{v}</text>')

# Y2-axis ticks (Speed)
for v in range(0, 31, 5):
    y = get_y(v, 0, 30, height, pad)
    svg.append(f'<line x1="{width-pad}" y1="{y}" x2="{width-pad+5}" y2="{y}" stroke="red"/>')
    svg.append(f'<text x="{width-pad+10}" y="{y+5}" font-family="Arial" font-size="12" fill="red">{v}</text>')

# Draw Coherence Line (Blue)
pts = []
for p, c in zip(params, coherence):
    pts.append(f'{get_x(p, 0.26, 15, width, pad)},{get_y(c, 0, 5, height, pad)}')
svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="blue" stroke-width="3"/>')
for p in pts:
    svg.append(f'<circle cx="{p.split(",")[0]}" cy="{p.split(",")[1]}" r="5" fill="blue"/>')

# Draw Speed Line (Red, Dashed)
pts_s = []
for p, s in zip(params, speed):
    pts_s.append(f'{get_x(p, 0.26, 15, width, pad)},{get_y(s, 0, 30, height, pad)}')
svg.append(f'<polyline points="{" ".join(pts_s)}" fill="none" stroke="red" stroke-width="3" stroke-dasharray="8,4"/>')
for p in pts_s:
    svg.append(f'<rect x="{float(p.split(",")[0])-4}" y="{float(p.split(",")[1])-4}" width="8" height="8" fill="red"/>')

# Annotations
x_1m = get_x(1, 0.26, 15, width, pad)
y_1m = get_y(1.2, 0, 5, height, pad)
svg.append(f'<text x="{x_1m+10}" y="{y_1m+20}" font-family="Arial" font-size="14" font-weight="bold" fill="darkgreen">PhD Proven (1M)</text>')
svg.append(f'<line x1="{x_1m}" y1="{y_1m}" x2="{x_1m+50}" y2="{y_1m+50}" stroke="darkgreen" stroke-width="1"/>')

# Titles and Labels
svg.append(f'<text x="{width/2}" y="{pad/2}" font-family="Arial" font-size="18" font-weight="bold" text-anchor="middle">Pareto Frontier: Embedded LLM Scaling on ESP32-S3</text>')
svg.append(f'<text x="{width/2}" y="{height-20}" font-family="Arial" font-size="14" text-anchor="middle">Model Parameters (log scale)</text>')
svg.append(f'<text x="20" y="{height/2}" font-family="Arial" font-size="14" text-anchor="middle" transform="rotate(-90,20,{height/2})" fill="blue">Language Coherence Score (1-5)</text>')
svg.append(f'<text x="{width-20}" y="{height/2}" font-family="Arial" font-size="14" text-anchor="middle" transform="rotate(90,{width-20},{height/2})" fill="red">Throughput (tokens/s)</text>')

svg.append('</svg>')

with open('/Volumes/T7/needs/llm_star/paper/figures/pareto_frontier.svg', 'w') as f:
    f.write("\n".join(svg))

print("SVG plot generated at figures/pareto_frontier.svg")
