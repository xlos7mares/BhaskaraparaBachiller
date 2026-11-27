import math
from urllib.parse import quote

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sympy import Rational, latex, simplify, sqrt

st.set_page_config(
    page_title="Bhāskara · paso a paso",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CA, CB, CC, HOT, VTX, CURVE = "#22e3ff", "#ff4fd8", "#b8ff2c", "#ffe14a", "#ff9f1c", "#b388ff"


# ---------- Logo: el «¡Mirá!» de Bhāskara (cuadrado dentro de cuadrado) + sol ----------
def logo(main, inner, ray, sw=2.2):
    rays = "".join(
        f'<line x1="{60+78*math.cos(t):.1f}" y1="{60+78*math.sin(t):.1f}" '
        f'x2="{60+92*math.cos(t):.1f}" y2="{60+92*math.sin(t):.1f}" '
        f'stroke="{ray}" stroke-width="{sw}" stroke-linecap="round"/>'
        for t in [i * math.pi / 12 for i in range(24)]
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-40 -40 200 200" fill="none">{rays}'
        f'<circle cx="60" cy="60" r="71" stroke="{ray}" stroke-width="{sw/2}" stroke-dasharray="2 4"/>'
        f'<rect x="10" y="10" width="100" height="100" stroke="{main}" stroke-width="{sw}"/>'
        f'<polygon points="43.3,10 110,43.3 76.7,110 10,76.7" stroke="{inner}" '
        f'stroke-width="{sw}" fill="{inner}" fill-opacity=".15"/></svg>'
    )


WM = "data:image/svg+xml," + quote(logo("#fff", "#fff", "#fff", 1.2))

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;800&family=Figtree:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@600&display=swap');
.stApp{background:radial-gradient(900px 500px at 8% -5%,#3b22a055,transparent),
  radial-gradient(800px 500px at 100% 10%,#00d4ff1f,transparent),#080b21;
  color:#e8ecff;font-family:'Figtree',sans-serif}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.07;
  background:url("__WM__") no-repeat right -120px bottom -140px/720px}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.block-container{max-width:1250px;padding-top:2.2rem;padding-bottom:3.5rem;position:relative;z-index:1}
h1,h2,h3{font-family:'Bricolage Grotesque',sans-serif!important}

.hero{display:flex;align-items:center;gap:18px;margin-bottom:6px;flex-wrap:wrap}
.hero svg{width:84px;height:84px;flex-shrink:0;filter:drop-shadow(0 0 14px #ffe14a88)}
.hero h1{margin:0;font-size:2.6rem;font-weight:800;letter-spacing:-.02em;
  background:linear-gradient(90deg,#fff,#ffe14a 60%,#ff9f1c);-webkit-background-clip:text;
  background-clip:text;color:transparent;padding:0}
.hero .dv{font-family:'Noto Sans Devanagari',sans-serif;color:#ffe14a;letter-spacing:.12em;
  text-shadow:0 0 12px #ffe14a99;font-size:1.05rem}
.hero p{margin:2px 0 0;color:#aab3e6;max-width:640px}

.st-key-ca,.st-key-cb,.st-key-cc{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
  border-radius:20px;padding:14px 18px 6px;transition:transform .25s,box-shadow .25s,border-color .25s;
  backdrop-filter:blur(10px)}
.st-key-ca{--k:#22e3ff}.st-key-cb{--k:#ff4fd8}.st-key-cc{--k:#b8ff2c}
.st-key-ca:hover,.st-key-cb:hover,.st-key-cc:hover{transform:translateY(-4px);border-color:var(--k);
  box-shadow:0 10px 40px -10px var(--k)}
[data-testid="stNumberInput"] label p{color:var(--k)!important;font-weight:700;font-size:.95rem}
[data-testid="stNumberInput"] div,[data-testid="stNumberInput"] input{background:transparent!important}
[data-testid="stNumberInput"] div[data-baseweb="input"]{background:rgba(0,0,0,.45)!important;
  border-radius:14px!important;border:1.5px solid var(--k)!important;transition:box-shadow .25s}
div[data-baseweb="input"]:focus-within{box-shadow:0 0 0 3px color-mix(in srgb,var(--k) 30%,transparent),0 0 28px var(--k)}
[data-testid="stNumberInput"] input{color:var(--k)!important;font-weight:800;font-size:1.7rem;
  font-family:'Bricolage Grotesque',sans-serif;text-shadow:0 0 12px var(--k)}
[data-testid="stNumberInput"] button{color:var(--k)!important;background:transparent!important}

.eq{font-family:'Bricolage Grotesque',sans-serif;font-size:2.4rem;font-weight:800;text-align:center;
  margin:16px 0 6px;letter-spacing:.01em}
.eq .n{color:var(--k);text-shadow:0 0 16px var(--k)}.eq .sg{color:#8d97cf;margin:0 .35em}
.eqh{text-align:center;color:#8d97cf;font-size:.9rem;margin-bottom:10px}

.stepper{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0 18px}
.pill{display:flex;align-items:center;gap:8px;padding:6px 14px 6px 6px;border-radius:999px;
  background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);color:#8d97cf;font-size:.85rem}
.pill b{display:grid;place-items:center;width:24px;height:24px;border-radius:50%;background:rgba(255,255,255,.1)}
.pill.done{color:#e8ecff}.pill.done b{background:#b8ff2c;color:#080b21}
.pill.on{color:#080b21;background:#ffe14a;border-color:#ffe14a;font-weight:700;box-shadow:0 0 24px #ffe14a88}
.pill.on b{background:#080b21;color:#ffe14a}

.st-key-stepcard,.st-key-graphcard{background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.12);
  border-radius:24px;padding:22px 24px;backdrop-filter:blur(14px);box-shadow:0 20px 60px -30px #000}
.sh h3{margin:0;font-size:1.5rem;color:#fff;padding-right:28px}.sh p{margin:2px 0 14px;color:#aab3e6}
.chip{display:inline-block;padding:1px 11px;border-radius:999px;color:var(--k);font-weight:700;
  background:color-mix(in srgb,var(--k) 14%,transparent);border:1px solid var(--k);text-shadow:0 0 10px var(--k)}
.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:10px 0}
.tcard{border:1.5px solid var(--k);border-radius:16px;padding:12px;text-align:center;
  background:color-mix(in srgb,var(--k) 8%,transparent);box-shadow:0 0 22px -8px var(--k);transition:transform .2s}
.tcard:hover{transform:scale(1.04)}
.tcard .big{font-family:'Bricolage Grotesque',sans-serif;font-size:2.1rem;font-weight:800;color:var(--k);
  text-shadow:0 0 16px var(--k)}
.tcard small{color:#c5ccf5;display:block;line-height:1.3}
.meter{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:10px 0}
.meter div{padding:10px;border-radius:14px;text-align:center;border:1px solid rgba(255,255,255,.12);
  color:#6f79ad;font-size:.88rem}
.meter div.on{color:#080b21;background:var(--k);border-color:var(--k);font-weight:700;box-shadow:0 0 28px var(--k)}
.hint{margin:12px 0 4px;padding:12px 14px;border-radius:14px;background:rgba(255,225,74,.08);
  border-left:3px solid #ffe14a;color:#f3f0d0;line-height:1.5}
.ok{margin-top:12px;padding:12px 14px;border-radius:14px;background:rgba(184,255,44,.1);
  border:1px solid #b8ff2c;color:#e6ffb3;box-shadow:0 0 24px -8px #b8ff2c}
.warn,.sign{margin:12px 0 4px;padding:12px 14px;border-radius:14px;line-height:1.5}
.warn{background:rgba(255,79,216,.09);border-left:3px solid #ff4fd8;color:#ffd6f6}
.warn b{color:#ff4fd8;text-shadow:0 0 10px #ff4fd8aa}
.sign{background:rgba(34,227,255,.09);border-left:3px solid #22e3ff;color:#d4f8ff}
.sign b{color:#22e3ff;text-shadow:0 0 10px #22e3ffaa}
.calc{display:inline-block;margin-top:8px;padding:6px 12px;border-radius:10px;background:rgba(0,0,0,.4);
  border:1px dashed #22e3ff;color:#22e3ff;font-family:ui-monospace,monospace;font-size:1.05rem}
.credit{margin:36px auto 12px;max-width:560px;text-align:center;padding:14px 20px;border-radius:18px;background:rgba(255,255,255,.045);border:1px solid rgba(255,255,255,.12);color:#aab3e6;line-height:1.5;transition:box-shadow .25s,border-color .25s}
.credit:hover{border-color:#ffe14a;box-shadow:0 0 30px -8px #ffe14a}
.credit b{color:#ffe14a;font-family:'Bricolage Grotesque',sans-serif;font-size:1.15rem;text-shadow:0 0 12px #ffe14a88}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.stApp .katex{font-size:1.4em}.stApp .katex *{text-shadow:0 0 10px currentColor}

@media (max-width: 640px){
  .trio,.meter{grid-template-columns:1fr}
  .eq{font-size:1.85rem}
  .hero h1{font-size:2rem}
}

[data-testid="stBaseButton-primary"]{background:linear-gradient(90deg,#ffe14a,#ff9f1c)!important;color:#080b21!important;
  border:0!important;font-weight:800!important;border-radius:14px!important;transition:transform .2s,box-shadow .2s}
[data-testid="stBaseButton-primary"]:hover{transform:translateY(-2px);box-shadow:0 8px 30px #ffe14a77}
[data-testid="stBaseButton-secondary"]{background:rgba(255,255,255,.06)!important;color:#e8ecff!important;
  border:1px solid rgba(255,255,255,.18)!important;border-radius:14px!important;transition:all .2s}
[data-testid="stBaseButton-secondary"]:hover{border-color:#22e3ff!important;color:#22e3ff!important;
  box-shadow:0 0 22px -4px #22e3ff}
</style>
""".replace("__WM__", WM)
st.markdown(CSS, unsafe_allow_html=True)


# ---------- Utilidades ----------
def to_rat(x):
    return Rational(str(round(float(x), 8)))


def col(v, color):
    t = latex(v)
    if getattr(v, "is_negative", False):
        t = f"({t})"
    return rf"{{\color{{{color}}}{t}}}"


def fmt(v):
    return str(v.p) if v.q == 1 else f"{v.p}/{v.q}"


def term(v, k, var, first=False):
    s = "−" if v < 0 else ("" if first else "+")
    m = abs(v)
    coef = "" if (m == 1 and var) else fmt(m)
    return f'<span class="sg">{s}</span><span class="n" style="--k:{k}">{coef}{var}</span>'


def chip(txt, k):
    return f'<span class="chip" style="--k:{k}">{txt}</span>'


def head(n, title, sub):
    st.markdown(f'<div class="sh"><h3>{n}. {title}</h3><p>{sub}</p></div>', unsafe_allow_html=True)


def preset(a, b, c):
    st.session_state.update(a_in=float(a), b_in=float(b), c_in=float(c))


for k, v in (("a_in", 1.0), ("b_in", -5.0), ("c_in", 6.0)):
    st.session_state.setdefault(k, v)

# ---------- Encabezado ----------
st.markdown(
    f'<div class="hero">{logo("#22e3ff", "#ff4fd8", "#ffe14a")}<div>'
    '<h1>Fórmula de Bhāskara</h1><div class="dv">भास्कर</div>'
    '<p>Bhāskara significa «el que hace la luz». Acá encendemos la luz sobre cada paso de la ecuación cuadrática.</p>'
    '</div></div>',
    unsafe_allow_html=True,
)

st.caption("Probá con un ejemplo o escribí tus propios números:")
pc = st.columns(4)
for i, (lbl, p_vals) in enumerate([
    ("x² − 5x + 6", (1, -5, 6)),
    ("x² − 4x + 4", (1, -4, 4)),
    ("x² + 2x + 5", (1, 2, 5)),
    ("2x² − 3x − 2", (2, -3, -2)),
]):
    pc[i].button(lbl, on_click=preset, args=p_vals, use_container_width=True, key=f"pre{i}")

ic = st.columns(3)
with ic[0].container(key="ca"):
    a_in = st.number_input("a · acompaña a x²", step=1.0, format="%g", key="a_in")
with ic[1].container(key="cb"):
    b_in = st.number_input("b · acompaña a x", step=1.0, format="%g", key="b_in")
with ic[2].container(key="cc"):
    c_in = st.number_input("c · número solo", step=1.0, format="%g", key="c_in")

if a_in == 0:
    st.warning("Si a = 0 deja de ser una ecuación cuadrática. Elegí un a distinto de 0.")
    st.stop()

a, b, c = (to_rat(x) for x in (a_in, b_in, c_in))
st.markdown(
    f'<div class="eq">{term(a, CA, "x²", True)}{term(b, CB, "x")}{term(c, CC, "")}'
    '<span class="sg">=</span>0</div>'
    '<div class="eqh">Tu ecuación, con cada coeficiente en su color</div>',
    unsafe_allow_html=True,
)

D = simplify(b**2 - 4 * a * c)
vx, vy = simplify(-b / (2 * a)), simplify(c - b**2 / (4 * a))
x1 = x2 = None
raices = []
if D >= 0:
    x1, x2 = simplify((-b + sqrt(D)) / (2 * a)), simplify((-b - sqrt(D)) / (2 * a))
    raices = sorted({float(x1), float(x2)})

names = (
    ["Identificar", "Discriminante", "Interpretar", "Fórmula", "Raíces", "Verificar"]
    if D >= 0
    else ["Identificar", "Discriminante", "Interpretar", "Conclusión"]
)
TOTAL = len(names)
firma = (a_in, b_in, c_in)
if st.session_state.get("firma") != firma:
    st.session_state.firma, st.session_state.paso = firma, 1
paso = min(st.session_state.paso, TOTAL)

st.markdown(
    '<div class="stepper">'
    + "".join(
        f'<div class="pill {"on" if i == paso else "done" if i < paso else ""}"><b>{i}</b>{n}</div>'
        for i, n in enumerate(names, 1)
    )
    + "</div>",
    unsafe_allow_html=True,
)


# ---------- Gráfico ----------
def grafico(paso):
    fa, fb, fc, fvx, fvy = map(float, (a, b, c, vx, vy))
    span = max(abs(fvy), abs(fc), 4.0)
    lo, hi = min(0.0, fvy, fc) - span * 0.4, max(0.0, fvy, fc) + span * 0.4
    if fa > 0:
        hi = max(hi, fvy + span * 1.5)
    else:
        lo = min(lo, fvy - span * 1.5)
    alto = (hi - fvy) if fa > 0 else (fvy - lo)
    half = max([2.5, 1.2 * math.sqrt(max(alto, 0.1) / abs(fa)), abs(fvx) + 1.5] + [abs(r - fvx) + 1.5 for r in raices])
    half = min(half, 40.0)
    xs = np.linspace(fvx - half, fvx + half, 600)
    ys = fa * xs**2 + fb * xs + fc

    f = go.Figure()
    for w, o in ((14, 0.08), (7, 0.2)):
        f.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line=dict(color=CURVE, width=w),
                opacity=o,
                hoverinfo="skip",
                showlegend=False,
            )
        )
    f.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            line=dict(color=CURVE, width=3.5),
            showlegend=False,
            hovertemplate="x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>",
        )
    )

    def punto(x, y, txt, color, pos="top right", bgcolor="rgba(8,11,33,0.78)"):
        f.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers",
                hoverinfo="skip",
                showlegend=False,
                marker=dict(size=26, color=color, opacity=0.22),
            )
        )
        f.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers+text",
                text=[txt],
                textposition=pos,
                textfont=dict(color=color, size=13),
                showlegend=False,
                marker=dict(size=11, color=color, line=dict(color="#fff", width=2)),
                hovertemplate=txt + "<extra></extra>",
            )
        )
        if bgcolor:
            f.add_annotation(
                x=x,
                y=y,
                text=txt,
                showarrow=False,
                font=dict(color=color, size=13),
                bgcolor=bgcolor,
                bordercolor=color,
                borderwidth=1,
                borderpad=3,
                xshift=34 if "right" in pos else (-34 if "left" in pos else 0),
                yshift=18 if "top" in pos else (-20 if "bottom" in pos else 0),
            )
            # Oculta el texto duplicado de mode="markers+text" cuando usamos annotation con fondo
            f.data[-2].mode = "markers"

    c_pos = "top left" if fvx >= 0 else "top right"
    punto(0, fc, f"c = {fc:g}", CC, c_pos)

    if paso >= 3:
        f.add_vline(x=fvx, line=dict(color="#8d97cf", dash="dash", width=1.4))
        v_pos = "bottom right" if fa > 0 else "top right"
        punto(fvx, fvy, f"Vértice ({fvx:.2f}; {fvy:.2f})", VTX, v_pos)

    if paso >= 5 and raices:
        for i, r in enumerate(raices, 1):
            lbl = f"x{'₁₂'[i-1]} = {r:.2f}" if len(raices) > 1 else f"x = {r:.2f}"
            r_pos = "bottom left" if (len(raices) > 1 and i == 1) else "top right"
            punto(r, 0, lbl, HOT, r_pos)

    ax = dict(
        showgrid=True,
        gridcolor="rgba(255,255,255,.07)",
        zeroline=True,
        zerolinecolor="rgba(255,255,255,.75)",
        zerolinewidth=2,
        color="#aab3e6",
    )
    f.update_layout(
        height=520,
        margin=dict(l=8, r=8, t=8, b=8),
        dragmode="pan",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,.25)",
        hoverlabel=dict(bgcolor="#14183a", font_color="#fff"),
        xaxis=dict(range=[fvx - half, fvx + half], dtick=1 if half <= 8 else None, **ax),
        yaxis=dict(range=[lo, hi], **ax),
    )
    return f


# ---------- Contenido de cada paso ----------
def p(v):
    return f"({fmt(v)})" if v < 0 else fmt(v)


def box(kind, title, body):
    st.markdown(f'<div class="{kind}"><b>{title}</b><br>{body}</div>', unsafe_allow_html=True)


def render(n):
    q = simplify(4 * a * c)
    if n == 1:
        head(
            1,
            "Identificá los coeficientes",
            "Cada letra de ax² + bx + c = 0 tiene un nombre matemático. Cada una conserva su color hasta el final.",
        )
        st.markdown(
            f'<div class="trio"><div class="tcard" style="--k:{CA}"><div class="big">a = {fmt(a)}</div>'
            "<small><b>coeficiente cuadrático</b><br>va con x²</small></div>"
            f'<div class="tcard" style="--k:{CB}"><div class="big">b = {fmt(b)}</div>'
            "<small><b>coeficiente lineal</b><br>va con x</small></div>"
            f'<div class="tcard" style="--k:{CC}"><div class="big">c = {fmt(c)}</div>'
            "<small><b>término independiente</b><br>está solo, sin x</small></div></div>",
            unsafe_allow_html=True,
        )
        neg = [nm for nm, v in (("a", a), ("b", b), ("c", c)) if v < 0]
        box(
            "warn",
            "El signo viaja con el número",
            "Si ves −5x, entonces b = −5 (no 5). "
            + (f"En tu ecuación son negativos: <b>{', '.join(neg)}</b>." if neg else "En tu ecuación los tres son positivos."),
        )
        st.markdown(
            f'<div class="hint">En el gráfico, {chip("c", CC)} es donde la parábola corta el eje vertical.</div>',
            unsafe_allow_html=True,
        )
    elif n == 2:
        head(
            2,
            "Calculá el discriminante Δ",
            "Δ = b² − 4ac. Se calcula con la fórmula escrita, luego con los números entre paréntesis, y al final se resuelve.",
        )
        st.latex(r"\Delta = b^2 - 4\,a\,c")
        st.latex(rf"\Delta = {col(b, CB)}^2 - 4\cdot{col(a, CA)}\cdot{col(c, CC)}")
        st.latex(rf"\Delta = {latex(b**2)} - ({latex(q)})")
        if q < 0:
            st.latex(rf"\Delta = {latex(b**2)} + {latex(-q)} = {col(D, HOT)}")
        else:
            st.latex(rf"\Delta = {latex(b**2)} - {latex(q)} = {col(D, HOT)}")
        box(
            "warn",
            "Orden de las operaciones",
            "1° potencias · 2° multiplicaciones · 3° sumas y restas. Los números negativos van siempre entre paréntesis.",
        )
        if b < 0:
            st.latex(rf"({latex(b)})^2 = {latex(b**2)} \qquad \text{{pero}} \qquad -{latex(abs(b))}^2 = {latex(-b**2)}")
            box(
                "warn",
                "Cuidado con los paréntesis",
                f"Si escribís −{fmt(abs(b))}² la calculadora eleva solo el {fmt(abs(b))} y da <b>{fmt(-b**2)}</b>. "
                f"Con ({fmt(b)})² da <b>+{fmt(b**2)}</b>: un número al cuadrado nunca es negativo.",
            )
        if q < 0:
            box(
                "sign",
                "Acá cambia un signo",
                f"4·a·c = {fmt(q)} es negativo y la fórmula lo resta: −({fmt(q)}) = <b>+{fmt(-q)}</b>. «Menos por menos, más».",
            )
        elif q > 0:
            box("sign", "Signos sin cambio", f"4·a·c = {fmt(q)} es positivo, así que simplemente se resta.")
        st.markdown(f'<div class="hint">Resultado: {chip("Δ = " + fmt(D), HOT)}</div>', unsafe_allow_html=True)
    elif n == 3:
        head(3, "¿Qué te dice Δ?", "El discriminante decide cuántas veces la parábola toca el eje horizontal.")
        cls = ["on" if D > 0 else "", "on" if D == 0 else "", "on" if D < 0 else ""]
        st.markdown(
            f'<div class="meter" style="--k:{HOT}"><div class="{cls[0]}">Δ &gt; 0<br>dos soluciones</div>'
            f'<div class="{cls[1]}">Δ = 0<br>una solución</div><div class="{cls[2]}">Δ &lt; 0<br>ninguna real</div></div>'
            f'<div class="hint">Tu Δ vale {chip(fmt(D), HOT)}. Apareció el {chip("vértice", VTX)} y su eje de simetría '
            "(línea punteada) en el gráfico.</div>",
            unsafe_allow_html=True,
        )
    elif n == 4 and D < 0:
        head(4, "Conclusión", "No hace falta seguir calculando.")
        st.markdown(
            f'<div class="hint">Como {chip("Δ &lt; 0", HOT)} el radicando es negativo y no existe la raíz cuadrada '
            "de un negativo en los reales. La parábola nunca toca el eje x: <b>no hay solución real</b>.</div>",
            unsafe_allow_html=True,
        )
    elif n == 4:
        head(
            4,
            "Reemplazá en la fórmula resolvente",
            "Arriba está el numerador y abajo el denominador. Se reemplaza cuidando paréntesis y signos.",
        )
        st.latex(
            r"x=\dfrac{\overbrace{-b\pm\sqrt{\Delta}}^{\text{numerador (arriba)}}}"
            r"{\underbrace{2a}_{\text{denominador (abajo)}}}"
        )
        st.latex(rf"x = \dfrac{{-{col(b, CB)} \pm \sqrt{{{col(D, HOT)}}}}}{{2\cdot{col(a, CA)}}}")
        st.latex(rf"x = \dfrac{{{latex(-b)} \pm {latex(sqrt(D))}}}{{{latex(2*a)}}}")
        if b != 0:
            box(
                "sign",
                "Acá cambia un signo: −b es el opuesto de b",
                f"b = {fmt(b)}, entonces −b = −({fmt(b)}) = <b>{fmt(-b)}</b>. "
                + ("Como b era negativo, pasa a positivo." if b < 0 else "Como b era positivo, pasa a negativo."),
            )
        else:
            box("sign", "−b cuando b = 0", "El opuesto de 0 es 0: acá no hay cambio de signo.")
        box(
            "warn",
            "La barra de fracción es un paréntesis invisible",
            "Divide <b>todo</b> el numerador (−b ± √Δ), no solo el último término. En la calculadora se escribe así:<br>"
            f'<span class="calc">(-{p(b)} + √{fmt(D)}) ÷ (2·{p(a)})</span>',
        )
        box("sign", "El símbolo ±", "Significa «más o menos»: hacés el cálculo dos veces, una sumando √Δ y otra restándolo.")
    elif n == 5:
        head(5, "Calculá arriba y abajo", "Primero resolvé el numerador, después el denominador y recién al final dividí.")
        sq, den = sqrt(D), simplify(2 * a)
        if D == 0:
            st.latex(rf"x = \dfrac{{{latex(-b)}}}{{{latex(den)}}} = {col(x1, HOT)}")
        else:
            for sg, nm, r in (("+", "x_1", x1), ("-", "x_2", x2)):
                nu = simplify(-b + sq) if sg == "+" else simplify(-b - sq)
                st.markdown(
                    f'{chip("con " + ("+" if sg == "+" else "−"), HOT)} '
                    f'numerador: <b>{fmt(-b)} {"+" if sg == "+" else "−"} {fmt(sq) if sq.is_Rational else latex(sq)} = {fmt(nu) if nu.is_Rational else latex(nu)}</b>'
                    f" · denominador: <b>{fmt(den)}</b>",
                    unsafe_allow_html=True,
                )
                st.latex(
                    rf"{nm} = \dfrac{{{latex(-b)} {sg} {latex(sq)}}}{{{latex(den)}}} = \dfrac{{{latex(nu)}}}{{{latex(den)}}} = {col(r, HOT)}"
                )
        box(
            "warn",
            "Cuidado al restar",
            f"Con el signo − se resta √Δ al numerador: {fmt(-b)} − {fmt(sqrt(D)) if sqrt(D).is_Rational else latex(sqrt(D))}. "
            "Si el numerador queda negativo, el signo − es parte de la solución.",
        )
        st.markdown(
            f'<div class="hint">Son los puntos {chip("amarillos", HOT)} del gráfico: donde la parábola cruza el eje x.</div>',
            unsafe_allow_html=True,
        )
    elif n == 6:
        head(6, "Verificá", "Reemplazá cada solución en la ecuación original: tiene que dar 0.")
        for r in ([x1] if D == 0 else [x1, x2]):
            st.latex(
                rf"{col(a, CA)}\cdot({latex(r)})^2 + {col(b, CB)}\cdot({latex(r)}) + {col(c, CC)} "
                rf"= {latex(simplify(a*r**2 + b*r + c))}"
            )
        box(
            "warn",
            "Paréntesis al verificar",
            "Al reemplazar x por un número, ponelo entre paréntesis. El cuadrado se aplica al número con su signo, "
            "y después se resuelve en el orden: potencias, multiplicaciones, sumas y restas.",
        )
        st.markdown(
            '<div class="ok">¡Comprobado! Ahora la ecuación también se puede escribir factorizada:</div>',
            unsafe_allow_html=True,
        )
        if D == 0:
            st.latex(rf"{latex(a)}\,(x - {col(x1, HOT)})^2 = 0")
        else:
            st.latex(rf"{latex(a)}\,(x - {col(x1, HOT)})(x - {col(x2, HOT)}) = 0")


izq, der = st.columns([1, 1.25], gap="large")
with izq.container(key="stepcard"):
    render(paso)
    b1, b2 = st.columns(2)
    if b1.button("← Anterior", disabled=paso == 1, use_container_width=True):
        st.session_state.paso -= 1
        st.rerun()
    if b2.button("Siguiente →", disabled=paso == TOTAL, type="primary", use_container_width=True):
        st.session_state.paso += 1
        st.rerun()

with der.container(key="graphcard"):
    st.plotly_chart(
        grafico(paso),
        use_container_width=True,
        config={"scrollZoom": True, "displaylogo": False},
    )
    leg = chip("c · corta el eje y", CC)
    if paso >= 3:
        leg += chip("vértice", VTX)
    if paso >= 5 and raices:
        leg += chip("soluciones", HOT)
    st.markdown(f'<div class="legend">{leg}</div>', unsafe_allow_html=True)
    st.caption("Rueda del mouse para zoom, arrastrá para mover el gráfico.")

with st.expander("Glosario: los nombres matemáticos"):
    st.markdown(
        "- **Ecuación cuadrática** (o de segundo grado): ax² + bx + c = 0, con a ≠ 0.\n"
        "- **Coeficiente cuadrático (a)**, **coeficiente lineal (b)** y **término independiente (c)**.\n"
        "- **Discriminante (Δ)**: b² − 4ac. Dice cuántas soluciones reales hay.\n"
        "- **Radicando**: lo que está dentro de la raíz, acá Δ.\n"
        "- **Numerador** (arriba de la fracción) y **denominador** (abajo).\n"
        "- **Opuesto de b (−b)**: el mismo número con el signo cambiado.\n"
        "- **Raíces o soluciones**: los valores de x que hacen cierta la ecuación.\n"
        "- **Vértice** y **eje de simetría**: el punto más alto o más bajo de la parábola y la recta vertical que la parte en dos."
    )

st.markdown(
    '<div class="credit">Desarrollador App<br><b>Leonardo Olivera</b><br>Bachiller en Agronomía</div>',
    unsafe_allow_html=True,
)
