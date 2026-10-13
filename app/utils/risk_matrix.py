"""
Risk Scoring Matrix and Helper Utilities
Based on Ontario Health / standard risk framework:
Likelihood (1-5) x Impact (1-5) -> Score (1-25) and Severity Label
"""

LIKELIHOOD_LEVELS = [
    {"value": 1, "name": "Remote", "label": "Remote (1)"},
    {"value": 2, "name": "Unlikely", "label": "Unlikely (2)"},
    {"value": 3, "name": "Possible", "label": "Possible (3)"},
    {"value": 4, "name": "Likely", "label": "Likely (4)"},
    {"value": 5, "name": "Virtually Certain", "label": "Virtually Certain (5)"},
]

IMPACT_LEVELS = [
    {"value": 1, "name": "Insignificant", "label": "Insignificant (1)"},
    {"value": 2, "name": "Minor", "label": "Minor (2)"},
    {"value": 3, "name": "Moderate", "label": "Moderate (3)"},
    {"value": 4, "name": "High", "label": "High (4)"},
    {"value": 5, "name": "Very High", "label": "Very High (5)"},
]

LIKELIHOOD_OPTIONS = [lvl["label"] for lvl in LIKELIHOOD_LEVELS]
IMPACT_OPTIONS = [lvl["label"] for lvl in IMPACT_LEVELS]

# Matrix mapping: (Likelihood, Impact) -> (Score, Level)
RISK_SCORING_TABLE = {
    # Virtually Certain (5)
    (5, 1): (5, "Low"),
    (5, 2): (10, "Medium"),
    (5, 3): (15, "High"),
    (5, 4): (20, "Very High"),
    (5, 5): (25, "Very High"),

    # Likely (4)
    (4, 1): (4, "Low"),
    (4, 2): (8, "Medium"),
    (4, 3): (12, "High"),
    (4, 4): (16, "High"),
    (4, 5): (20, "Very High"),

    # Possible (3)
    (3, 1): (3, "Very Low"),
    (3, 2): (6, "Low"),
    (3, 3): (9, "Medium"),
    (3, 4): (12, "High"),
    (3, 5): (15, "High"),

    # Unlikely (2)
    (2, 1): (2, "Very Low"),
    (2, 2): (4, "Low"),
    (2, 3): (6, "Low"),
    (2, 4): (8, "Medium"),
    (2, 5): (10, "Medium"),

    # Remote (1)
    (1, 1): (1, "Very Low"),
    (1, 2): (2, "Very Low"),
    (1, 3): (3, "Very Low"),
    (1, 4): (4, "Low"),
    (1, 5): (5, "Low"),
}

LEVEL_COLORS = {
    "Very Low": {
        "text": "#15803d",
        "bg": "#f0fdf4",
        "border": "#86efac",
        "badge_bg": "#dcfce7"
    },
    "Low": {
        "text": "#0369a1",
        "bg": "#f0f9ff",
        "border": "#7dd3fc",
        "badge_bg": "#e0f2fe"
    },
    "Medium": {
        "text": "#b45309",
        "bg": "#fffbeb",
        "border": "#fde047",
        "badge_bg": "#fef9c3"
    },
    "High": {
        "text": "#c2410c",
        "bg": "#fff7ed",
        "border": "#fdba74",
        "badge_bg": "#ffedd5"
    },
    "Very High": {
        "text": "#991b1b",
        "bg": "#fef2f2",
        "border": "#fca5a5",
        "badge_bg": "#fee2e2"
    },
}

