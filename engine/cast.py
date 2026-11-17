"""MarketSamachar character cast — original, code-drawn SVG hosts, one per kind of update.

Every character is its own <svg> (feet at 0,0; viewBox -150 -300 300 330) so GSAP svgOrigin pivots are local.
Rig ids (p = unique prefix):  {p}-bob  body group (bob / squash)   {p}-eyes  blink   {p}-mouth  talk
                              {p}-armL / {p}-armR  arms (pivot at the shoulder)   {p}-prop  hand prop / special part
SHOULDER[name] gives the arm pivots. js_* helpers return GSAP timeline lines.
"""
import math

INK = "#0B0B16"
CAST = {
    "munshi":  dict(label="Munshi",  role="Results",              color="#7C6CF6"),
    "bhonpu":  dict(label="Bhonpu",  role="Announcements & orders", color="#FF8A3D"),
    "golu":    dict(label="Golu",    role="Dividends",            color="#FF8FB1"),
    "katli":   dict(label="Katli",   role="Stock splits",         color="#E9D6AE"),
    "tohfa":   dict(label="Tohfa",   role="Bonus shares",         color="#2DD4BF"),
    "wapsi":   dict(label="Wapsi",   role="Buybacks",             color="#FACC15"),
    "naya":    dict(label="Naya",    role="IPOs & listings",      color="#38BDF8"),
    "tareekh": dict(label="Tareekh", role="Events & calendar",    color="#F8FAFC"),
    "ghanti":  dict(label="Ghanti",  role="Market open & close",  color="#F5B83D"),
    "teji":    dict(label="Teji",    role="Top gainers",          color="#00FF88"),
    "mandi":   dict(label="Mandi",   role="Top losers",           color="#FF4D6D"),
    "desi":    dict(label="Desi",    role="DII flows",            color="#F5C542"),
    "videshi": dict(label="Videshi", role="FII flows",            color="#3B82F6"),
    "arth":    dict(label="Prof. Arth", role="Economy, RBI & rupee", color="#22A06B"),
}
SHOULDER = {}


def _eyes(p, x1, x2, y, r=15, look=0):
    def one(x):
        return (f'<ellipse cx="{x}" cy="{y}" rx="{r}" ry="{r * 1.12:.1f}" fill="#fff" stroke="{INK}" stroke-width="3"/>'
                f'<circle cx="{x + look}" cy="{y + 2}" r="{r * .55:.1f}" fill="{INK}"/><circle cx="{x + look + r * .22:.1f}" cy="{y - r * .2:.1f}" r="{r * .2:.1f}" fill="#fff"/>')
    return f'<g id="{p}-eyes">{one(x1)}{one(x2)}</g>'


def _mouth(p, x, y, w=28):
    return (f'<g id="{p}-mouth"><path d="M{x - w / 2},{y} Q{x},{y + w * .75} {x + w / 2},{y} Z" fill="#3A0D18" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<ellipse cx="{x}" cy="{y + w * .38:.1f}" rx="{w * .22:.1f}" ry="{w * .12:.1f}" fill="#FF6B8A"/></g>')


def _cheeks(x1, x2, y):
    return f'<ellipse cx="{x1}" cy="{y}" rx="11" ry="7" fill="#FF6B8A" opacity=".45"/><ellipse cx="{x2}" cy="{y}" rx="11" ry="7" fill="#FF6B8A" opacity=".45"/>'


def _arm(p, side, sx, sy, length, color, ang, hand=None, width=14):
    """Arm drawn hanging at angle `ang` (deg, 0 = straight down, + = outward)."""
    s = -1 if side == "L" else 1
    a = math.radians(ang); ex, ey = sx + s * length * math.sin(a), sy + length * math.cos(a)
    mx, my = (sx + ex) / 2 + s * 8, (sy + ey) / 2
    SHOULDER.setdefault(p, {})[side] = (sx, sy)
    return (f'<g id="{p}-arm{side}"><path d="M{sx},{sy} Q{mx:.0f},{my:.0f} {ex:.0f},{ey:.0f}" fill="none" stroke="{INK}" stroke-width="{width + 6}" stroke-linecap="round"/>'
            f'<path d="M{sx},{sy} Q{mx:.0f},{my:.0f} {ex:.0f},{ey:.0f}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
            f'<circle cx="{ex:.0f}" cy="{ey:.0f}" r="13" fill="{hand or color}" stroke="{INK}" stroke-width="4"/></g>')


