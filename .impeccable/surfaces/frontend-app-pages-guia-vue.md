---
version: 1
slug: "frontend-app-pages-guia-vue"
primary_target: "frontend/app/pages/guia.vue"
related_targets: ["frontend/app/layouts/portal.vue"]
---

# Superficie: /guia y el chasis del portal

**Alcance**: el sistema de diseño vivo (`/guia`) y el chasis que enmarca las nueve pantallas.
**Modo de visitante**: Operate. El éxito es que la persona complete su tarea.

## Audiencia y trabajo

El equipo que construye, decidido el 11-ago-2026 sobre el evaluador del curso. Vienen a copiar un
token, comparar un estado o verificar un contraste. **El espécimen va primero; la justificación se
pliega.** Hoy el primer color aparece a 718 px del inicio y eso se invierte.

## Dirección elegida

**Diagrama hombre-máquina**, elegida por el usuario sobre la dirección asignada por el tiro (la
ficha de catálogo). Un mundo de diagrama de líneas sobre retícula visible: conectores ortogonales,
nodos, y corriente que se enciende al recorrer el linaje de una cifra.

**La paleta de semáforo del mundo original queda derogada por medición.** Rojo contra verde bajo
protanopia da dE=20.0, exactamente en el umbral. Sustituida por una escala donde **el estado se
lee por luminancia**, canal que ninguna dicromacia pierde:

| Estado | Luminancia | Peor separación tras simular las tres dicromacias |
|---|---|---|
| inactivo · error · aviso · activo | 0.13 · 0.29 · 0.60 · 0.89 | **dE=21.8**, salto mínimo de luminancia 0.163 |

El verde se elimina. El rojo queda solo para error, siempre acompañado de forma e icono.

## Momento memorable

Seguir una cifra hasta su origen y ver la corriente encenderse por la cadena de conectores. Es el
mecanismo del producto hecho visible: ninguna cifra sin procedencia.

## Restricciones

- **Dos modos, claro y oscuro**, con `prefers-color-scheme` por defecto y control manual. Decisión
  del usuario del 11-ago-2026. La matriz de contraste se calcula **dos veces**.
- Todo entra por `docs/entregables/generar_tokens_a4.py`. Ningún token se escribe a mano.
- Los once colores ancla de `uxdoc.sty` conservan su valor byte a byte: A1, A2 y A3 están
  calificadas y compilan contra ellos.
- La barra lateral **debe colapsar de verdad** por debajo de 768 px. Hoy no lo hace y deja el
  contenido en 135 px.
- El peso tipográfico entra como segundo canal de jerarquía. Nueve roles con un solo peso no son
  nueve roles.
- Sin scroll-hijack ni animación decorativa. La corriente que recorre un conector se justifica
  porque comunica la cadena de procedencia; nada más se mueve.

## Decisiones sin resolver

- Si la escala tipográfica se queda en nueve roles o se reduce a los cuatro que la interfaz usa de
  verdad (el 91.9 % de los nodos cae en 14, 12 u 11 px).
- Cómo se documentan los dos modos en el PDF, que es de un solo color de papel.