def parse_level_value(val) -> int:
    """Extract numeric value (1-5) from an integer or string like 'Likely (4)' or '4'."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    val_str = str(val).strip()
    # Check parenthetical number e.g. "Likely (4)"
    import re
    match = re.search(r"\((\d+)\)", val_str)
    if match:
        return int(match.group(1))
    # Check if purely digits
    if val_str.isdigit():
        return int(val_str)
    # Check by label prefix
    val_lower = val_str.lower()
    for lvl in LIKELIHOOD_LEVELS:
        if lvl["name"].lower() == val_lower or lvl["label"].lower() == val_lower:
            return lvl["value"]
    for lvl in IMPACT_LEVELS:
        if lvl["name"].lower() == val_lower or lvl["label"].lower() == val_lower:
            return lvl["value"]
    return 0

def calculate_risk(likelihood, impact) -> dict:
    """
    Calculate risk score, level, and styling given likelihood and impact.
    Returns a dict with: score, level, label, colors.
    """
    l_val = parse_level_value(likelihood)
    i_val = parse_level_value(impact)

    if l_val < 1 or l_val > 5 or i_val < 1 or i_val > 5:
        return {
            "score": None,
            "level": "Unassessed",
            "label": "Unassessed",
            "likelihood_val": l_val,
            "impact_val": i_val,
            "text_color": "#64748b",
            "bg_color": "#f1f5f9",
            "border_color": "#cbd5e1"
        }

    score, level = RISK_SCORING_TABLE.get((l_val, i_val), (l_val * i_val, "Medium"))
    colors = LEVEL_COLORS.get(level, {
        "text": "#334155",
        "bg": "#f8fafc",
        "border": "#e2e8f0",
        "badge_bg": "#f1f5f9"
    })

    return {
        "score": score,
        "level": level,
        "label": f"{level} ({score})",
        "likelihood_val": l_val,
        "impact_val": i_val,
        "text_color": colors["text"],
        "bg_color": colors["bg"],
        "border_color": colors["border"],
        "badge_bg": colors["badge_bg"]
    }

def get_risk_badge_html(level: str, score: int = None) -> str:
    """Generate a clean HTML badge for a risk level and score."""
    colors = LEVEL_COLORS.get(level, {
        "text": "#475569",
        "badge_bg": "#f1f5f9",
        "border": "#cbd5e1"
    })
    label = f"{level} ({score})" if score is not None else level
    return f"""<span style="display: inline-block; padding: 3px 10px; font-size: 12px; font-weight: 700; border-radius: 9999px; background-color: {colors['badge_bg']}; color: {colors['text']}; border: 1px solid {colors['border']}; white-space: nowrap;">{label}</span>"""

def render_matrix_table_html(highlight_l: int = None, highlight_i: int = None) -> str:
    """
    Generates an HTML table of the 5x5 Risk Scoring Matrix.
    Optionally highlights the cell at (highlight_l, highlight_i).
    """
    html = [
        '<div style="overflow-x: auto; margin: 16px 0;">',
        '<table style="width: 100%; border-collapse: separate; border-spacing: 4px; font-family: \'Inter\', sans-serif; font-size: 13px; text-align: center;">',
        '<thead>',
        '<tr>',
        '<th style="padding: 10px; background-color: #003865; color: white; border-radius: 6px; font-weight: 700; width: 22%;">Likelihood \\ Impact</th>',
        '<th style="padding: 8px; background-color: #f1f5f9; color: #1e293b; border-radius: 6px; font-weight: 600;">Insignificant<br><span style="font-size: 11px; opacity: 0.8;">(1)</span></th>',
        '<th style="padding: 8px; background-color: #f1f5f9; color: #1e293b; border-radius: 6px; font-weight: 600;">Minor<br><span style="font-size: 11px; opacity: 0.8;">(2)</span></th>',
        '<th style="padding: 8px; background-color: #f1f5f9; color: #1e293b; border-radius: 6px; font-weight: 600;">Moderate<br><span style="font-size: 11px; opacity: 0.8;">(3)</span></th>',
        '<th style="padding: 8px; background-color: #f1f5f9; color: #1e293b; border-radius: 6px; font-weight: 600;">High<br><span style="font-size: 11px; opacity: 0.8;">(4)</span></th>',
        '<th style="padding: 8px; background-color: #f1f5f9; color: #1e293b; border-radius: 6px; font-weight: 600;">Very High<br><span style="font-size: 11px; opacity: 0.8;">(5)</span></th>',
        '</tr>',
        '</thead>',
        '<tbody>'
    ]

    # Iterate rows from 5 down to 1
    for l_val in range(5, 0, -1):
        l_info = next(lvl for lvl in LIKELIHOOD_LEVELS if lvl["value"] == l_val)
        html.append('<tr>')
        html.append(f'<td style="padding: 10px 12px; text-align: left; background-color: #f8fafc; font-weight: 700; color: #003865; border-radius: 6px; border-left: 4px solid #0056b3;">{l_info["name"]} <span style="font-size: 11px; color: #64748b; font-weight: 500;">({l_val})</span></td>')
        for i_val in range(1, 6):
            score, level = RISK_SCORING_TABLE[(l_val, i_val)]
            c = LEVEL_COLORS[level]
            is_hl = (highlight_l == l_val and highlight_i == i_val)
            hl_border = "3px solid #003865" if is_hl else f"1px solid {c['border']}"
            hl_shadow = "box-shadow: 0 0 10px rgba(0, 56, 101, 0.4);" if is_hl else ""
            
            html.append(f'<td style="padding: 10px; background-color: {c["bg"]}; color: {c["text"]}; border: {hl_border}; border-radius: 6px; {hl_shadow}"><div style="font-weight: 700; font-size: 13px;">{level}</div><div style="font-size: 11px; font-weight: 600; opacity: 0.85;">Score: {score}</div></td>')
        html.append('</tr>')

    html.append('</tbody>')
    html.append('</table>')
    html.append('</div>')
    return "".join(html)