def _legs(x1, x2, y0, color, shoe=INK):
    return (f'<path d="M{x1},{y0} L{x1},-14 M{x2},{y0} L{x2},-14" stroke="{INK}" stroke-width="18" stroke-linecap="round"/>'
            f'<path d="M{x1},{y0} L{x1},-14 M{x2},{y0} L{x2},-14" stroke="{color}" stroke-width="11" stroke-linecap="round"/>'
            f'<ellipse cx="{x1 - 6}" cy="-8" rx="20" ry="10" fill="{shoe}"/><ellipse cx="{x2 + 6}" cy="-8" rx="20" ry="10" fill="{shoe}"/>')


def _shadow():
    return '<ellipse cx="0" cy="2" rx="95" ry="14" fill="#000" opacity=".35"/>'


def _wrap(p, body, width):
    h = width * 330 / 300
    return (f'<svg id="{p}-svg" width="{width}" height="{h:.0f}" viewBox="-150 -300 300 330" style="overflow:visible">'
            f'{_shadow()}<g id="{p}-bob">{body}</g></svg>')


# ---------------------------------------------------------------- the cast
def munshi(p):
    body = (_legs(-30, 30, -40, "#F5A524", "#F5A524")
            + f'<path d="M0,-262 C78,-262 104,-190 104,-120 C104,-50 62,-24 0,-24 C-62,-24 -104,-50 -104,-120 C-104,-190 -78,-262 0,-262 Z" fill="#6D5BD0" stroke="{INK}" stroke-width="6"/>'
            + f'<path d="M-62,-250 L-84,-296 L-36,-262 Z M62,-250 L84,-296 L36,-262 Z" fill="#5646B8" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            + f'<ellipse cx="0" cy="-92" rx="62" ry="62" fill="#F3E8D2" stroke="{INK}" stroke-width="4"/>'
            + "".join(f'<path d="M{x - 12},{y} Q{x},{y + 12} {x + 12},{y}" fill="none" stroke="#D8C8A8" stroke-width="4" stroke-linecap="round"/>' for x, y in ((-24, -112), (0, -112), (24, -112), (-12, -90), (12, -90), (0, -68)))
            + f'<ellipse cx="-38" cy="-180" rx="38" ry="38" fill="#9B8CF2"/><ellipse cx="38" cy="-180" rx="38" ry="38" fill="#9B8CF2"/>'
            + _eyes(p, -38, 38, -180, 19)
            + f'<circle cx="-38" cy="-180" r="30" fill="none" stroke="#F5C542" stroke-width="7"/><circle cx="38" cy="-180" r="30" fill="none" stroke="#F5C542" stroke-width="7"/><path d="M-8,-182 L8,-182" stroke="#F5C542" stroke-width="6"/>'
            + f'<path d="M-14,-150 L14,-150 L0,-134 Z" fill="#F5A524" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/>'
            + f'<g id="{p}-mouth"><path d="M-10,-134 L10,-134 L0,-122 Z" fill="#D97706" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/></g>'
            + _arm(p, "L", -92, -140, 74, "#5646B8", 28, width=22)
            + f'<g id="{p}-armR"><path d="M92,-140 Q124,-112 120,-84" fill="none" stroke="{INK}" stroke-width="28" stroke-linecap="round"/><path d="M92,-140 Q124,-112 120,-84" fill="none" stroke="#5646B8" stroke-width="22" stroke-linecap="round"/>'
            + f'<g id="{p}-prop"><rect x="92" y="-126" width="76" height="96" rx="8" fill="#0F9D58" stroke="{INK}" stroke-width="5" transform="rotate(-8 130 -78)"/>'
            + f'<rect x="100" y="-118" width="12" height="80" fill="#0B7A44" transform="rotate(-8 130 -78)"/><text x="136" y="-62" text-anchor="middle" font-family="DM Mono" font-weight="700" font-size="40" fill="#E8FFF2" transform="rotate(-8 130 -78)">₹</text></g></g>')
    SHOULDER.setdefault(p, {})["R"] = (92, -140)
    return body


def bhonpu(p):
    return (_legs(-30, 30, -40, "#C2410C")
            + f'<path d="M-46,-40 L46,-40 L104,-232 L-104,-232 Z" fill="#FF8A3D" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
            + f'<path d="M-28,-40 L-60,-232" stroke="#FFB27A" stroke-width="10" opacity=".6"/>'
            + f'<ellipse cx="0" cy="-232" rx="104" ry="28" fill="#C2410C" stroke="{INK}" stroke-width="6"/><ellipse cx="0" cy="-232" rx="78" ry="16" fill="#3A1205"/>'
            + f'<g id="{p}-prop" fill="none" stroke="#FFB27A" stroke-width="8" stroke-linecap="round"><path d="M-60,-272 Q0,-300 60,-272"/><path d="M-38,-292 Q0,-312 38,-292" opacity=".6"/></g>'
            + _eyes(p, -28, 28, -150, 16) + _mouth(p, 0, -112, 30) + _cheeks(-50, 50, -126)
            + _arm(p, "L", -64, -120, 70, "#FF8A3D", 25) + _arm(p, "R", 64, -120, 70, "#FF8A3D", 25))


