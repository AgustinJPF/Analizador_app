"""Graficador matemático: funciones 2D, 3D y complejas, con sus soluciones.

Modos disponibles:
  * 2D  f(x)             -> curva; si hay parte imaginaria se grafican Re e Im.
  * 3D  f(x,y)           -> superficie z = f(x,y) y curva de ceros en rojo.
  * Complejo f(z)        -> plano complejo coloreado (tono = argumento,
                            brillo = módulo) con las raíces marcadas.
  * Complejo |f(z)| (3D) -> superficie del módulo, coloreada por el argumento.

Se puede escribir "i" (o "j") como unidad imaginaria, "^" como potencia y
multiplicación implícita ("2x", "3sin(x)").
"""
import re
import textwrap
import threading

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from matplotlib.colors import hsv_to_rgb
from matplotlib.widgets import RadioButtons, TextBox
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x, y, z = sp.symbols("x y z")
TRANSFORMACIONES = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)
RECT = [0.27, 0.30, 0.45, 0.65]  # posición del gráfico principal


# --------------------------------------------------------------------------
# Utilidades matemáticas
# --------------------------------------------------------------------------
def crear_funcion(texto, variables):
    """Convierte el texto en (expresión simbólica, función numérica)."""
    local = {v.name: v for v in variables}
    local.update({"i": sp.I, "j": sp.I, "e": sp.E})
    expr = parse_expr(texto, transformations=TRANSFORMACIONES, local_dict=local)
    sobrantes = expr.free_symbols - set(variables)
    if sobrantes:
        nombres = ", ".join(sorted(str(s) for s in sobrantes))
        raise ValueError(f"variable no permitida en este modo: {nombres}")
    return expr, sp.lambdify(variables, expr, modules=["numpy"])


def evaluar(f, *mallas):
    """Evalúa f con aritmética compleja; los valores no finitos pasan a NaN."""
    mallas = [np.asarray(m, dtype=complex) for m in mallas]
    with np.errstate(all="ignore"):
        w = f(*mallas)
    w = np.broadcast_to(np.asarray(w, dtype=complex), mallas[0].shape).copy()
    w[~np.isfinite(w)] = np.nan
    return w


def leer_rango(texto):
    """Interpreta 'min,max' y devuelve (min, max)."""
    a, b = (float(v) for v in texto.replace(";", ",").split(","))
    if a >= b:
        raise ValueError("el mínimo debe ser menor que el máximo")
    return a, b


def resolver(expr, variable, segundos=4):
    """Resuelve expr = 0 de forma exacta con un límite de tiempo.

    Devuelve la lista de soluciones o None si no se pudo resolver.
    """
    salida = {}

    def tarea():
        try:
            salida["sol"] = sp.solve(expr, variable)
        except Exception as error:  # noqa: BLE001
            salida["error"] = error

    hilo = threading.Thread(target=tarea, daemon=True)
    hilo.start()
    hilo.join(segundos)
    if hilo.is_alive() or "error" in salida:
        return None
    return salida["sol"]


def raices_reales(f, xmin, xmax, n=4000):
    """Raíces reales numéricas en [xmin, xmax] (cambios de signo + bisección)."""
    xs = np.linspace(xmin, xmax, n)
    w = evaluar(f, xs)
    ys = np.where(np.abs(w.imag) < 1e-9, w.real, np.nan)
    if not np.isfinite(ys).any():
        return np.array([])
    with np.errstate(all="ignore"):
        cambio = ys[:-1] * ys[1:] <= 0
    a, b, fa = xs[:-1][cambio], xs[1:][cambio], ys[:-1][cambio]
    if a.size == 0:
        return np.array([])
    for _ in range(60):
        m = (a + b) / 2
        fm = evaluar(f, m).real
        izquierda = fa * fm <= 0
        b = np.where(izquierda, m, b)
        a = np.where(izquierda, a, m)
        fa = np.where(izquierda, fa, fm)
    r = (a + b) / 2
    tol = 1e-6 * (1 + np.nanmedian(np.abs(ys)))
    r = r[np.abs(evaluar(f, r).real) <= tol]  # descarta asíntotas (1/x, tan)
    return np.unique(np.round(r, 6))


