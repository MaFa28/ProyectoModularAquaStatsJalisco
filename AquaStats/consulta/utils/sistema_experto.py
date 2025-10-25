from datetime import datetime

def sistema_experto(consumo_promedio, consumo_usuario, categoria_bayes=None, cluster=None):
    """
    Genera recomendaciones automáticas basadas en el comportamiento del usuario.
    """
    recomendaciones = []

    # Comparación con el promedio
    if consumo_usuario > consumo_promedio * 1.3:
        recomendaciones.append("Tu consumo es alto respecto al promedio regional. Revisa fugas o hábitos de uso.")
    elif consumo_usuario < consumo_promedio * 0.7:
        recomendaciones.append("Excelente trabajo, tu consumo está por debajo del promedio. ¡Sigue así!")
    else:
        recomendaciones.append("Tu consumo es adecuado comparado con otros usuarios de tu región.")

    # Clasificación Bayesiana
    if categoria_bayes:
        if categoria_bayes.lower() == "alto":
            recomendaciones.append("Clasificado como usuario de alto consumo. Considera aplicar medidas de ahorro.")
        elif categoria_bayes.lower() == "medio":
            recomendaciones.append("Consumo moderado. Intenta optimizar el uso en horarios de baja demanda.")
        else:
            recomendaciones.append("Tu consumo es bajo, contribuyes positivamente a la sostenibilidad.")

    # Clúster (K-Means)
    if cluster is not None:
        recomendaciones.append(f"Perteneces al grupo de usuarios con patrón de consumo similar (Cluster {cluster}).")

    # Información final
    recomendaciones.append(f"Análisis generado automáticamente el {datetime.now().strftime('%d/%m/%Y %H:%M')}.")

    return recomendaciones