def golu(p):
    return (_legs(-36, 36, -44, "#F472A6")
            + f'<ellipse cx="0" cy="-130" rx="100" ry="96" fill="#FF8FB1" stroke="{INK}" stroke-width="6"/>'
            + f'<path d="M-70,-210 L-88,-262 L-40,-222 Z M70,-210 L88,-262 L40,-222 Z" fill="#F472A6" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>'
            + f'<rect x="-30" y="-232" width="60" height="12" rx="6" fill="{INK}"/>'
            + f'<path d="M98,-110 q26,-6 18,-26 q-8,-18 -22,-4" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
            + _eyes(p, -34, 34, -168, 15)
            + f'<ellipse cx="0" cy="-126" rx="34" ry="24" fill="#FFB3C9" stroke="{INK}" stroke-width="5"/><ellipse cx="-11" cy="-126" rx="5" ry="8" fill="{INK}"/><ellipse cx="11" cy="-126" rx="5" ry="8" fill="{INK}"/>'
            + _mouth(p, 0, -92, 26) + _cheeks(-62, 62, -140)
            + _arm(p, "L", -88, -112, 60, "#FF8FB1", 30)
            + f'<g id="{p}-armR"><path d="M88,-112 Q112,-90 116,-64" fill="none" stroke="{INK}" stroke-width="20" stroke-linecap="round"/><path d="M88,-112 Q112,-90 116,-64" fill="none" stroke="#FF8FB1" stroke-width="14" stroke-linecap="round"/>'
            + f'<g id="{p}-prop"><circle cx="122" cy="-58" r="26" fill="#F5C542" stroke="{INK}" stroke-width="5"/><circle cx="122" cy="-58" r="17" fill="none" stroke="#C99A1E" stroke-width="4"/>'
            + f'<text x="122" y="-47" text-anchor="middle" font-family="DM Mono" font-weight="700" font-size="28" fill="#8A6510">₹</text></g></g>')


def katli(p):
    return (_legs(-28, 28, -46, "#B9A27A")
            + f'<path d="M0,-266 L118,-150 L0,-34 L-118,-150 Z" fill="#CDB88E" stroke="{INK}" stroke-width="6" stroke-linejoin="round" transform="translate(0 10)"/>'
            + f'<path d="M0,-266 L118,-150 L0,-34 L-118,-150 Z" fill="#EAD7B0" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
            + f'<path d="M0,-252 L104,-150 L0,-48 L-104,-150 Z" fill="#F7F3EA" opacity=".85"/>'
            + f'<path d="M-40,-212 L40,-132 M-10,-238 L70,-158 M-70,-182 L10,-102" stroke="#FFFFFF" stroke-width="8" opacity=".7"/>'
            + f'<g id="{p}-prop"><path d="M0,-266 L0,-34" stroke="#C7B48D" stroke-width="3" stroke-dasharray="8 8" opacity=".9"/></g>'
            + _eyes(p, -30, 30, -168, 15) + _mouth(p, 0, -128, 26) + _cheeks(-56, 56, -142)
            + _arm(p, "L", -84, -140, 62, "#D9C49A", 30, width=11) + _arm(p, "R", 84, -140, 62, "#D9C49A", 30, width=11))


def tohfa(p):
    return (_legs(-40, 40, -40, "#0F766E")
            + f'<rect x="-96" y="-196" width="192" height="160" rx="14" fill="#2DD4BF" stroke="{INK}" stroke-width="6"/>'
            + f'<rect x="-14" y="-196" width="28" height="160" fill="#F43F5E" stroke="{INK}" stroke-width="4"/>'
            + f'<g id="{p}-prop"><rect x="-108" y="-226" width="216" height="40" rx="10" fill="#14B8A6" stroke="{INK}" stroke-width="6"/>'
            + f'<rect x="-14" y="-226" width="28" height="40" fill="#F43F5E" stroke="{INK}" stroke-width="4"/>'
            + f'<ellipse cx="-34" cy="-246" rx="36" ry="20" fill="#F43F5E" stroke="{INK}" stroke-width="5" transform="rotate(-24 -34 -246)"/>'
            + f'<ellipse cx="34" cy="-246" rx="36" ry="20" fill="#F43F5E" stroke="{INK}" stroke-width="5" transform="rotate(24 34 -246)"/><circle cx="0" cy="-236" r="14" fill="#E11D48" stroke="{INK}" stroke-width="4"/></g>'
            + _eyes(p, -50, 50, -148, 16) + _mouth(p, 0, -104, 28) + _cheeks(-62, 62, -116)
            + _arm(p, "L", -94, -130, 64, "#2DD4BF", 28) + _arm(p, "R", 94, -130, 64, "#2DD4BF", 28))


