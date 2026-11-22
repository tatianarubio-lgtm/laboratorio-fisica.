import paleta


# "controles" indica qué deslizadores se muestran en cada tema.

TEMAS = {

    "trabajo": {
        "nombre": "Trabajo mecánico",
        "formula": "W = F · d · cos(θ)",
        "descripcion": (
            "El trabajo mecánico ocurre cuando una fuerza "
            "produce un desplazamiento."
        ),
        "color": paleta.COLOR_TRABAJO,
        "controles": ["masa", "fuerza", "distancia", "angulo"]
    },

    "cinetica": {
        "nombre": "Energía cinética",
        "formula": "Ec = ½ · m · v²",
        "descripcion": (
            "Es la energía que posee un objeto debido "
            "a su movimiento."
        ),
        "color": paleta.COLOR_CINETICA,
        "controles": ["masa", "velocidad"]
    },

    "gravitacional": {
        "nombre": "Energía potencial gravitacional",
        "formula": "Epg = m · g · h",
        "descripcion": (
            "Es la energía que posee un objeto debido "
            "a su posición o altura."
        ),
        "color": paleta.COLOR_GRAVITACIONAL,
        "controles": ["masa", "altura"]
    },

    "elastica": {
        "nombre": "Energía potencial elástica",
        "formula": "Epe = ½ · k · x²",
        "descripcion": (
            "Es la energía almacenada cuando un resorte "
            "se comprime o se estira."
        ),
        "color": paleta.COLOR_ELASTICA,
        "controles": ["masa", "constante", "compresion"]
    },

    "mecanica": {
        "nombre": "Energía mecánica",
        "formula": "Em = Ec + Epg + Epe",
        "descripcion": (
            "Es la suma de la energía cinética y las "
            "energías potenciales del sistema."
        ),
        "color": paleta.COLOR_MECANICA,
        "controles": ["masa", "altura", "velocidad"]
    },

    "potencia": {
        "nombre": "Potencia mecánica",
        "formula": "P = W / t",
        "descripcion": (
            "Indica qué tan rápido se realiza un trabajo "
            "o se transfiere energía."
        ),
        "color": paleta.COLOR_POTENCIA,
        "controles": ["fuerza", "distancia", "angulo", "tiempo"]
    }

}