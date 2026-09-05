from textwrap import wrap


def _texto(valor):
    return str(valor or "Sin registro").encode("latin-1", "replace").decode("latin-1")


def generar_pdf(titulo, secciones):
    lineas = [titulo, ""]
    for etiqueta, valor in secciones:
        lineas.append(etiqueta.upper())
        lineas.extend(wrap(_texto(valor), width=92) or ["Sin registro"])
        lineas.append("")
    paginas = [lineas[i:i + 48] for i in range(0, len(lineas), 48)] or [[]]
    objetos = []

    def agregar(contenido):
        objetos.append(contenido)
        return len(objetos)

    catalogo, arbol, fuente = agregar(b""), agregar(b""), agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    ids_paginas = []
    for pagina in paginas:
        comandos = ["BT", "/F1 11 Tf", "48 790 Td", "14 TL"]
        for numero, linea in enumerate(pagina):
            escapada = _texto(linea).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if numero:
                comandos.append("T*")
            comandos.append(f"({escapada}) Tj")
        comandos.append("ET")
        flujo = "\n".join(comandos).encode("latin-1")
        contenido = agregar(b"<< /Length %d >>\nstream\n" % len(flujo) + flujo + b"\nendstream")
        ids_paginas.append(agregar(
            f"<< /Type /Page /Parent {arbol} 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {fuente} 0 R >> >> /Contents {contenido} 0 R >>".encode()
        ))
    objetos[catalogo - 1] = f"<< /Type /Catalog /Pages {arbol} 0 R >>".encode()
    hijos = " ".join(f"{pagina} 0 R" for pagina in ids_paginas)
    objetos[arbol - 1] = f"<< /Type /Pages /Kids [{hijos}] /Count {len(ids_paginas)} >>".encode()
    salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posiciones = [0]
    for numero, objeto in enumerate(objetos, 1):
        posiciones.append(len(salida))
        salida.extend(f"{numero} 0 obj\n".encode() + objeto + b"\nendobj\n")
    xref = len(salida)
    salida.extend(f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode())
    for posicion in posiciones[1:]:
        salida.extend(f"{posicion:010d} 00000 n \n".encode())
    salida.extend(f"trailer\n<< /Size {len(objetos) + 1} /Root {catalogo} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(salida)


def informe_requerimiento(ticket):
    return generar_pdf("INFORME DE REQUERIMIENTO TECNICO", [
        ("Código", ticket.codigo), ("Asunto", ticket.titulo),
        ("Solicitante", ticket.solicitante.nombre_completo),
        ("Técnico", getattr(ticket.tecnico_asignado, "nombre_completo", "")),
        ("Diagnóstico", ticket.diagnostico), ("Plan de solución", ticket.plan_solucion),
        ("Componente requerido", ticket.componente_requerido), ("Cantidad", ticket.cantidad_componente),
        ("Especificaciones técnicas", ticket.especificaciones_tecnicas),
        ("Justificación", ticket.justificacion_compra),
        ("Proveedor de referencia", ticket.proveedor_cotizacion), ("Costo estimado", ticket.costo_estimado),
    ])


def informe_final_jefatura(ticket, informe_final):
    return generar_pdf("INFORME FINAL DE JEFATURA UTIC", [
        ("Código", ticket.codigo), ("Asunto", ticket.titulo),
        ("Solicitante", ticket.solicitante.nombre_completo),
        ("Técnico", getattr(ticket.tecnico_asignado, "nombre_completo", "")),
        ("Diagnóstico", ticket.diagnostico), ("Plan de solución", ticket.plan_solucion),
        ("Intervención realizada", ticket.solucion), ("Resultado de pruebas", ticket.resultado_pruebas),
        ("Informe del técnico", ticket.informe_tecnico),
        ("Conformidad del solicitante", "Conforme" if ticket.conformidad_usuario else "No conforme"),
        ("Observaciones del solicitante", ticket.observaciones_usuario),
        ("Informe y validación de Jefatura UTIC", informe_final),
    ])


def informe_tecnico(ticket, texto_informe):
    return generar_pdf("INFORME TECNICO DE ATENCION", [
        ("Código", ticket.codigo), ("Asunto", ticket.titulo),
        ("Solicitante", ticket.solicitante.nombre_completo),
        ("Técnico", getattr(ticket.tecnico_asignado, "nombre_completo", "")),
        ("Descripción del requerimiento", ticket.descripcion),
        ("Ubicación", ticket.ubicacion), ("Equipo afectado", ticket.equipo_afectado),
        ("Diagnóstico", ticket.diagnostico), ("Plan de solución", ticket.plan_solucion),
        ("Intervención realizada", ticket.solucion), ("Resultado de pruebas", ticket.resultado_pruebas),
        ("Informe del técnico", texto_informe),
    ])