def wapsi(p):
    return (_legs(-26, 26, -60, "#CA8A04")
            + f'<path d="M-128,-212 Q-60,-120 0,-70 Q60,-120 128,-212 Q140,-232 118,-236 Q60,-170 0,-130 Q-60,-170 -118,-236 Q-140,-232 -128,-212 Z" fill="#FACC15" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
            + f'<path d="M-104,-206 Q-56,-140 0,-100 Q56,-140 104,-206" fill="none" stroke="#A16207" stroke-width="6" stroke-dasharray="14 12"/>'
            + f'<ellipse cx="0" cy="-122" rx="62" ry="54" fill="#FDE047" stroke="{INK}" stroke-width="5"/>'
            + _eyes(p, -24, 24, -136, 13) + _mouth(p, 0, -104, 22)
            + f'<g id="{p}-prop"><path d="M-150,-250 q30,-22 60,-6" fill="none" stroke="#FDE047" stroke-width="6" stroke-linecap="round" opacity=".7"/><path d="M150,-250 q-30,-22 -60,-6" fill="none" stroke="#FDE047" stroke-width="6" stroke-linecap="round" opacity=".7"/></g>'
            + _arm(p, "L", -52, -100, 56, "#EAB308", 32, width=11) + _arm(p, "R", 52, -100, 56, "#EAB308", 32, width=11))


def naya(p):
    return (_legs(-30, 30, -40, "#0284C7")
            + f'<path d="M-82,-170 C-82,-250 82,-250 82,-170 L82,-90 C82,-30 -82,-30 -82,-90 Z" fill="#38BDF8" stroke="{INK}" stroke-width="6"/>'
            + f'<g id="{p}-prop"><path d="M0,-238 C-6,-262 -28,-272 -44,-262 C-30,-250 -12,-246 0,-238 Z" fill="#22C55E" stroke="{INK}" stroke-width="4"/>'
            + f'<path d="M0,-238 C8,-266 34,-276 50,-262 C34,-248 14,-244 0,-238 Z" fill="#4ADE80" stroke="{INK}" stroke-width="4"/></g>'
            + _eyes(p, -28, 28, -178, 15) + _mouth(p, 0, -142, 26) + _cheeks(-52, 52, -154)
            + f'<rect x="-56" y="-118" width="112" height="62" rx="8" fill="#fff" stroke="{INK}" stroke-width="4"/><rect x="-56" y="-118" width="112" height="20" rx="6" fill="#EF4444"/>'
            + f'<text x="0" y="-103" text-anchor="middle" font-family="DM Sans" font-weight="800" font-size="13" fill="#fff" letter-spacing="1">HELLO I&#39;M</text>'
            + f'<text x="0" y="-68" text-anchor="middle" font-family="Alfa Slab One" font-size="26" fill="{INK}">NEW</text>'
            + _arm(p, "L", -78, -120, 62, "#38BDF8", 28) + _arm(p, "R", 78, -120, 62, "#38BDF8", 28))


def tareekh(p, day="17", mon="NOV"):
    return (_legs(-34, 34, -40, "#94A3B8")
            + f'<rect x="-96" y="-246" width="192" height="210" rx="16" fill="#F8FAFC" stroke="{INK}" stroke-width="6"/>'
            + f'<path d="M-96,-230 Q-96,-246 -80,-246 L80,-246 Q96,-246 96,-230 L96,-196 L-96,-196 Z" fill="#EF4444" stroke="{INK}" stroke-width="6"/>'
            + f'<text id="{p}-mon" x="0" y="-208" text-anchor="middle" font-family="DM Sans" font-weight="800" font-size="24" fill="#fff" letter-spacing="4">{mon}</text>'
            + f'<rect x="-56" y="-262" width="14" height="34" rx="7" fill="#64748B" stroke="{INK}" stroke-width="4"/><rect x="42" y="-262" width="14" height="34" rx="7" fill="#64748B" stroke="{INK}" stroke-width="4"/>'
            + _eyes(p, -34, 34, -164, 14) + _mouth(p, 0, -134, 22)
            + f'<text id="{p}-day" x="0" y="-52" text-anchor="middle" font-family="Alfa Slab One" font-size="64" fill="#0B1A44">{day}</text>'
            + f'<g id="{p}-prop"><path d="M60,-62 L96,-36 L60,-36 Z" fill="#CBD5E1" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/></g>'
            + _arm(p, "L", -92, -150, 64, "#CBD5E1", 26) + _arm(p, "R", 92, -150, 64, "#CBD5E1", 26))


