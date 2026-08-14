# 07 — La lámina de campos de la guía sigue escribiendo `administrador`

**Origen**: US-017, 12-ago-2026. El literal lo escribió US-UX-09.
**Estado**: abierto, acotado a una línea y sin consecuencia hoy.

## Qué pasa

US-016 detectó que el frontend tenía dos grafías para el cuarto rol: `admin`, que es el valor real
del *claim* `scope` del JWT y de la restricción `CHECK` de `app_user`, y `administrador`, que vivía
en el contrato de navegación. US-017 erradicó la segunda del vocabulario de la aplicación:
`RolSugerido` pasó a ser alias de `RolUsuario`, el dato del índice de prototipos dice `admin` y la
clave del `Record` de `BotonPrototipo.vue` también.

Queda una aparición, y no es del vocabulario de la aplicación:

```
frontend/app/components/guia/LaminaCampos.vue:148   rol: 'administrador',
```

Es la clave interna de un arreglo de demostración de la lámina de insignias de la guía de estilos.
No está tipada contra `RolSugerido`, así que el cambio de tipo no la rompe, y no llega a ningún
`if` contra un token.

## Por qué no se resolvió sobre la marcha

`frontend/app/components/guia/**` es de US-UX-09, que estaba en vuelo la misma semana. La frontera
de US-017 se declaró por nombre de archivo antes de programar y esa carpeta quedó fuera: cambiar un
literal ajeno para dejar un `grep` en cero es cosmética que se paga con un conflicto de fusión.

Consecuencia medible y aceptada: el comando de CA-10 excluye `components/guia/` por nombre.

```bash
grep -rn 'administrador' frontend/app --include=*.ts --include=*.vue | grep -v 'components/guia/'
```

## Qué lo absorbe

**US-UX-09**, en su propio commit, cuando toque esa lámina por cualquier otro motivo. El cambio es
una línea y su prueba ya existe: `frontend/test/laminas.spec.ts` monta la lámina.

## Dos apariciones más, y estas no se tocan nunca

`frontend/app/types/sesion.ts` y `frontend/app/utils/sesion.ts` nombran `administrador` **dentro de
sus docstrings**, para explicar por qué la grafía se rechaza. Son de US-015 y decir el nombre del
error es parte de explicarlo: `esRolUsuario('administrador')` devuelve `false` y
`frontend/test/sesion.spec.ts` lo fija. Borrarlas dejaría el `grep` en cero y la explicación sin
sujeto.
