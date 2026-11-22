import asyncio
import time
import traceback

import flet as ft

import paleta
from temas import TEMAS
from controles import crear_controles
from calculos import calcular
from resultados import crear_resultados, actualizar_resultados
from escenas import (
    crear_escena,
    cambiar_escena,
    avanzar_escena,
    reiniciar_escena
)

# ESCRIBE AQUÍ TU NOMBRE (y el de tu grupo, si quieres)
AUTOR = "Sofia Tatiana Rubio Cuellar y Mabel Yuliza Bolanos Castillo# Laboratorio de Física
Simulación interactiva de trabajo, energía y potencia hecha con Python y Flet.

## Cómo ejecutarlo
1. pip install -r requirements.txt
2. python main.py"


def main(page: ft.Page):
    # CONFIGURACIÓN
    page.title = "Laboratorio de Física"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = paleta.FONDO
    page.padding = 20
    page.window.width = 1250
    page.window.height = 900

    # CREAR COMPONENTES
    escena = crear_escena()
    tarjetas, panel_resultados = crear_resultados()
    animacion = {"pausa": False, "rapidez": 1.0}

    # OBTENER VALORES DE LOS SLIDERS
    def obtener_parametros():
        return {
            nombre: control["slider"].value
            for nombre, control in controles.items()
        }

    # ACTUALIZAR TODO (al mover un slider o cambiar de tema)
    def actualizar_laboratorio(e=None):

        parametros = obtener_parametros()
        tema_id = selector_tema.value
        tema = TEMAS[tema_id]

        datos = calcular(
            parametros["masa"],
            parametros["velocidad"],
            parametros["altura"],
            parametros["fuerza"],
            parametros["distancia"],
            parametros["angulo"],
            parametros["constante"],
            parametros["compresion"],
            parametros["tiempo"]
        )

        # Mostrar solo los controles que usa el tema
        for nombre, control in controles.items():
            control["contenido"].visible = nombre in tema["controles"]
            unidad = control["slider"].data or ""
            control["etiqueta"].value = (
                f"{parametros[nombre]:.2f} {unidad}".strip()
            )

        actualizar_resultados(tarjetas, datos)

        cambiar_escena(escena, tema_id)
        avanzar_escena(escena, tema_id, parametros, 0)

        page.update()

    # BOTONES
    def alternar_pausa(e):
        animacion["pausa"] = not animacion["pausa"]

    def reiniciar(e):
        reiniciar_escena(escena)
        escena["estado"]["mec"] = None
        avanzar_escena(escena, selector_tema.value,
                       obtener_parametros(), 0)
        page.update()

    def cambiar_rapidez(e):
        animacion["rapidez"] = slider_rapidez.value

    boton_pausa = ft.Button("⏯ Pausar / seguir", on_click=alternar_pausa)
    boton_reiniciar = ft.Button("🔄 Reiniciar", on_click=reiniciar)

    slider_rapidez = ft.Slider(
        min=0.25, max=2, value=1, divisions=7, width=170,
        active_color=paleta.AZUL,
        on_change=cambiar_rapidez
    )

    # SELECTOR DE TEMAS
    selector_tema = ft.Dropdown(
        label="Seleccionar tema de Física",
        value="trabajo",
        options=[
            ft.dropdown.Option(key=clave, text=tema["nombre"])
            for clave, tema in TEMAS.items()
        ],
        on_select=actualizar_laboratorio,
        width=350
    )

    # CREAR CONTROLES
    controles, panel_controles = crear_controles(actualizar_laboratorio)

    # ENCABEZADO
    encabezado = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "🔬 LABORATORIO DE FÍSICA",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=paleta.AZUL_OSCURO
                ),
                ft.Text(
                    "Simulación interactiva de trabajo, energía y potencia",
                    size=15,
                    color=paleta.TEXTO_SECUNDARIO
                ),
                ft.Text(
                    f"👩‍🔬 Presentado por: {AUTOR}",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=paleta.AZUL
                ),
                ft.Row(
                    controls=[
                        selector_tema,
                        boton_pausa,
                        boton_reiniciar,
                        ft.Text("Velocidad de la animación:", size=12,
                                color=paleta.TEXTO_SECUNDARIO),
                        slider_rapidez
                    ],
                    wrap=True,
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            spacing=10
        ),
        padding=15
    )

    # DISTRIBUCIÓN
    contenido_principal = ft.Row(
        controls=[
            ft.Container(content=panel_controles, width=350),
            ft.Container(content=escena["panel"], expand=True)
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
        spacing=20
    )

    # MOSTRAR TODO
    page.add(
        ft.Column(
            controls=[
                encabezado,
                contenido_principal,
                panel_resultados
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    )

    # ACTUALIZACIÓN INICIAL
    actualizar_laboratorio()

    # BUCLE DE ANIMACIÓN (~30 cuadros por segundo)
    async def bucle():
        ultimo = time.perf_counter()
        while True:
            await asyncio.sleep(1 / 30)
            ahora = time.perf_counter()
            dt = min(ahora - ultimo, 0.1)
            ultimo = ahora

            if animacion["pausa"]:
                continue

            try:
                avanzar_escena(
                    escena,
                    selector_tema.value,
                    obtener_parametros(),
                    dt * animacion["rapidez"]
                )
                page.update()
            except Exception:
                traceback.print_exc()
                break

    page.run_task(bucle)


ft.run(main)