def ghanti(p):
    return (_legs(-30, 30, -44, "#B45309")
            + f'<path d="M-14,-266 a14,14 0 1 1 28,0" fill="none" stroke="{INK}" stroke-width="16"/><path d="M-14,-266 a14,14 0 1 1 28,0" fill="none" stroke="#D97706" stroke-width="9"/>'
            + f'<path d="M0,-262 C62,-262 78,-210 82,-150 C86,-104 104,-82 118,-66 L-118,-66 C-104,-82 -86,-104 -82,-150 C-78,-210 -62,-262 0,-262 Z" fill="#F5B83D" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
            + f'<path d="M-50,-236 C-66,-200 -70,-150 -74,-112" fill="none" stroke="#FFE08A" stroke-width="10" stroke-linecap="round" opacity=".8"/>'
            + f'<rect x="-122" y="-74" width="244" height="22" rx="11" fill="#D97706" stroke="{INK}" stroke-width="5"/>'
            + f'<g id="{p}-prop"><path d="M0,-52 L0,-36" stroke="{INK}" stroke-width="6"/><circle cx="0" cy="-30" r="14" fill="#92400E" stroke="{INK}" stroke-width="5"/></g>'
            + _eyes(p, -30, 30, -178, 15) + _mouth(p, 0, -140, 26) + _cheeks(-54, 54, -152)
            + _arm(p, "L", -80, -140, 66, "#D97706", 32) + _arm(p, "R", 80, -140, 66, "#D97706", 32))


def teji(p):
    return (_legs(-26, 26, -40, "#059669")
            + f'<path d="M0,-286 L112,-176 L48,-176 L48,-40 L-48,-40 L-48,-176 L-112,-176 Z" fill="#00FF88" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
            + f'<path d="M0,-262 L82,-182" stroke="#B6FFD9" stroke-width="10" stroke-linecap="round" opacity=".8"/>'
            + _eyes(p, -22, 22, -140, 14) + _mouth(p, 0, -104, 24)
            + f'<g id="{p}-prop"></g>'
            + _arm(p, "L", -48, -110, 58, "#00D474", 34) + _arm(p, "R", 48, -110, 58, "#00D474", 34))


def mandi(p):
    return (_legs(-26, 26, -44, "#BE123C")
            + f'<path d="M-48,-262 L48,-262 L48,-140 L112,-140 L0,-34 L-112,-140 L-48,-140 Z" fill="#FF4D6D" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>'
            + f'<path d="M-30,-248 L-30,-160" stroke="#FFB3C1" stroke-width="10" stroke-linecap="round" opacity=".8"/>'
            + _eyes(p, -22, 22, -214, 14) + _mouth(p, 0, -180, 24)
            + f'<g id="{p}-prop"></g>'
            + _arm(p, "L", -48, -190, 58, "#E11D48", 34) + _arm(p, "R", 48, -190, 58, "#E11D48", 34))


def desi(p):
    return (_legs(-30, 30, -40, "#B7791F")
            + f'<circle cx="0" cy="-138" r="104" fill="#C99A1E" stroke="{INK}" stroke-width="6"/>'
            + f'<circle cx="0" cy="-142" r="96" fill="#F5C542" stroke="{INK}" stroke-width="4"/><circle cx="0" cy="-142" r="80" fill="none" stroke="#C99A1E" stroke-width="5" stroke-dasharray="6 8"/>'
            + _eyes(p, -30, 30, -170, 15) + _mouth(p, 0, -130, 26) + _cheeks(-56, 56, -146)
            + f'<g id="{p}-prop"><path d="M-70,-82 L70,-82" stroke="#FF9933" stroke-width="16" stroke-linecap="round"/>'
            + f'<text x="0" y="-74" text-anchor="middle" font-family="DM Sans" font-weight="800" font-size="16" fill="#fff" letter-spacing="3">DII</text></g>'
            + _arm(p, "L", -94, -120, 60, "#E0AE2C", 30) + _arm(p, "R", 94, -120, 60, "#E0AE2C", 30))


