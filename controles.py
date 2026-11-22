import flet as ft
import paleta


# ==========================================
# CREAR UN CONTROL DESLIZANTE
# ==========================================

def crear_control(nombre, minimo, maximo, inicial, unidad, callback):

    # Texto que muestra el valor actual
    etiqueta = ft.Text(
        f"{inicial:.2f} {unidad}",
        size=12,
        color=paleta.TEXTO_SECUNDARIO
    )

    # Slider (la unidad se guarda en .data para usarla en main)
    slider = ft.Slider(
        min=minimo,
        max=maximo,
        value=inicial,
        divisions=50,
        active_color=paleta.AZUL,
        on_change=callback,
        data=unidad
    )

    # Nombre y valor
    encabezado = ft.Row(
        controls=[
            ft.Text(
                nombre,
                size=13,
                weight=ft.FontWeight.BOLD,
                color=paleta.TEXTO_OSCURO
            ),
            etiqueta
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    # Organización del control
    contenido = ft.Column(
        controls=[encabezado, slider],
        spacing=2
    )

    return {
        "slider": slider,
        "etiqueta": etiqueta,
        "contenido": contenido
    }


# ==========================================
# CREAR TODOS LOS CONTROLES
# ==========================================

def crear_controles(callback):

    controles = {}

    controles["masa"] = crear_control(
        "Masa", 0.5, 20, 5, "kg", callback)

    controles["velocidad"] = crear_control(
        "Velocidad", 0, 30, 8, "m/s", callback)

    controles["altura"] = crear_control(
        "Altura", 0, 20, 4, "m", callback)

    controles["fuerza"] = crear_control(
        "Fuerza aplicada", 0, 200, 50, "N", callback)

    controles["distancia"] = crear_control(
        "Distancia recorrida", 0, 30, 10, "m", callback)

    controles["angulo"] = crear_control(
        "Ángulo de la fuerza", 0, 180, 0, "°", callback)

    controles["constante"] = crear_control(
        "Constante del resorte", 10, 500, 150, "N/m", callback)

    controles["compresion"] = crear_control(
        "Compresión del resorte", 0, 1, 0.3, "m", callback)

    controles["tiempo"] = crear_control(
        "Tiempo empleado", 0.1, 30, 5, "s", callback)

    # ======================================
    # PANEL DE CONTROLES
    # ======================================

    panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "🎛️ CONTROLES DEL EXPERIMENTO",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=paleta.AZUL_OSCURO
                ),
                controles["masa"]["contenido"],
                controles["velocidad"]["contenido"],
                controles["altura"]["contenido"],
                controles["fuerza"]["contenido"],
                controles["distancia"]["contenido"],
                controles["angulo"]["contenido"],
                controles["constante"]["contenido"],
                controles["compresion"]["contenido"],
                controles["tiempo"]["contenido"]
            ],
            spacing=10
        ),
        padding=18,
        bgcolor=paleta.BLANCO,
        border=ft.Border.all(1, paleta.BORDE),
        border_radius=18
    )

    return controles, panel