def formatear(valor):
    """Texto de una solución con su aproximación decimal."""
    texto = str(valor)
    try:
        if not valor.free_symbols:
            aprox = str(sp.N(valor, 6))
            if aprox != texto:
                texto += f"  ≈ {aprox}"
    except Exception:  # noqa: BLE001
        pass
    return re.sub(r"\bI\b", "i", texto)


def listar(soluciones, maximo=12):
    """Líneas de texto para mostrar una lista de soluciones."""
    if soluciones is None:
        return ["  (no se pudo resolver en forma exacta)"]
    if not soluciones:
        return ["  (sin soluciones)"]
    lineas = [f"  • {formatear(s)}" for s in soluciones[:maximo]]
    if len(soluciones) > maximo:
        lineas.append(f"  … y {len(soluciones) - maximo} más")
    return lineas


def colorear(w):
    """Colores del plano complejo: tono = arg(w), brillo = |w| (log)."""
    ok = np.isfinite(w)
    w0 = np.where(ok, w, 1)
    tono = (np.angle(w0) + np.pi) / (2 * np.pi)
    modulo = np.abs(w0)
    escalon = np.log2(modulo + 1e-300) % 1
    brillo = (0.6 + 0.4 * escalon) * (0.35 + 0.65 * modulo / (1 + modulo))
    rgb = hsv_to_rgb(np.dstack([tono, np.full_like(tono, 0.85), brillo]))
    rgb[~ok] = 0.5
    return rgb


# --------------------------------------------------------------------------
# Dibujo de cada modo: devuelven (ejes, líneas de texto con la solución)
# --------------------------------------------------------------------------
def dibujar_2d(fig, texto, rango):
    xmin, xmax = rango
    expr, f = crear_funcion(texto, (x,))
    xs = np.linspace(xmin, xmax, 2000)
    w = evaluar(f, xs)
    finitos = np.isfinite(w)
    if not finitos.any():
        raise ValueError("la función no tiene valores finitos en el rango")
    hay_im = np.max(np.abs(w.imag[finitos])) > 1e-9 * (1 + np.max(np.abs(w[finitos])))

    ax = fig.add_axes(RECT)
    ax.axhline(0, color="black", lw=0.8)
    ax.axvline(0, color="black", lw=0.8)
    ax.grid(True, alpha=0.3)
    ax.plot(xs, w.real, color="red", lw=2, label="Re f(x)")
    valores = w.real[finitos]
    if hay_im:
        ax.plot(xs, w.imag, color="blue", lw=2, ls="--", label="Im f(x)")
        valores = np.concatenate([valores, w.imag[finitos]])
        ax.legend(loc="best")
    ax.set_xlim(xmin, xmax)
    bajo, alto = np.percentile(valores, [2, 98])
    margen = (alto - bajo) * 0.15 or 1
    ax.set_ylim(bajo - margen, alto + margen)
    ax.set_title(f"f(x) = {texto}")

    reales = raices_reales(f, xmin, xmax)
    ax.plot(reales, np.zeros_like(reales), "ko", label="raíces")
    lineas = [f"f(x) = {texto}", "", "Soluciones exactas de f(x)=0:"]
    lineas += listar(resolver(expr, x))
    lineas += ["", "Raíces reales en el intervalo:"]
    lineas += ([f"  • x ≈ {r + 0.0:.6g}" for r in reales[:12]] or ["  (ninguna)"])
    if hay_im:
        lineas += ["", "La función toma valores complejos:", "se grafican Re (rojo) e Im (azul)."]
    return ax, lineas


