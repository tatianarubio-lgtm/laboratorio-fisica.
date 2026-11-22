import math

# Constante gravitacional
G = 9.81


def calcular(masa, velocidad, altura, fuerza, distancia,
             angulo, constante, compresion, tiempo):

    theta = math.radians(angulo)

    trabajo = fuerza * distancia * math.cos(theta)
    energia_cinetica = 0.5 * masa * velocidad ** 2
    energia_gravitacional = masa * G * altura
    energia_elastica = 0.5 * constante * compresion ** 2

    energia_mecanica = (
        energia_cinetica + energia_gravitacional + energia_elastica
    )

    potencia = trabajo / tiempo if tiempo > 0 else 0

    return {
        "trabajo": trabajo,
        "cinetica": energia_cinetica,
        "gravitacional": energia_gravitacional,
        "elastica": energia_elastica,
        "mecanica": energia_mecanica,
        "potencia": potencia
    }