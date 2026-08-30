# Medios de verificación — Postulación a Profesor Titular

Repositorio de respaldo del expediente. **Fuente única de verdad: `manifest.csv`.**
Todo lo demás (el índice, el sitio, las estadísticas de avance) se genera desde ahí.

---

## ⚠️ Antes de publicar: advertencia de privacidad

Este expediente contiene resoluciones internas, nombres de estudiantes, actas de
examen y puntajes de encuesta docente. **No debe quedar público.**

Ten presente que en GitHub un sitio de **Pages es público aunque el repositorio sea
privado**, salvo en planes Enterprise Cloud con control de acceso. Verifica el plan
antes de publicar. Tres opciones seguras, en orden de preferencia:

1. **Repositorio privado, sin Pages.** Se navega el `index.qmd` renderizado en local
   o el HTML en `docs/`. Es lo que recomiendo: la Comisión no necesita una URL.
2. **Renderizar a un PDF único con marcadores** y entregar ese archivo. Es lo que
   efectivamente leerá la Comisión.
3. **Pages privado**, solo si dispones de Enterprise Cloud.

Si finalmente publicas algo abierto, publica el *índice* sin los PDFs: la tabla
demuestra que el expediente existe y está ordenado, sin exponer los documentos.

---

## Convención de identificadores

```
MV-<sección Plantilla>.<correlativo>_<slug>.pdf
   │                    │             └── descripción corta, minúsculas, con guiones
   │                    └── correlativo dentro de la sección
   └── numeración oficial de la Plantilla Única (02, 06.1.2, 07.4.3, 10.1 …)
```

Ejemplo: `MV-07.3.1_fondecyt-1211490.pdf`

**Por qué anclar a la numeración de la Plantilla y no a un correlativo global:** el
número de sección es fijo, lo define la Universidad y es la coordenada que la Comisión
está mirando cuando busca tu respaldo. Un correlativo global se desordena en cuanto
insertas un documento, y cualquier referencia ya escrita en la carta queda mal.

En la carta de presentación se cita así:

> …proyecto FONDECYT Regular 1211490, cuyo certificado de término se acompaña
> como **MV-07.3.1**.

---

## Estructura

```
.
├── manifest.csv          ← se edita esto y solo esto
├── build_index.py        ← genera index.qmd + valida
├── _quarto.yml
├── index.qmd             ← GENERADO, no editar a mano
├── docs/                 ← GENERADO por quarto render
└── mv/
    ├── 02-titulos-grados/
    ├── 05-acreditaciones/
    ├── 06-docencia/
    ├── 07-investigacion/
    ├── 09-vinculacion/
    ├── 10-gestion/
    ├── 13-reconocimientos/
    ├── 14-idiomas/
    └── 15-profesional/
```

## Columnas del manifiesto

| Columna | Contenido |
|---|---|
| `id` | Identificador `MV-…`, único |
| `seccion` | Número de sección de la Plantilla (agrupa el índice) |
| `seccion_titulo` | Título de la sección |
| `titulo` | Nombre del documento tal como lo verá la Comisión |
| `tipo` | Certificado, Resolución, Constancia, Carta, Acta, Informe, Artículo… |
| `fecha` | Año o rango |
| `emisor` | Quién emite el documento — **es tu lista de a-quién-pedirle-qué** |
| `archivo` | Ruta relativa al PDF |
| `estado` | `ok` · `solicitado` · `pendiente` · `no-aplica` |
| `notas` | Discrepancias, recordatorios, a quién escribir |

## Flujo de trabajo

```bash
python3 build_index.py --check   # valida sin escribir
python3 build_index.py           # valida y regenera index.qmd
quarto render                    # construye el sitio en docs/
quarto render index.qmd --to pdf # índice imprimible para adjuntar
```

El validador detecta: IDs duplicados, filas marcadas `ok` cuyo PDF no está en disco,
archivos sueltos en `mv/` que nadie declaró, y estados mal escritos.

## Sugerencia de flujo

1. Llena el manifiesto **antes** de tener los documentos, marcando todo `pendiente`.
   El manifiesto se convierte así en tu lista de solicitudes, ordenada por emisor.
2. Ordena por la columna `emisor` y manda **una sola solicitud por institución** en
   vez de una por documento. Secretaría de Estudios, Decanato y ANID concentran la
   mayor parte del expediente.
3. Cambia a `solicitado` con la fecha de envío en `notas`, para saber a quién insistir.
4. Cuando llegue el PDF, guárdalo con su nombre `MV-…` y cambia el estado a `ok`.
   Si el nombre no calza, el validador te avisa.