def dibujar_3d(fig, texto, rango):
    lo, hi = rango
    expr, f = crear_funcion(texto, (x, y))
    g = np.linspace(lo, hi, 80)
    X, Y = np.meshgrid(g, g)
    w = evaluar(f, X, Y)
    Z = np.where(np.abs(w.imag) < 1e-9, w.real, np.nan)
    ok = np.isfinite(Z)
    if not ok.any():
        raise ValueError("no hay valores reales finitos en el rango")
    zmin, zmax = Z[ok].min(), Z[ok].max()
    bajo, alto = np.percentile(Z[ok], [1, 99])
    margen = (alto - bajo) * 0.1 or 1
    with np.errstate(all="ignore"):
        Z = np.where((Z >= bajo - margen) & (Z <= alto + margen), Z, np.nan)

    ax = fig.add_axes(RECT, projection="3d")
    ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none", alpha=0.9)
    if np.nanmin(Z) < 0 < np.nanmax(Z):
        ax.contour(X, Y, Z, levels=[0], colors="red", linewidths=2, zdir="z", offset=0)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(f"z = {texto}")

    lineas = [f"z = {texto}", "", "Curva de ceros f(x,y)=0 (roja):"]
    usadas = [v for v in (y, x) if v in expr.free_symbols]
    for v in usadas:
        lineas.append(f"Despejando {v}:")
        lineas += listar(resolver(expr, v), maximo=6)
    if not usadas:
        lineas.append("  (función constante)")
    lineas += ["", f"z mínimo ≈ {zmin:.6g}", f"z máximo ≈ {zmax:.6g}"]
    return ax, lineas


def _raices_complejas(expr, lineas):
    """Soluciones de f(z)=0; agrega líneas de texto y devuelve los puntos."""
    sols = resolver(expr, z)
    lineas += listar(sols)
    puntos = []
    for s in sols or []:
        try:
            puntos.append(complex(sp.N(s)))
        except Exception:  # noqa: BLE001
            pass
    return puntos


def dibujar_complejo_plano(fig, texto, rango):
    lo, hi = rango
    expr, f = crear_funcion(texto, (z,))
    g = np.linspace(lo, hi, 600)
    X, Y = np.meshgrid(g, g)
    w = evaluar(f, X + 1j * Y)

    ax = fig.add_axes(RECT)
    ax.imshow(colorear(w), extent=[lo, hi, lo, hi], origin="lower", interpolation="bilinear")
    ax.set_xlabel("Re(z)")
    ax.set_ylabel("Im(z)")
    ax.set_title(f"f(z) = {texto}\ntono = argumento, brillo = |f|", fontsize=10)

    lineas = [f"f(z) = {texto}", "", "Soluciones exactas de f(z)=0:"]
    for c in _raices_complejas(expr, lineas):
        if lo <= c.real <= hi and lo <= c.imag <= hi:
            ax.plot(c.real, c.imag, "o", mfc="white", mec="black", ms=7)
    lineas += ["", "Círculos blancos = raíces en la ventana."]
    return ax, lineas


def dibujar_complejo_3d(fig, texto, rango):
    lo, hi = rango
    expr, f = crear_funcion(texto, (z,))
    g = np.linspace(lo, hi, 150)
    X, Y = np.meshgrid(g, g)
    w = evaluar(f, X + 1j * Y)
    modulo = np.abs(w)
    ok = np.isfinite(modulo)
    if not ok.any():
        raise ValueError("no hay valores finitos en el rango")
    tope = np.percentile(modulo[ok], 95) * 1.5 or 1
    altura = np.clip(np.where(ok, modulo, 0), 0, tope)
    colores = np.dstack([colorear(w), np.ones(w.shape)])

    ax = fig.add_axes(RECT, projection="3d")
    ax.plot_surface(X, Y, altura, facecolors=colores, shade=False,
                    linewidth=0, antialiased=False)
    ax.set_xlabel("Re(z)")
    ax.set_ylabel("Im(z)")
    ax.set_zlabel("|f(z)|")
    ax.set_title(f"|f(z)|, f(z) = {texto}", fontsize=10)

    lineas = [f"f(z) = {texto}", "", "Soluciones exactas de f(z)=0:"]
    _raices_complejas(expr, lineas)
    lineas += ["", "Altura = |f(z)| (recortada),", "color = argumento de f(z)."]
    return ax, lineas