def videshi(p):
    return (_legs(-30, 30, -40, "#1D4ED8")
            + f'<circle cx="0" cy="-142" r="102" fill="#3B82F6" stroke="{INK}" stroke-width="6"/>'
            + f'<path d="M-80,-196 C-50,-214 -30,-190 -44,-168 C-58,-150 -86,-160 -92,-176 Z M30,-226 C64,-224 84,-196 70,-178 C50,-170 38,-196 22,-204 Z M-20,-84 C10,-96 40,-80 34,-60 C10,-48 -14,-58 -20,-84 Z M62,-120 C84,-126 96,-100 86,-86 C70,-84 60,-104 62,-120 Z" fill="#22C55E" stroke="{INK}" stroke-width="3"/>'
            + f'<path d="M-102,-142 L102,-142 M0,-244 C-50,-200 -50,-84 0,-40 M0,-244 C50,-200 50,-84 0,-40" fill="none" stroke="#93C5FD" stroke-width="3" opacity=".6"/>'
            + _eyes(p, -30, 30, -160, 15) + _mouth(p, 0, -120, 26)
            + f'<g id="{p}-prop"><ellipse cx="0" cy="-142" rx="140" ry="40" fill="none" stroke="#BFDBFE" stroke-width="4" stroke-dasharray="10 10" opacity=".7"/>'
            + f'<path d="M126,-170 l22,-6 -6,12 z" fill="#F8FAFC" stroke="{INK}" stroke-width="3"/>'
            + f'<text x="0" y="-62" text-anchor="middle" font-family="DM Sans" font-weight="800" font-size="16" fill="#fff" letter-spacing="3">FII</text></g>'
            + _arm(p, "L", -92, -116, 60, "#2563EB", 30) + _arm(p, "R", 92, -116, 60, "#2563EB", 30))


def arth(p):
    return (_legs(-34, 34, -40, "#65A30D")
            + f'<path d="M-118,-110 C-128,-210 -40,-250 0,-250 C40,-250 128,-210 118,-110 C110,-60 70,-40 0,-40 C-70,-40 -110,-60 -118,-110 Z" fill="#166534" stroke="{INK}" stroke-width="6"/>'
            + "".join(f'<path d="M{x - 22},{y} l11,-19 h22 l11,19 l-11,19 h-22 z" fill="#22A06B" stroke="#14532D" stroke-width="4"/>' for x, y in ((-60, -190), (0, -210), (60, -190), (-80, -130), (-20, -150), (40, -150), (90, -120)))
            + f'<ellipse cx="0" cy="-110" rx="64" ry="72" fill="#E9D8A6" stroke="{INK}" stroke-width="5"/>'
            + f'<path d="M-40,-140 L40,-140 M-48,-110 L48,-110 M-40,-80 L40,-80" stroke="#C9B57E" stroke-width="5"/>'
            + f'<ellipse cx="0" cy="-226" rx="58" ry="52" fill="#84CC16" stroke="{INK}" stroke-width="6"/>'
            + _eyes(p, -22, 22, -232, 13)
            + f'<circle cx="-22" cy="-232" r="20" fill="none" stroke="{INK}" stroke-width="5"/><circle cx="22" cy="-232" r="20" fill="none" stroke="{INK}" stroke-width="5"/><path d="M-2,-234 L2,-234" stroke="{INK}" stroke-width="5"/>'
            + _mouth(p, 0, -200, 22)
            + f'<path d="M-64,-280 L0,-300 L64,-280 L0,-262 Z" fill="#1E293B" stroke="{INK}" stroke-width="4" stroke-linejoin="round"/><rect x="-26" y="-282" width="52" height="16" fill="#1E293B"/>'
            + f'<path d="M44,-282 L60,-246" stroke="#F5C542" stroke-width="4"/><circle cx="60" cy="-244" r="6" fill="#F5C542"/>'
            + _arm(p, "L", -100, -130, 62, "#84CC16", 30)
            + f'<g id="{p}-armR"><path d="M100,-130 Q130,-108 128,-80" fill="none" stroke="{INK}" stroke-width="20" stroke-linecap="round"/><path d="M100,-130 Q130,-108 128,-80" fill="none" stroke="#84CC16" stroke-width="14" stroke-linecap="round"/>'
            + f'<g id="{p}-prop"><path d="M128,-80 L178,-210" stroke="#7C2D12" stroke-width="8" stroke-linecap="round"/><circle cx="178" cy="-210" r="7" fill="#F5C542"/></g><circle cx="128" cy="-80" r="13" fill="#84CC16" stroke="{INK}" stroke-width="4"/></g>')


DRAW = dict(munshi=munshi, bhonpu=bhonpu, golu=golu, katli=katli, tohfa=tohfa, wapsi=wapsi, naya=naya, tareekh=tareekh,
            ghanti=ghanti, teji=teji, mandi=mandi, desi=desi, videshi=videshi, arth=arth)
_SH = {"munshi": {"R": (92, -140)}, "golu": {"R": (88, -112)}, "arth": {"R": (100, -130)}}


