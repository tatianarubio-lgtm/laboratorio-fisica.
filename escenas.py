import math
import flet as ft
import flet.canvas as cv

import paleta
import dibujo as dib
from temas import TEMAS
from calculos import G


# ==========================================
# TAMAÑOS Y CONSTANTES VISUALES
# ==========================================

W_ESC, H_ESC = 580, 320        # escena animada
W_BAR, H_BAR = 150, 320        # barras de energía
W_GRAF, H_GRAF = 730, 170      # gráfica en el tiempo

Y_SUELO = 250                  # altura del piso (píxeles)
ESC_M = 14                     # píxeles por metro (movimiento horizontal)
COL_F = "#DC2626"              # color del vector fuerza

# Pista parabólica (energía mecánica): y = C * x²
C_PISTA = 0.2
X_MAX = 10.0
SX, SY = 26, 10.5
CX_PISTA, Y_BASE = 290, 285


def fmt(v):
    return f"{v:.0f}" if abs(v) >= 10 else f"{v:.1f}"


def _suelo():
    return [
        dib.rect(0, Y_SUELO, W_ESC, H_ESC - Y_SUELO, "#CBD5E1"),
        dib.rect(0, Y_SUELO, W_ESC, 4, "#94A3B8"),
    ]


# ==========================================
# CREAR ESCENA (CONTENEDORES)
# ==========================================