MODOS = {
    "2D  f(x)": dict(vars="x", funcion="x**2 - 3*x + 2", rango="-10,10", dibujar=dibujar_2d),
    "3D  f(x,y)": dict(vars="x,y", funcion="sin(x)*cos(y)", rango="-5,5", dibujar=dibujar_3d),
    "Complejo  f(z)  plano": dict(vars="z", funcion="z**3 - 1", rango="-2,2",
                                  dibujar=dibujar_complejo_plano),
    "Complejo  |f(z)|  3D": dict(vars="z", funcion="z**3 - 1", rango="-2,2",
                                 dibujar=dibujar_complejo_3d),
}


# --------------------------------------------------------------------------
# Interfaz
# --------------------------------------------------------------------------
def main():
    # Libera las teclas de atajo de matplotlib para poder escribir en las cajas.
    for clave in [k for k in plt.rcParams if k.startswith("keymap.")]:
        plt.rcParams[clave] = []

    fig = plt.figure(figsize=(13, 7))
    primero = next(iter(MODOS))
    estado = {
        "modo": primero,
        "funcion": MODOS[primero]["funcion"],
        "rango": MODOS[primero]["rango"],
        "ax": None,
        "silencio": False,
    }

    panel = fig.add_axes([0.74, 0.30, 0.25, 0.65])
    panel.axis("off")
    panel.set_title("Solución", fontsize=10, loc="left")
    texto_panel = panel.text(0, 1, "", va="top", family="monospace", fontsize=8)

    def actualizar():
        if estado["ax"] is not None:
            estado["ax"].remove()
        try:
            rango = leer_rango(estado["rango"])
            ax, lineas = MODOS[estado["modo"]]["dibujar"](fig, estado["funcion"], rango)
        except Exception as error:  # noqa: BLE001
            ax = fig.add_axes(RECT)
            ax.grid(True, alpha=0.3)
            ax.set_title(f"Error: {error}", color="red", fontsize=9)
            lineas = ["Error:", str(error)]
        estado["ax"] = ax
        texto_panel.set_text("\n".join(
            textwrap.fill(linea, 40, subsequent_indent="      ") for linea in lineas
        ))
        print("\n".join(lineas), "\n" + "-" * 40)
        fig.canvas.draw_idle()

    def al_cambiar_modo(etiqueta):
        datos = MODOS[etiqueta]
        estado.update(modo=etiqueta, funcion=datos["funcion"], rango=datos["rango"])
        estado["silencio"] = True
        caja_f.label.set_text(f"f({datos['vars']}) = ")
        caja_f.set_val(datos["funcion"])
        caja_r.set_val(datos["rango"])
        estado["silencio"] = False
        actualizar()

    def al_cambiar_funcion(texto):
        if not estado["silencio"]:
            estado["funcion"] = texto
            actualizar()

    def al_cambiar_rango(texto):
        if not estado["silencio"]:
            estado["rango"] = texto
            actualizar()

    ax_radio = fig.add_axes([0.02, 0.45, 0.22, 0.30])
    ax_radio.set_title("Modo", fontsize=10)
    radio = RadioButtons(ax_radio, list(MODOS), active=0)
    for etiqueta in radio.labels:
        etiqueta.set_fontsize(9)
    radio.on_clicked(al_cambiar_modo)

    caja_f = TextBox(fig.add_axes([0.30, 0.14, 0.62, 0.05]), "f(x) = ",
                     initial=estado["funcion"])
    caja_r = TextBox(fig.add_axes([0.30, 0.06, 0.62, 0.05]),
                     "intervalo [min, max] = ", initial=estado["rango"])
    caja_f.on_submit(al_cambiar_funcion)
    caja_r.on_submit(al_cambiar_rango)

    actualizar()
    plt.show()
    return radio, caja_f, caja_r  # se devuelven para que no los borre el recolector


if __name__ == "__main__":
    widgets = main()