def svg(name, p, width=300, **kw):
    body = DRAW[name](p, **kw) if kw else DRAW[name](p)
    for side, xy in _SH.get(name, {}).items(): SHOULDER.setdefault(p, {})[side] = xy
    return _wrap(p, body, width)


# ---------------------------------------------------------------- animation helpers (GSAP)
def T(x): return f"{x:.3f}"


def js_enter(p, t, how="pop"):
    """Entrances with anticipation, squash and a settle (acting, not UI motion)."""
    sel, bob = f"#{p}", f"#{p}-bob"
    out = []
    if how == "drop":
        out.append(f'tl.fromTo("{sel}",{{y:-1000,opacity:1}},{{y:0,duration:.42,ease:"power3.in"}},{T(t)})')
        t += .42
    elif how in ("left", "right"):
        out.append(f'tl.fromTo("{sel}",{{x:{-800 if how == "left" else 800},opacity:1}},{{x:0,duration:.5,ease:"power3.out"}},{T(t)})')
        out.append(f'tl.fromTo("{bob}",{{rotation:{12 if how == "left" else -12},svgOrigin:"0 0"}},{{rotation:0,svgOrigin:"0 0",duration:.6,ease:"elastic.out(1,.45)"}},{T(t + .35)})')
        return out
    elif how == "rise":
        out.append(f'tl.fromTo("{sel}",{{y:520,opacity:1}},{{y:0,duration:.55,ease:"expo.out"}},{T(t)})')
        t += .4
    else:
        out.append(f'tl.fromTo("{sel}",{{scale:0,opacity:0,transformOrigin:"50% 100%"}},{{scale:1,opacity:1,duration:.35,ease:"power3.out"}},{T(t)})')
        t += .3
    # land: squash, stretch, settle
    out.append(f'tl.fromTo("{bob}",{{scaleX:1.25,scaleY:.72,svgOrigin:"0 0"}},{{scaleX:.94,scaleY:1.08,svgOrigin:"0 0",duration:.12,ease:"power2.out"}},{T(t)})')
    out.append(f'tl.to("{bob}",{{scaleX:1,scaleY:1,svgOrigin:"0 0",duration:.45,ease:"elastic.out(1,.4)"}},{T(t + .12)})')
    return out


def js_react(p, t, mood):
    """A take: anticipation, the action, a held reaction, then settle."""
    bob = f"#{p}-bob"; sh = SHOULDER.get(p, {}); out = []
    if mood == "up":
        out.append(f'tl.to("{bob}",{{scaleY:.86,scaleX:1.08,svgOrigin:"0 0",duration:.1,ease:"power2.in"}},{T(t)})')
        out.append(f'tl.to("{bob}",{{y:-70,scaleY:1.08,scaleX:.95,svgOrigin:"0 0",duration:.22,ease:"power2.out"}},{T(t + .1)})')
        out.append(f'tl.to("{bob}",{{y:0,scaleY:1,scaleX:1,svgOrigin:"0 0",duration:.4,ease:"bounce.out"}},{T(t + .32)})')
        for side, deg, dl in (("L", 150, 0), ("R", -140, .07)):
            if side in sh:
                x, y = sh[side]
                out.append(f'tl.to("#{p}-arm{side}",{{rotation:{deg},svgOrigin:"{x} {y}",duration:.22,ease:"back.out(2)"}},{T(t + .1 + dl)})')
                out.append(f'tl.to("#{p}-arm{side}",{{rotation:0,svgOrigin:"{x} {y}",duration:.4,ease:"power2.inOut"}},{T(t + 1.0 + dl)})')
    elif mood == "down":
        out.append(f'tl.to("{bob}",{{scaleY:.9,scaleX:1.05,y:8,svgOrigin:"0 0",duration:.35,ease:"power2.out"}},{T(t)})')
        out.append(f'tl.to("#{p}-eyes",{{y:6,scaleY:.75,transformOrigin:"50% 50%",duration:.25}},{T(t + .05)})')
        out.append(f'tl.to("{bob}",{{scaleY:1,scaleX:1,y:0,svgOrigin:"0 0",duration:.5,ease:"power2.inOut"}},{T(t + 1.1)})')
        out.append(f'tl.to("#{p}-eyes",{{y:0,scaleY:1,duration:.3}},{T(t + 1.1)})')
    return out


def js_look(p, t, dx):
    return [f'tl.to("#{p}-eyes",{{x:{dx},duration:.25,ease:"power2.out"}},{T(t)})']


def js_exit(p, t, how="down"):
    if how == "down": return [f'tl.to("#{p}",{{y:600,duration:.45,ease:"back.in(1.4)"}},{T(t)})']
    return [f'tl.to("#{p}",{{scale:0,opacity:0,duration:.35,ease:"back.in(2)",transformOrigin:"50% 100%"}},{T(t)})']


