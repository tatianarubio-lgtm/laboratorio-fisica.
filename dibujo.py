import math
import flet as ft
import flet.canvas as cv
import paleta


# ==========================================
# PINTURAS BÁSICAS
# ==========================================

def relleno(color):
    return ft.Paint(color=color, style=ft.PaintingStyle.FILL)


def trazo(color, ancho=2, punteado=False):
    if punteado:
        return ft.Paint(
            color=color,
            stroke_width=ancho,
            style=ft.PaintingStyle.STROKE,
            stroke_dash_pattern=[6, 5]
        )
    return ft.Paint(
        color=color,
        stroke_width=ancho,
        style=ft.PaintingStyle.STROKE
    )


def transparente(color, alfa="55"):
    """Devuelve el color con transparencia (formato #AARRGGBB)."""
    return "#" + alfa + color.lstrip("#")


# ==========================================
# FORMAS
# ==========================================

def rect(x, y, w, h, color, radio=0):
    return cv.Rect(x, y, w, h, border_radius=radio, paint=relleno(color))


def rect_borde(x, y, w, h, color, ancho=1, radio=0):
    return cv.Rect(x, y, w, h, border_radius=radio, paint=trazo(color, ancho))


def circulo(x, y, r, color):
    return cv.Circle(x, y, r, paint=relleno(color))


def linea(x1, y1, x2, y2, color, ancho=2, punteada=False):
    return cv.Line(x1, y1, x2, y2, paint=trazo(color, ancho, punteada))


def texto(x, y, s, tam=12, color=paleta.TEXTO_OSCURO, negrita=False):
    return cv.Text(
        x, y, s,
        style=ft.TextStyle(
            size=tam,
            color=color,
            weight=ft.FontWeight.BOLD if negrita else ft.FontWeight.NORMAL
        )
    )


def polilinea(puntos, color, ancho=2):
    if len(puntos) < 2:
        return None
    elementos = [cv.Path.MoveTo(puntos[0][0], puntos[0][1])]
    for x, y in puntos[1:]:
        elementos.append(cv.Path.LineTo(x, y))
    return cv.Path(elements=elementos, paint=trazo(color, ancho))


def poligono(puntos, color):
    elementos = [cv.Path.MoveTo(puntos[0][0], puntos[0][1])]
    for x, y in puntos[1:]:
        elementos.append(cv.Path.LineTo(x, y))
    elementos.append(cv.Path.Close())
    return cv.Path(elements=elementos, paint=relleno(color))


def flecha(x1, y1, x2, y2, color, ancho=3):
    """Flecha (vector) de (x1,y1) a (x2,y2). Devuelve una lista de formas."""
    dx, dy = x2 - x1, y2 - y1
    largo = math.hypot(dx, dy)
    if largo < 3:
        return []
    ux, uy = dx / largo, dy / largo
    punta = min(11, largo * 0.6)
    bx, by = x2 - ux * punta, y2 - uy * punta
    px, py = -uy * punta * 0.5, ux * punta * 0.5
    return [
        linea(x1, y1, bx, by, color, ancho),
        poligono([(x2, y2), (bx + px, by + py), (bx - px, by - py)], color)
    ]


def resorte(x1, x2, y, color, vueltas=12, alto=12, ancho=3):
    """Resorte horizontal en zigzag entre x1 y x2."""
    largo = x2 - x1
    if largo <= 4:
        return [linea(x1, y, x2, y, color, ancho)]
    stub = min(12, largo * 0.15)
    a, b = x1 + stub, x2 - stub
    puntos = [(x1, y), (a, y)]
    n = vueltas * 2
    for i in range(n):
        xi = a + (b - a) * (i + 0.5) / n
        puntos.append((xi, y - alto if i % 2 == 0 else y + alto))
    puntos += [(b, y), (x2, y)]
    return [polilinea(puntos, color, ancho)]


# ==========================================
# OBJETOS
# ==========================================

def carrito(x, y_suelo, masa, color, etiqueta=True):
    """
    Dibuja un carrito. (x, y_suelo) = esquina izquierda sobre el piso.
    Devuelve: formas, (centro_x, centro_y), ancho, alto
    """
    r = 9
    w = 56 + masa * 1.6
    h = 30 + masa * 0.5
    y_top = y_suelo - 2 * r - h + 6

    formas = [
        rect(x, y_top, w, h, color, 8),
        rect(x + 6, y_top + 5, w - 12, 7, "#33FFFFFF", 3),
        circulo(x + 14, y_suelo - r, r, "#1E293B"),
        circulo(x + w - 14, y_suelo - r, r, "#1E293B"),
        circulo(x + 14, y_suelo - r, 3.5, "#CBD5E1"),
        circulo(x + w - 14, y_suelo - r, 3.5, "#CBD5E1"),
    ]

    if etiqueta:
        s = f"{masa:.1f} kg"
        formas.append(
            texto(x + w / 2 - len(s) * 3.3, y_top + h / 2 - 4,
                  s, 12, "#FFFFFF", True)
        )

    return formas, (x + w / 2, y_top + h / 2), w, h