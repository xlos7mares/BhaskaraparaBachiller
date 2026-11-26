import numpy as np
import plotly.graph_objects as go
import streamlit as st
from sympy import Rational, latex, simplify, sqrt

st.set_page_config(page_title="Bhaskara paso a paso", page_icon="📈", layout="wide")

# Un color por coeficiente: el alumno los reconoce en todos los pasos
CA, CB, CC = "#2563eb", "#ea580c", "#16a34a"


def col(v, color):
    """Número o letra con color, en LaTeX; negativos entre paréntesis."""
    t = latex(v)
    if getattr(v, "is_negative", False):
        t = f"({t})"
    return rf"{{\color{{{color}}}{t}}}"


def num(x):
    return Rational(str(x))


# ---------------- Entrada ----------------
st.title("Resolvé ax² + bx + c = 0, paso a paso")

with st.sidebar:
    st.header("Tu ecuación")
    a_in = st.number_input("a (acompaña a x²)", value=1.0, step=1.0)
    b_in = st.number_input("b (acompaña a x)", value=-5.0, step=1.0)
    c_in = st.number_input("c (término solo)", value=6.0, step=1.0)
    ver_todo = st.checkbox("Mostrar todos los pasos juntos")

if a_in == 0:
    st.warning("Si a = 0 la ecuación no es cuadrática. Probá con a distinto de 0.")
    st.stop()

a, b, c = num(a_in), num(b_in), num(c_in)
D = b**2 - 4 * a * c
vx, vy = -b / (2 * a), c - b**2 / (4 * a)
if D >= 0:
    x1 = simplify((-b + sqrt(D)) / (2 * a))
    x2 = simplify((-b - sqrt(D)) / (2 * a))
    raices = sorted({float(x1), float(x2)})
else:
    x1 = x2 = None
    raices = []

TOTAL = 6 if D >= 0 else 4
firma = (a_in, b_in, c_in)
if st.session_state.get("firma") != firma:
    st.session_state.firma = firma
    st.session_state.paso = 1
paso = TOTAL if ver_todo else st.session_state.paso


# ---------------- Gráfico estilo GeoGebra ----------------
def grafico(paso):
    fa, fb, fc, fvx, fvy = map(float, (a, b, c, vx, vy))
    half = max([6] + [abs(r - fvx) + 2 for r in raices])
    xs = np.linspace(fvx - half, fvx + half, 600)
    ys = fa * xs**2 + fb * xs + fc
    f = go.Figure()
    f.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="f(x)",
                           line=dict(color="#7c3aed", width=3),
                           hovertemplate="x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>"))

    def punto(x, y, nombre, color):
        f.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text", text=[nombre], textposition="top right",
            marker=dict(size=11, color=color, line=dict(color="white", width=2)),
            hovertemplate=f"{nombre}<extra></extra>", showlegend=False))

    punto(0, fc, f"C(0, {fc:g})", CC)  # donde corta el eje y: es c
    if paso >= 3:
        f.add_vline(x=fvx, line=dict(color="#94a3b8", dash="dash", width=1.5))
        punto(fvx, fvy, f"V({fvx:.2f}, {fvy:.2f})", "#dc2626")
    if paso >= 5 and raices:
        for i, r in enumerate(raices, 1):
            punto(r, 0, f"x{i}={r:.2f}" if len(raices) > 1 else f"x={r:.2f}", "#0ea5e9")

    yspan = max(abs(fvy), abs(fc), 4)
    lo, hi = min(0, fvy, fc) - yspan * 0.4, max(0, fvy, fc) + yspan * 0.4
    if fa > 0:
        hi = max(hi, fvy + yspan * 1.5)
    else:
        lo = min(lo, fvy - yspan * 1.5)
    f.update_layout(
        height=520, margin=dict(l=10, r=10, t=10, b=10), showlegend=False,
        plot_bgcolor="white", dragmode="pan", hovermode="closest",
        xaxis=dict(range=[fvx - half, fvx + half], showgrid=True, gridcolor="#e5e7eb",
                   zeroline=True, zerolinecolor="#111", zerolinewidth=2, dtick=1),
        yaxis=dict(range=[lo, hi], showgrid=True, gridcolor="#e5e7eb",
                   zeroline=True, zerolinecolor="#111", zerolinewidth=2),
    )
    return f


# ---------------- Pasos ----------------
def render(n):
    if n == 1:
        st.subheader("Paso 1 · Identificá a, b y c")
        st.latex(rf"{col(a, CA)}x^2 + {col(b, CB)}x + {col(c, CC)} = 0")
        st.markdown(
            f"- **a** es el número que va con x² → :blue[**{latex(a)}**]\n"
            f"- **b** es el que va con x → :orange[**{latex(b)}**]\n"
            f"- **c** es el que está solo → :green[**{latex(c)}**]"
        )
        st.info("Mirá el gráfico: la parábola corta el eje y justo en **c**.")
    elif n == 2:
        st.subheader("Paso 2 · Calculá el discriminante")
        st.latex(r"\Delta = b^2 - 4ac")
        st.latex(rf"\Delta = {col(b, CB)}^2 - 4\cdot{col(a, CA)}\cdot{col(c, CC)} = {latex(D)}")
        st.caption("Δ es la «señal» que te dice cuántas soluciones hay.")
    elif n == 3:
        st.subheader("Paso 3 · ¿Qué te dice Δ?")
        st.latex(rf"\Delta = {latex(D)}")
        if D > 0:
            st.success("Δ > 0 → **dos soluciones reales**. La parábola corta el eje x en dos puntos.")
        elif D == 0:
            st.success("Δ = 0 → **una solución doble**. La parábola toca el eje x en el vértice.")
        else:
            st.error("Δ < 0 → **no hay soluciones reales**. La parábola nunca toca el eje x.")
        st.info("Apareció el vértice y su eje de simetría (línea punteada).")
    elif n == 4 and D < 0:
        st.subheader("Paso 4 · Conclusión")
        st.write("Como Δ es negativo, no existe √Δ en los reales: la ecuación **no tiene solución real**.")
    elif n == 4:
        st.subheader("Paso 4 · Reemplazá en la fórmula")
        st.latex(r"x = \dfrac{-b \pm \sqrt{\Delta}}{2a}")
        st.latex(rf"x = \dfrac{{-{col(b, CB)} \pm \sqrt{{{latex(D)}}}}}{{2\cdot{col(a, CA)}}}")
    elif n == 5:
        st.subheader("Paso 5 · Calculá las dos soluciones")
        if D == 0:
            st.latex(rf"x = {latex(x1)}")
        else:
            st.latex(rf"x_1 = \dfrac{{-b + \sqrt{{\Delta}}}}{{2a}} = {latex(x1)} \approx {float(x1):.3f}")
            st.latex(rf"x_2 = \dfrac{{-b - \sqrt{{\Delta}}}}{{2a}} = {latex(x2)} \approx {float(x2):.3f}")
        st.info("Las soluciones son los puntos donde la parábola cruza el eje x.")
    elif n ==
