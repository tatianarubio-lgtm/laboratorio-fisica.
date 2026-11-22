import flet as ft
import paleta


# ==========================================
# CREAR UNA TARJETA DE RESULTADO
# ==========================================

def crear_tarjeta(nombre, formula, color):

    valor = ft.Text("0.00", size=26, weight=ft.FontWeight.BOLD, color=color)
    unidad = ft.Text("", size=13, color=paleta.TEXTO_SECUNDARIO)

    tarjeta = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(nombre, size=14, weight=ft.FontWeight.BOLD,
                        color=paleta.TEXTO_OSCURO),
                ft.Row(
                    controls=[valor, unidad],
                    spacing=5,
                    vertical_alignment=ft.CrossAxisAlignment.END
                ),
                ft.Text(formula, size=12, color=paleta.TEXTO_SECUNDARIO)
            ],
            spacing=8
        ),
        padding=16,
        bgcolor=paleta.BLANCO,
        border=ft.Border.all(1, paleta.BORDE),
        border_radius=16,
        expand=True
    )

    return {"tarjeta": tarjeta, "valor": valor, "unidad": unidad}


# ==========================================
# CREAR TODAS LAS TARJETAS
# ==========================================

DEFINICIONES = [
    ("trabajo", "Trabajo mecánico", "W = F · d · cos(θ)",
     paleta.COLOR_TRABAJO, "J"),
    ("cinetica", "Energía cinética", "Ec = ½ · m · v²",
     paleta.COLOR_CINETICA, "J"),
    ("gravitacional", "Energía potencial gravitacional", "Epg = m · g · h",
     paleta.COLOR_GRAVITACIONAL, "J"),
    ("elastica", "Energía potencial elástica", "Epe = ½ · k · x²",
     paleta.COLOR_ELASTICA, "J"),
    ("mecanica", "Energía mecánica", "Em = Ec + Epg + Epe",
     paleta.COLOR_MECANICA, "J"),
    ("potencia", "Potencia mecánica", "P = W / t",
     paleta.COLOR_POTENCIA, "W"),
]

UNIDADES = {clave: unidad for clave, _, _, _, unidad in DEFINICIONES}


def crear_resultados():

    resultados = {}
    for clave, nombre, formula, color, _ in DEFINICIONES:
        resultados[clave] = crear_tarjeta(nombre, formula, color)

    panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "📊 RESULTADOS DEL EXPERIMENTO",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=paleta.AZUL_OSCURO
                ),
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            content=resultados[clave]["tarjeta"],
                            col={"sm": 12, "md": 6, "lg": 4}
                        )
                        for clave, _, _, _, _ in DEFINICIONES
                    ],
                    spacing=10,
                    run_spacing=10
                )
            ],
            spacing=12
        ),
        padding=18,
        bgcolor=paleta.FONDO_PANEL,
        border_radius=18
    )

    return resultados, panel


# ==========================================
# ACTUALIZAR LOS RESULTADOS
# ==========================================

def actualizar_resultados(tarjetas, datos):
    for clave, unidad in UNIDADES.items():
        tarjetas[clave]["valor"].value = f"{datos[clave]:.2f}"
        tarjetas[clave]["unidad"].value = unidad