def crear_escena():

    titulo = ft.Text(
        "Laboratorio de Física", size=22,
        weight=ft.FontWeight.BOLD, color=paleta.AZUL_OSCURO
    )

    descripcion = ft.Text(
        "Selecciona un tema para comenzar el experimento.",
        size=14, color=paleta.TEXTO_SECUNDARIO
    )

    formula = ft.Text(
        "", size=22, weight=ft.FontWeight.BOLD, color=paleta.AZUL
    )

    canvas_escena = cv.Canvas(shapes=[], width=W_ESC, height=H_ESC)
    canvas_barras = cv.Canvas(shapes=[], width=W_BAR, height=H_BAR)
    canvas_grafica = cv.Canvas(shapes=[], width=W_GRAF, height=H_GRAF)

    informacion = ft.Text(
        "Modifica los controles para observar los cambios.",
        size=14, color=paleta.TEXTO_OSCURO
    )

    fila = ft.Row(
        controls=[
            ft.Container(
                content=canvas_escena,
                width=W_ESC, height=H_ESC,
                bgcolor="#F0F7FF",
                border_radius=15,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            ),
            ft.Container(
                content=canvas_barras,
                width=W_BAR, height=H_BAR,
                bgcolor=paleta.FONDO_PANEL,
                border=ft.Border.all(1, paleta.BORDE),
                border_radius=15,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
    )

    grafica = ft.Container(
        content=canvas_grafica,
        width=W_GRAF, height=H_GRAF,
        bgcolor=paleta.FONDO_PANEL,
        border=ft.Border.all(1, paleta.BORDE),
        border_radius=15,
        clip_behavior=ft.ClipBehavior.HARD_EDGE
    )

    panel = ft.Container(
        content=ft.Column(
            controls=[
                titulo,
                descripcion,
                ft.Divider(),
                fila,
                ft.Container(content=formula, alignment=ft.Alignment.CENTER),
                grafica,
                ft.Container(
                    content=informacion,
                    padding=12,
                    bgcolor=paleta.AZUL_CLARO,
                    border_radius=12,
                    width=W_GRAF
                )
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        bgcolor=paleta.BLANCO,
        border=ft.Border.all(1, paleta.BORDE),
        border_radius=18
    )

    return {
        "panel": panel,
        "titulo": titulo,
        "descripcion": descripcion,
        "formula": formula,
        "informacion": informacion,
        "canvas_escena": canvas_escena,
        "canvas_barras": canvas_barras,
        "canvas_grafica": canvas_grafica,
        "estado": {
            "t": 0.0,
            "tema": None,
            "mec": None,
            "hist": {"t": [], "vals": {}}
        }
    }


# ==========================================
# CONTROL DEL TIEMPO Y CAMBIO DE TEMA
# ==========================================

def reiniciar_escena(escena):
    est = escena["estado"]
    est["t"] = 0.0
    est["hist"] = {"t": [], "vals": {}}


def cambiar_escena(escena, tema_id):
    tema = TEMAS[tema_id]
    est = escena["estado"]

    escena["titulo"].value = tema["nombre"]
    escena["descripcion"].value = tema["descripcion"]
    escena["formula"].value = tema["formula"]
    escena["formula"].color = tema["color"]

    if est["tema"] != tema_id:
        est["tema"] = tema_id
        est["mec"] = None

    reiniciar_escena(escena)


# ==========================================
# BARRAS DE ENERGÍA
# ==========================================

def dibujar_barras(vivo):
    barras = vivo["barras"]
    ymin, ymax = vivo["rango_barras"]
    unidad = vivo["unidad"]

    top, alto = 55, 200
    escala = alto / (ymax - ymin)
    y_base = top + ymax * escala

    formas = [
        dib.texto(12, 12, "Barras de", 13, paleta.AZUL_OSCURO, True),
        dib.texto(12, 28, f"valor ({unidad})", 12, paleta.TEXTO_SECUNDARIO),
    ]

    n = len(barras)
    ancho = 34
    hueco = (W_BAR - n * ancho) / (n + 1)

    for i, (nombre, valor, color) in enumerate(barras):
        x = hueco + i * (ancho + hueco)
        h = abs(valor) * escala
        if valor >= 0:
            formas.append(dib.rect(x, y_base - h, ancho, h, color, 4))
            y_val = y_base - h - 16
        else:
            formas.append(dib.rect(x, y_base, ancho, h, color, 4))
            y_val = y_base + h + 2
        formas.append(dib.texto(x - 4, max(y_val, 44), fmt(valor), 12,
                                color, True))
        formas.append(dib.texto(x + 2, top + alto + 12, nombre, 12,
                                paleta.TEXTO_OSCURO, True))

    formas.append(dib.linea(8, y_base, W_BAR - 8, y_base, "#64748B", 2))
    return formas


# ==========================================
# GRÁFICA EN EL TIEMPO
# ==========================================

def dibujar_grafica(est, vivo):
    ml, mt, pw, ph = 60, 14, 540, 115
    ymin, ymax = vivo["rango"]
    T = vivo["T"]
    hist = est["hist"]

    def X(t):
        return ml + (t / T) * pw

    def Y(v):
        y = mt + ph - (v - ymin) / (ymax - ymin) * ph
        return max(mt, min(mt + ph, y))

    formas = [
        dib.rect(ml, mt, pw, ph, "#FFFFFF"),
        dib.rect_borde(ml, mt, pw, ph, paleta.BORDE, 1),
        dib.texto(4, mt - 6, f"{fmt(ymax)} {vivo['unidad']}", 11,
                  paleta.TEXTO_SECUNDARIO),
        dib.texto(4, mt + ph - 8, f"{fmt(ymin)}", 11,
                  paleta.TEXTO_SECUNDARIO),
        dib.texto(ml - 2, mt + ph + 8, "0", 11, paleta.TEXTO_SECUNDARIO),
        dib.texto(ml + pw / 2 - 40, mt + ph + 8, "tiempo (s)", 11,
                  paleta.TEXTO_SECUNDARIO),
        dib.texto(ml + pw - 22, mt + ph + 8, f"{T:.1f}", 11,
                  paleta.TEXTO_SECUNDARIO),
    ]

    if ymin < 0 < ymax:
        formas.append(dib.linea(ml, Y(0), ml + pw, Y(0), "#94A3B8", 1, True))

    for i, (nombre, valor, color) in enumerate(vivo["series"]):
        valores = hist["vals"].get(nombre, [])
        puntos = [(X(tt), Y(v)) for tt, v in zip(hist["t"], valores)]
        linea = dib.polilinea(puntos, color, 3)
        if linea is not None:
            formas.append(linea)
            formas.append(dib.circulo(puntos[-1][0], puntos[-1][1], 4, color))

        # Leyenda
        ly = mt + 8 + i * 24
        formas.append(dib.linea(ml + pw + 14, ly + 6, ml + pw + 34, ly + 6,
                                color, 4))
        formas.append(dib.texto(ml + pw + 40, ly, nombre, 11,
                                paleta.TEXTO_OSCURO))

    return formas


# ==========================================
# ESCENA 1: TRABAJO
# ==========================================

def _escena_trabajo(t, p, est, dt):
    m, F = p["masa"], p["fuerza"]
    dist, ang = p["distancia"], p["angulo"]

    th = math.radians(ang)
    c, s = math.cos(th), math.sin(th)

    T_mov = 4.0
    T = T_mov + 1.5
    rec = dist * min(t / T_mov, 1.0)

    formas = _suelo()
    car, (cx, cy), w, h = dib.carrito(30 + rec * ESC_M, Y_SUELO, m,
                                      paleta.COLOR_TRABAJO)
    c0 = 30 + w / 2

    # Línea de inicio y desplazamiento
    formas.append(dib.linea(c0, Y_SUELO - 90, c0, Y_SUELO + 32,
                            "#94A3B8", 1, True))
    formas.append(dib.texto(c0 - 14, Y_SUELO + 36, "inicio", 11,
                            paleta.TEXTO_SECUNDARIO))
    formas += car
    formas += dib.flecha(c0, Y_SUELO + 24, cx, Y_SUELO + 24,
                         paleta.AZUL_OSCURO, 3)
    if rec > 0.2:
        formas.append(dib.texto((c0 + cx) / 2 - 28, Y_SUELO + 30,
                                f"d = {rec:.1f} m", 12,
                                paleta.AZUL_OSCURO, True))

    # Fuerza y su componente paralela
    y0 = cy - h / 2
    L = min(F * 0.6, 130)
    tx, ty = cx + L * c, y0 - L * s
    if F > 0:
        formas += dib.flecha(cx, y0, tx, ty, COL_F, 4)
        formas.append(dib.texto(tx + 6, ty - 16, f"F = {F:.0f} N", 12,
                                COL_F, True))
        if 2 < ang < 178:
            formas.append(dib.linea(tx, ty, tx, y0, "#94A3B8", 1, True))
            formas += dib.flecha(cx, y0, tx, y0, paleta.COLOR_CINETICA, 4)
            formas.append(dib.texto(cx + 20, y0 - 14, f"θ = {ang:.0f}°", 11,
                                    paleta.TEXTO_SECUNDARIO))

    # Leyenda
    formas.append(dib.texto(12, 10, "━ F (fuerza aplicada)", 12, COL_F, True))
    formas.append(dib.texto(12, 28, "━ F·cos(θ) (parte que hace trabajo)", 12,
                            paleta.COLOR_CINETICA, True))

    W = F * rec * c
    Wt = F * dist * c
    lo, hi = min(0, Wt), max(0, Wt)
    if hi - lo < 1e-9:
        hi = lo + 1

    if abs(ang - 90) < 0.5:
        nota = "La fuerza es perpendicular al movimiento: no realiza trabajo."
    elif ang > 90:
        nota = "cos(θ) es negativo: la fuerza se opone al movimiento (trabajo negativo)."
    elif ang < 0.5:
        nota = "Fuerza paralela al desplazamiento: se aprovecha toda la fuerza."
    else:
        nota = "Solo la componente F·cos(θ), paralela al movimiento, hace trabajo."

    vivo = {
        "T": T, "unidad": "J",
        "rango": (lo, hi), "rango_barras": (lo, hi),
        "barras": [("W", W, paleta.COLOR_TRABAJO)],
        "series": [("W (trabajo)", W, paleta.COLOR_TRABAJO)],
        "texto": (
            f"Recorrido: {rec:.1f} m de {dist:.1f} m\n"
            f"W = F · d · cos(θ) = {F:.0f} × {rec:.1f} × cos({ang:.0f}°) "
            f"= {W:.1f} J\n"
            f"{nota}"
        )
    }
    return formas, vivo


# ==========================================
# ESCENA 2: ENERGÍA CINÉTICA
# ==========================================

def _escena_cinetica(t, p, est, dt):
    m, v = p["masa"], p["velocidad"]

    Ta, Th = 3.0, 2.5
    T = Ta + Th
    a = v / Ta
    if t < Ta:
        vt = a * t
        s = 0.5 * a * t * t
    else:
        vt = v
        s = 0.5 * a * Ta * Ta + v * (t - Ta)

    ec = 0.5 * m * vt * vt
    ec_max = 0.5 * m * v * v

    formas = _suelo()

    # Montañas de fondo (se mueven lento: efecto de profundidad)
    desp = (s * 2) % 300
    for i in range(-1, 4):
        bx = i * 300 - desp
        formas.append(dib.poligono(
            [(bx, Y_SUELO), (bx + 110, Y_SUELO - 90), (bx + 220, Y_SUELO)],
            "#DBEAFE"))

    # Marcas de la carretera
    desp_r = (s * 12) % 90
    for i in range(-1, 8):
        formas.append(dib.rect(i * 90 - desp_r, Y_SUELO + 30, 50, 6,
                               "#F8FAFC", 3))

    # Carrito fijo en pantalla
    x_car = 200
    car, (cx, cy), w, h = dib.carrito(x_car, Y_SUELO, m,
                                      paleta.COLOR_CINETICA)

    # Líneas de velocidad
    largo = vt * 3
    for k, dy in enumerate((-18, 0, 14)):
        if largo > 6:
            formas.append(dib.linea(x_car - 8 - largo * (0.6 + 0.2 * k),
                                    cy + dy, x_car - 8, cy + dy,
                                    "#94A3B8", 2))
    formas += car

    # Vector velocidad
    formas += dib.flecha(cx, cy - h / 2 - 14, cx + vt * 6, cy - h / 2 - 14,
                         paleta.COLOR_CINETICA, 4)
    formas.append(dib.texto(cx - 10, cy - h / 2 - 40,
                            f"v = {vt:.1f} m/s ({vt * 3.6:.0f} km/h)", 13,
                            paleta.COLOR_CINETICA, True))

    formas.append(dib.texto(12, 10,
                            "El carrito acelera desde el reposo hasta v", 12,
                            paleta.TEXTO_SECUNDARIO))

    rango = (0, ec_max if ec_max > 1e-9 else 1)
    vivo = {
        "T": T, "unidad": "J",
        "rango": rango, "rango_barras": rango,
        "barras": [("Ec", ec, paleta.COLOR_CINETICA)],
        "series": [("Ec (cinética)", ec, paleta.COLOR_CINETICA)],
        "texto": (
            f"Ec = ½ · m · v² = ½ × {m:.1f} × {vt:.1f}² = {ec:.1f} J\n"
            f"Si la velocidad se duplica, la energía cinética se cuadruplica.\n"
            f"Teorema trabajo-energía: el trabajo neto realizado sobre el "
            f"carrito es W = ΔEc = {ec:.1f} J."
        )
    }
    return formas, vivo


# ==========================================
# ESCENA 3: ENERGÍA POTENCIAL GRAVITACIONAL
# ==========================================

def _escena_gravitacional(t, p, est, dt):
    m, h = p["masa"], p["altura"]

    ESC = 9.5
    factor = 0.5                         # cámara lenta
    tf = math.sqrt(2 * h / G) if h > 0 else 0.0
    espera, cierre = 1.2, 1.5
    caida = tf / factor
    T = espera + caida + cierre

    if t < espera:
        ts = 0.0
    elif t < espera + caida:
        ts = (t - espera) * factor
    else:
        ts = tf

    y = max(h - 0.5 * G * ts * ts, 0.0)
    v = G * ts

    r = 10 + m * 0.7
    bx = 300
    by = Y_SUELO - r - y * ESC

    formas = _suelo()

    # Regla de alturas
    formas.append(dib.linea(90, Y_SUELO, 90, Y_SUELO - max(h, 1) * ESC,
                            "#64748B", 2))
    for k in range(0, int(h // 5) + 1):
        yk = Y_SUELO - 5 * k * ESC
        formas.append(dib.linea(84, yk, 96, yk, "#64748B", 2))
        formas.append(dib.texto(50, yk - 7, f"{5 * k} m", 11,
                                paleta.TEXTO_SECUNDARIO))

    # Nivel inicial
    y_ini = Y_SUELO - h * ESC
    formas.append(dib.linea(90, y_ini, 520, y_ini, paleta.COLOR_GRAVITACIONAL,
                            1, True))
    formas.append(dib.texto(400, y_ini - 18, f"nivel inicial: h = {h:.1f} m",
                            12, paleta.COLOR_GRAVITACIONAL, True))

    # Imágenes estroboscópicas (muestran cómo aumenta la velocidad)
    k = 1
    while 0.15 * k < ts:
        yk = max(h - 0.5 * G * (0.15 * k) ** 2, 0)
        formas.append(dib.circulo(bx, Y_SUELO - r - yk * ESC, r,
                                  dib.transparente(
                                      paleta.COLOR_GRAVITACIONAL, "30")))
        k += 1

    # Pelota
    formas.append(dib.circulo(bx, by, r, paleta.COLOR_GRAVITACIONAL))
    formas.append(dib.circulo(bx - r * 0.3, by - r * 0.3, r * 0.25,
                              "#66FFFFFF"))
    formas.append(dib.texto(bx - 16, by - 6, f"{m:.1f} kg", 11,
                            "#FFFFFF", True))

    # Altura actual y vector velocidad
    if y > 0.05:
        formas.append(dib.linea(bx + r + 12, by + r, bx + r + 12, Y_SUELO,
                                "#94A3B8", 1, True))
        formas.append(dib.texto(bx + r + 18, (by + r + Y_SUELO) / 2 - 6,
                                f"y = {y:.1f} m", 12,
                                paleta.TEXTO_SECUNDARIO))
    formas += dib.flecha(bx, by + r + 4, bx, by + r + 4 + min(v * 3, 70),
                         paleta.COLOR_CINETICA, 4)
    if v > 0.1:
        formas.append(dib.texto(bx - 90, by + r + 6, f"v = {v:.1f} m/s", 12,
                                paleta.COLOR_CINETICA, True))

    epg = m * G * y
    ec = 0.5 * m * v * v
    em = m * G * h
    rango = (0, em if em > 1e-9 else 1)

    vivo = {
        "T": T, "unidad": "J",
        "rango": rango, "rango_barras": rango,
        "barras": [
            ("Epg", epg, paleta.COLOR_GRAVITACIONAL),
            ("Ec", ec, paleta.COLOR_CINETICA),
            ("Em", epg + ec, paleta.COLOR_MECANICA),
        ],
        "series": [
            ("Epg (gravitacional)", epg, paleta.COLOR_GRAVITACIONAL),
            ("Ec (cinética)", ec, paleta.COLOR_CINETICA),
            ("Em (mecánica)", epg + ec, paleta.COLOR_MECANICA),
        ],
        "texto": (
            f"Epg = m · g · y = {m:.1f} × 9.81 × {y:.1f} = {epg:.1f} J\n"
            f"Ec = ½ · m · v² = {ec:.1f} J\n"
            f"Al caer, la energía potencial se transforma en cinética; "
            f"la suma Em = {epg + ec:.1f} J se mantiene constante."
        )
    }
    return formas, vivo


# ==========================================
# ESCENA 4: ENERGÍA POTENCIAL ELÁSTICA
# ==========================================

def _escena_elastica(t, p, est, dt):
    m, k, x0 = p["masa"], p["constante"], p["compresion"]

    omega = math.sqrt(k / m)
    periodo = 2 * math.pi / omega
    fac = min(1.0, periodo / 3.0)          # cámara lenta si es muy rápido
    periodo_vis = periodo / fac
    espera = 1.0
    T = espera + 2 * periodo_vis
    ts = max(t - espera, 0.0) * fac

    x = -x0 * math.cos(omega * ts)         # desplazamiento (negativo = comprime)
    v = x0 * omega * math.sin(omega * ts)

    ESC_X = 200
    pared_x = 30
    x_eq = pared_x + 14 + 240
    formas = _suelo()

    # Pared
    formas.append(dib.rect(pared_x, Y_SUELO - 110, 14, 110, "#64748B"))
    for i in range(6):
        formas.append(dib.linea(pared_x, Y_SUELO - 105 + i * 20,
                                pared_x - 10, Y_SUELO - 95 + i * 20,
                                "#64748B", 2))

    # Bloque
    x_blq = x_eq + x * ESC_X
    car, (cx, cy), w, h = dib.carrito(x_blq, Y_SUELO, m, paleta.COLOR_ELASTICA)

    # Posición de equilibrio
    formas.append(dib.linea(x_eq, Y_SUELO - 125, x_eq, Y_SUELO + 6,
                            "#94A3B8", 1, True))
    formas.append(dib.texto(x_eq - 30, Y_SUELO - 142, "equilibrio (x = 0)",
                            11, paleta.TEXTO_SECUNDARIO))

    # Resorte y bloque
    formas += dib.resorte(pared_x + 14, x_blq, cy, paleta.COLOR_ELASTICA)
    formas += car

    # Desplazamiento x
    y_d = Y_SUELO - 100
    formas += dib.flecha(x_eq, y_d, x_blq, y_d, paleta.AZUL_OSCURO, 3)
    formas.append(dib.texto(min(x_eq, x_blq) + abs(x_blq - x_eq) / 2 - 30,
                            y_d - 20, f"x = {x:+.2f} m", 12,
                            paleta.AZUL_OSCURO, True))

    # Vector velocidad
    if abs(v) > 0.05:
        formas += dib.flecha(cx, cy - h / 2 - 12, cx + v * 10, cy - h / 2 - 12,
                             paleta.COLOR_CINETICA, 4)

    estado = "comprimido" if x < -0.005 else ("estirado" if x > 0.005 else
                                              "en equilibrio")
    formas.append(dib.texto(12, 10, f"Resorte {estado}", 12,
                            paleta.TEXTO_SECUNDARIO, True))
    if fac < 1:
        formas.append(dib.texto(12, 28, "(cámara lenta)", 11,
                                paleta.TEXTO_SECUNDARIO))

    epe = 0.5 * k * x * x
    ec = 0.5 * m * v * v
    em = 0.5 * k * x0 * x0
    rango = (0, em if em > 1e-9 else 1)

    vivo = {
        "T": T, "unidad": "J",
        "rango": rango, "rango_barras": rango,
        "barras": [
            ("Epe", epe, paleta.COLOR_ELASTICA),
            ("Ec", ec, paleta.COLOR_CINETICA),
            ("Em", epe + ec, paleta.COLOR_MECANICA),
        ],
        "series": [
            ("Epe (elástica)", epe, paleta.COLOR_ELASTICA),
            ("Ec (cinética)", ec, paleta.COLOR_CINETICA),
            ("Em (mecánica)", epe + ec, paleta.COLOR_MECANICA),
        ],
        "texto": (
            f"Epe = ½ · k · x² = ½ × {k:.0f} × {x:.2f}² = {epe:.2f} J\n"
            f"Ec = ½ · m · v² = {ec:.2f} J   (v = {abs(v):.2f} m/s)\n"
            f"En los extremos toda la energía es elástica; al pasar por el "
            f"equilibrio toda es cinética. Em = {epe + ec:.2f} J."
        )
    }
    return formas, vivo


# ==========================================
# ESCENA 5: ENERGÍA MECÁNICA (PISTA)
# ==========================================

def _pista_px(x):
    """Punto de la pista en píxeles para x en metros."""
    return CX_PISTA + x * SX, Y_BASE - C_PISTA * x * x * SY


def _escena_mecanica(t, p, est, dt):
    m, h0, v0 = p["masa"], p["altura"], p["velocidad"]

    # --- Estado de la simulación ---
    clave = (round(m, 3), round(h0, 3), round(v0, 3))
    mec = est.get("mec")
    if mec is None or mec["clave"] != clave:
        x0 = -math.sqrt(h0 / C_PISTA) if h0 > 0 else 0.0
        x0 = max(x0, -X_MAX)
        s0 = 1 + 4 * C_PISTA ** 2 * x0 * x0
        mec = {
            "clave": clave,
            "x": x0,
            "xd": v0 / math.sqrt(s0),
            "e0": G * C_PISTA * x0 * x0 + 0.5 * v0 * v0   # energía por masa
        }
        est["mec"] = mec

    # --- Integración (cámara lenta 0.4x) ---
    if dt > 0:
        n = 20
        hs = dt * 0.4 / n
        x, xd, e0 = mec["x"], mec["xd"], mec["e0"]
        for _ in range(n):
            s = 1 + 4 * C_PISTA ** 2 * x * x
            xdd = -(4 * C_PISTA ** 2 * x * xd * xd + 2 * C_PISTA * G * x) / s
            xd += xdd * hs
            x += xd * hs
            if x > X_MAX:
                x, xd = X_MAX, -abs(xd)
            elif x < -X_MAX:
                x, xd = -X_MAX, abs(xd)
            # Corrección de energía: evita la deriva numérica
            y = C_PISTA * x * x
            s = 1 + 4 * C_PISTA ** 2 * x * x
            ec_obj = max(e0 - G * y, 0.0)
            signo = 1 if xd >= 0 else -1
            xd = signo * math.sqrt(2 * ec_obj / s)
        mec["x"], mec["xd"] = x, xd

    x, xd, e0 = mec["x"], mec["xd"], mec["e0"]
    y = C_PISTA * x * x
    s = 1 + 4 * C_PISTA ** 2 * x * x
    rapidez = abs(xd) * math.sqrt(s)

    # --- Dibujo ---
    puntos = [_pista_px(-X_MAX + 0.5 * i) for i in range(41)]
    formas = [
        dib.poligono(puntos + [(CX_PISTA + X_MAX * SX, H_ESC),
                               (CX_PISTA - X_MAX * SX, H_ESC)], "#CBD5E1"),
        dib.polilinea(puntos, "#64748B", 5),
    ]

    # Nivel de energía mecánica
    y_em = Y_BASE - (e0 / G) * SY
    if y_em > 14:
        formas.append(dib.linea(10, y_em, W_ESC - 10, y_em,
                                paleta.COLOR_MECANICA, 1, True))
        formas.append(dib.texto(W_ESC - 175, y_em - 16,
                                "nivel de energía mecánica", 11,
                                paleta.COLOR_MECANICA, True))

    # Pelota sobre la pista
    px, py = _pista_px(x)
    g = -2 * C_PISTA * x * SY / SX
    norma = math.sqrt(1 + g * g)
    r = 10 + m * 0.5
    bx, by = px + (g / norma) * r, py - (1 / norma) * r

    formas.append(dib.circulo(bx, by, r, paleta.COLOR_MECANICA))
    formas.append(dib.circulo(bx - r * 0.3, by - r * 0.3, r * 0.25,
                              "#66FFFFFF"))

    # Altura y vector velocidad
    formas.append(dib.linea(bx, by + r, bx, Y_BASE, "#94A3B8", 1, True))
    formas.append(dib.texto(bx + 6, Y_BASE - 18, f"y = {y:.1f} m", 11,
                            paleta.TEXTO_SECUNDARIO))
    sentido = 1 if xd >= 0 else -1
    L = min(rapidez * 2.5, 90)
    formas += dib.flecha(bx, by, bx + sentido * L / norma,
                         by + sentido * L * g / norma,
                         paleta.COLOR_CINETICA, 4)

    # Energías
    ec = 0.5 * m * rapidez ** 2
    epg = m * G * y
    em = ec + epg
    total = m * e0
    rango = (0, total if total > 1e-9 else 1)

    vivo = {
        "T": 10.0, "unidad": "J",
        "rango": rango, "rango_barras": rango,
        "barras": [
            ("Ec", ec, paleta.COLOR_CINETICA),
            ("Epg", epg, paleta.COLOR_GRAVITACIONAL),
            ("Em", em, paleta.COLOR_MECANICA),
        ],
        "series": [
            ("Ec (cinética)", ec, paleta.COLOR_CINETICA),
            ("Epg (gravitacional)", epg, paleta.COLOR_GRAVITACIONAL),
            ("Em (mecánica)", em, paleta.COLOR_MECANICA),
        ],
        "texto": (
            f"Ec = {ec:.1f} J    Epg = {epg:.1f} J    "
            f"Em = Ec + Epg = {em:.1f} J\n"
            f"Sin fricción, la energía mecánica se conserva: la pelota sube "
            f"hasta la altura de donde partió.\n"
            f"Abajo toda la energía es cinética; arriba es potencial "
            f"(velocidad v = {rapidez:.1f} m/s)."
        )
    }
    return formas, vivo


# ==========================================
# ESCENA 6: POTENCIA MECÁNICA
# ==========================================

def _escena_potencia(t, p, est, dt):
    F, dist = p["fuerza"], p["distancia"]
    ang, Tt = p["angulo"], p["tiempo"]

    Fx = F * math.cos(math.radians(ang))
    W = Fx * dist
    P1 = W / Tt
    T2 = Tt / 2
    P2 = 2 * P1

    espera, cierre = 0.5, 1.5
    T = espera + Tt + cierre
    ts = max(t - espera, 0.0)

    x1 = dist * min(ts / Tt, 1.0)
    x2 = dist * min(ts / T2, 1.0)
    W1, W2 = Fx * x1, Fx * x2

    mover1 = 0 < ts < Tt
    mover2 = 0 < ts < T2
    pa = P1 if mover1 else 0.0
    pb = P2 if mover2 else 0.0

    formas = []
    carriles = [
        (140, x1, W1, "Motor A", Tt, P1, paleta.COLOR_POTENCIA),
        (250, x2, W2, "Motor B", T2, P2, paleta.COLOR_CINETICA),
    ]

    for ys, xr, Wi, nombre, ti, Pi, color in carriles:
        formas.append(dib.rect(0, ys, W_ESC, 6, "#94A3B8"))
        car, (cx, cy), w, h = dib.carrito(30 + xr * ESC_M, ys, 5, color,
                                          etiqueta=False)
        # Meta
        formas.append(dib.linea(30 + dist * ESC_M + w / 2, ys - 70,
                                30 + dist * ESC_M + w / 2, ys + 6,
                                "#94A3B8", 1, True))
        # Cuerda y motor
        formas.append(dib.linea(30 + xr * ESC_M + w, cy, 545, cy,
                                "#475569", 2))
        formas.append(dib.rect(545, cy - 16, 30, 32, "#475569", 6))
        formas.append(dib.texto(554, cy - 7, "M", 14, "#FFFFFF", True))
        formas += car
        formas.append(dib.texto(10, ys - 96,
                                f"{nombre}: t = {ti:.1f} s   →   "
                                f"P = W/t = {Pi:.1f} W",
                                12, color, True))
        formas.append(dib.texto(30 + xr * ESC_M, ys - 72,
                                f"W = {Wi:.0f} J", 12, color, True))

    lo, hi = min(0, W), max(0, W)
    if hi - lo < 1e-9:
        hi = lo + 1
    blo, bhi = min(0, P2), max(0, P2)
    if bhi - blo < 1e-9:
        bhi = blo + 1

    vivo = {
        "T": T, "unidad": "W",
        "rango": (lo, hi), "rango_barras": (blo, bhi),
        "barras": [("P A", pa, paleta.COLOR_POTENCIA),
                   ("P B", pb, paleta.COLOR_CINETICA)],
        "series": [("W motor A", W1, paleta.COLOR_POTENCIA),
                   ("W motor B", W2, paleta.COLOR_CINETICA)],
        "texto": (
            f"Ambos motores realizan el mismo trabajo: "
            f"W = F·d·cos(θ) = {W:.1f} J.\n"
            f"Motor A: P = {W:.1f} / {Tt:.1f} = {P1:.1f} W     "
            f"Motor B (la mitad del tiempo): P = {W:.1f} / {T2:.1f} "
            f"= {P2:.1f} W\n"
            f"Más potencia = el mismo trabajo en menos tiempo. "
            f"En la gráfica, la pendiente de W(t) es la potencia."
        )
    }
    return formas, vivo


FUNCIONES = {
    "trabajo": _escena_trabajo,
    "cinetica": _escena_cinetica,
    "gravitacional": _escena_gravitacional,
    "elastica": _escena_elastica,
    "mecanica": _escena_mecanica,
    "potencia": _escena_potencia,
}


# ==========================================
# AVANZAR LA ANIMACIÓN UN PASO
# ==========================================

def avanzar_escena(escena, tema_id, parametros, dt):
    """dt = 0 solo redibuja (útil en pausa o al mover un slider)."""

    est = escena["estado"]
    est["t"] += dt

    formas, vivo = FUNCIONES[tema_id](est["t"], parametros, est, dt)

    if dt > 0:
        if est["t"] > vivo["T"]:
            reiniciar_escena(escena)          # empieza un nuevo ciclo
        else:
            hist = est["hist"]
            hist["t"].append(est["t"])
            for nombre, valor, _ in vivo["series"]:
                hist["vals"].setdefault(nombre, []).append(valor)

    escena["canvas_escena"].shapes = [f for f in formas if f is not None]
    escena["canvas_barras"].shapes = dibujar_barras(vivo)
    escena["canvas_grafica"].shapes = dibujar_grafica(est, vivo)
    escena["informacion"].value = vivo["texto"]