def js_idle(p, t0, t1, seed=0):
    out = []
    if t1 - t0 < .4: return out
    per = .55 + (seed % 3) * .08; n = max(1, int((t1 - t0) / per))
    out.append(f'tl.fromTo("#{p}-bob",{{y:0,scaleY:1}},{{y:-7,scaleY:1.015,duration:{T(per)},ease:"sine.inOut",yoyo:true,repeat:{n - 1 + (n % 2)},svgOrigin:"0 0"}},{T(t0)})')
    k = t0 + 1.1 + (seed % 5) * .3
    while k < t1 - .3:
        out.append(f'tl.to("#{p}-eyes",{{scaleY:.1,duration:.07,yoyo:true,repeat:1,transformOrigin:"50% 50%"}},{T(k)})')
        k += 2.4 + ((seed + int(k)) % 4) * .55
    return out


def js_talk(p, amps):
    """amps: [(t, rms)] every ~2 frames while this character speaks."""
    return [f'tl.set("#{p}-mouth",{{scaleY:{.35 + min(1.6, a * 9):.2f},transformOrigin:"50% 0%"}},{T(t)})' for t, a in amps]


def js_gesture(p, t, kind="wave", name=None):
    sh = SHOULDER.get(p, {}); out = []
    def rot(side, deg, d=.3, back=None):
        if side not in sh: return
        x, y = sh[side]
        out.append(f'tl.to("#{p}-arm{side}",{{rotation:{deg},svgOrigin:"{x} {y}",duration:{d},ease:"back.out(2)"}},{T(t)})')
        if back is not None: out.append(f'tl.to("#{p}-arm{side}",{{rotation:0,svgOrigin:"{x} {y}",duration:.35,ease:"power2.inOut"}},{T(t + back)})')
    if kind == "wave":
        if "R" in sh:
            x, y = sh["R"]
            out.append(f'tl.to("#{p}-armR",{{rotation:-130,svgOrigin:"{x} {y}",duration:.3,ease:"back.out(2)"}},{T(t)})')
            out.append(f'tl.to("#{p}-armR",{{rotation:-100,svgOrigin:"{x} {y}",duration:.18,yoyo:true,repeat:3}},{T(t + .3)})')
            out.append(f'tl.to("#{p}-armR",{{rotation:0,svgOrigin:"{x} {y}",duration:.35}},{T(t + 1.1)})')
    elif kind == "cheer":
        rot("L", 140, back=1.0); t += .08; rot("R", -125, back=.95)
        out.append(f'tl.to("#{p}-bob",{{y:-40,duration:.22,yoyo:true,repeat:1,ease:"power2.out"}},{T(t)})')
    elif kind == "point":
        rot("R", -95, back=1.4)
    elif kind == "present":
        rot("L", 70, back=1.6); t += .1; rot("R", -55, back=1.5)
    elif kind == "shrug":
        rot("L", 60, back=.9); t += .06; rot("R", -48, back=.85)
    elif kind == "jump":
        out.append(f'tl.to("#{p}-bob",{{y:-60,duration:.25,yoyo:true,repeat:1,ease:"power2.out"}},{T(t)})')
    elif kind == "ring":   # Ghanti
        out.append(f'tl.to("#{p}-bob",{{rotation:14,svgOrigin:"0 -266",duration:.12,yoyo:true,repeat:7,ease:"sine.inOut"}},{T(t)})')
    elif kind == "open":   # Tohfa lid
        out.append(f'tl.to("#{p}-prop",{{y:-70,rotation:-18,svgOrigin:"-108 -206",duration:.5,ease:"back.out(2)"}},{T(t)})')
    elif kind == "split":  # Katli
        out.append(f'tl.to("#{p}-prop",{{opacity:1,strokeWidth:6,duration:.2}},{T(t)})')
        out.append(f'tl.to("#{p}-bob",{{scaleX:1.12,duration:.2,yoyo:true,repeat:1,svgOrigin:"0 0"}},{T(t)})')
    elif kind == "spin":   # Wapsi
        out.append(f'tl.to("#{p}-bob",{{rotation:360,svgOrigin:"0 -150",duration:.8,ease:"power2.inOut"}},{T(t)})')
    elif kind == "waves":  # Bhonpu
        out.append(f'tl.fromTo("#{p}-prop",{{scale:.6,opacity:0,svgOrigin:"0 -272"}},{{scale:1.15,opacity:1,duration:.35,yoyo:true,repeat:3,svgOrigin:"0 -272"}},{T(t)})')
    return out
