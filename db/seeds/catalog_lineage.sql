-- Seed del linaje del catalogo. Curado a mano: 12 fuentes x 4 pasos = 48 filas.
--
-- Sin emisor en ml/, y es una decision. US-008 necesita generador porque expande
-- 304 campos desde esquemas y contenido curado, con logica que hay que poder
-- reejecutar; aqui son 48 filas y ninguna regla que las expanda, asi que un
-- emisor de Python solo imprimiria una lista literal. Cuando el artefacto y su
-- fuente son la misma cosa, la reproducibilidad no la compra el generador: la
-- compra git.
--
-- Se aplica DESPUES de catalog.sql, y por eso el nombre ordena alfabeticamente
-- despues: "make db-seed" recorre db/seeds/*.sql en orden. El seed del catalogo
-- abre con TRUNCATE ... CASCADE sobre catalog_source, asi que esta tabla se
-- vacia sola antes de volver a llenarse.
--
-- Idempotente por construccion: transaccion, TRUNCATE con RESTART IDENTITY y
-- reinsercion. Sembrar dos veces deja la base identica hasta en las claves.
--
-- Ni un solo id literal: cada fila encuentra su fuente por su code natural. Si
-- un code dejara de existir, el JOIN descartaria la fila EN SILENCIO, y por eso
-- las pruebas de integracion comprueban el conteo exacto de 48 y que ninguna
-- fuente se quede sin sus cuatro pasos.
--
-- El paso terminal -la cifra que se esta mirando- no esta aqui a proposito: se
-- compone en lineage_service desde catalog_field. Persistirlo duplicaria
-- columnas que esa tabla ya tiene y crearia una segunda verdad para el mismo
-- hecho. Contenido sintetico y curado, como el resto del prototipo.

BEGIN;

SET client_encoding = 'UTF8';

TRUNCATE catalog_lineage_step RESTART IDENTITY;

INSERT INTO catalog_lineage_step
    (source_id, step_order, stage, system_code, system_name,
     transformation_code, transformation_detail, owner_area, owner_name,
     effective_from, effective_to)
SELECT s.id, v.step_order, v.stage, v.system_code, v.system_name,
       v.transformation_code, v.transformation_detail, v.owner_area, v.owner_name,
       v.effective_from, v.effective_to
FROM (VALUES
    -- (code de catalog_source, orden, etapa, sistema, nombre legible del sistema,
    --  codigo de transformacion, detalle no traducible, area, persona, desde, hasta)

    -- creditos: SIC-Core exporta cada noche; la regla de saldo insoluto es de Riesgo.
    ('creditos', 1, 'origen', 'SIC-Core', 'Core bancario SIC',
     'origin_capture', 'SIC-Core.CRE_CONTRATO',
     'Tecnologia de Core', 'Alberto Nunez', DATE '2018-01-01', NULL::date),
    ('creditos', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_creditos_nocturno',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2022-03-01', NULL::date),
    ('creditos', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'business_rule', 'regla_saldo_insoluto_v3',
     'Riesgo de Crédito', 'Sofia Aranda', DATE '2023-07-01', NULL::date),
    ('creditos', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_cuadre_saldo_vs_mayor',
     'Calidad de Datos', 'Teresa Villalba', DATE '2024-02-01', NULL::date),

    -- liquidez: posiciones por divisa, convertidas al fix de cierre.
    ('liquidez', 1, 'origen', 'TESO-Pos', 'Posiciones de tesorería TESO',
     'origin_capture', 'TESO-Pos.POSICION_DIA',
     'Tecnologia de Tesorería', 'Bruno Lara', DATE '2019-04-01', NULL::date),
    ('liquidez', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'stream_extract', 'stream_liquidez_tiempo_real',
     'Plataforma de Datos', 'Nadia Robles', DATE '2023-01-15', NULL::date),
    ('liquidez', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'currency_conversion', 'fx_fix_banxico_cierre',
     'Tesorería', 'Adriana Cortes', DATE '2023-09-01', NULL::date),
    ('liquidez', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_cobertura_lcr_minima',
     'Calidad de Datos', 'Teresa Villalba', DATE '2024-05-01', NULL::date),

    -- derivados: el nocional nace en USD y se convierte para el tablero.
    ('derivados', 1, 'origen', 'DRV-Front', 'Front office de derivados DRV',
     'origin_capture', 'DRV-Front.TRADE_BOOK',
     'Tecnologia de Mercados', 'Cecilia Prado', DATE '2018-06-01', NULL::date),
    ('derivados', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'stream_extract', 'stream_derivados_intradia',
     'Plataforma de Datos', 'Nadia Robles', DATE '2022-11-01', NULL::date),
    ('derivados', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'currency_conversion', 'fx_nocional_usd_a_mxn',
     'Mesa de Derivados', 'Hugo Beltran', DATE '2024-01-08', NULL::date),
    ('derivados', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_mtm_contra_curva_oficial',
     'Riesgo de Mercado', 'Daniel Ocampo', DATE '2024-09-01', NULL::date),

    -- clientes: la misma persona llega por tres codificaciones y hay que deduplicar.
    ('clientes', 1, 'origen', 'MDM-Cli', 'Maestro de clientes MDM',
     'origin_capture', 'MDM-Cli.PERSONA',
     'Tecnologia de Datos', 'Ivonne Bravo', DATE '2017-09-01', NULL::date),
    ('clientes', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_clientes_semanal',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2022-02-01', NULL::date),
    ('clientes', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'deduplication', 'dedup_persona_rfc_curp',
     'Datos y Gobierno', 'Paola Iniguez', DATE '2023-04-01', NULL::date),
    ('clientes', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_unicidad_clave_cliente',
     'Calidad de Datos', 'Oscar Medina', DATE '2024-03-01', NULL::date),

    -- garantias: el aforo llega con precisiones distintas y se normaliza.
    ('garantias', 1, 'origen', 'GAR-Col', 'Gestor de colaterales GAR',
     'origin_capture', 'GAR-Col.BIEN_GARANTIA',
     'Tecnologia de Crédito', 'Rosa Elizondo', DATE '2019-02-01', NULL::date),
    ('garantias', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_garantias_semanal',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2022-08-01', NULL::date),
    ('garantias', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'type_normalization', 'norm_aforo_decimal_4',
     'Dirección de Crédito', 'Marcela Rios', DATE '2023-05-01', NULL::date),
    ('garantias', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_avaluo_vigente_12m',
     'Calidad de Datos', 'Oscar Medina', DATE '2024-06-01', NULL::date),

    -- pagos: el mismo folio entra por dos canales y se deduplica antes de aplicarlo.
    ('pagos', 1, 'origen', 'PAG-Cob', 'Pagos y cobranza PAG',
     'origin_capture', 'PAG-Cob.APLICACION_PAGO',
     'Tecnologia de Operaciones', 'Hector Vidal', DATE '2018-03-01', NULL::date),
    ('pagos', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_pagos_horario',
     'Plataforma de Datos', 'Nadia Robles', DATE '2022-05-01', NULL::date),
    ('pagos', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'deduplication', 'dedup_pago_folio_canal',
     'Operaciones', 'Ivan Zepeda', DATE '2023-10-01', NULL::date),
    ('pagos', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_pago_sin_contrato',
     'Calidad de Datos', 'Teresa Villalba', DATE '2024-04-01', NULL::date),

    -- provisiones: la estimacion preventiva sigue la regla B6 de la CNBV.
    ('provisiones', 1, 'origen', 'PRV-Res', 'Motor de reservas PRV',
     'origin_capture', 'PRV-Res.CALIFICACION',
     'Tecnologia de Riesgos', 'Karla Fonseca', DATE '2019-01-01', NULL::date),
    ('provisiones', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_provisiones_mensual',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2022-04-01', NULL::date),
    ('provisiones', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'business_rule', 'regla_epr_cnbv_b6',
     'Riesgo de Crédito', 'Sofia Aranda', DATE '2023-12-01', NULL::date),
    ('provisiones', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_reserva_no_negativa',
     'Calidad de Datos', 'Oscar Medina', DATE '2024-07-01', NULL::date),

    -- contabilidad: el mayor se concilia contra los auxiliares de cada silo.
    ('contabilidad', 1, 'origen', 'CTB-GL', 'Libro mayor CTB',
     'origin_capture', 'CTB-GL.POLIZA',
     'Tecnologia Financiera', 'Gustavo Rendon', DATE '2017-01-01', NULL::date),
    ('contabilidad', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_contabilidad_cierre',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2021-11-01', NULL::date),
    ('contabilidad', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'reconciliation', 'concilia_mayor_vs_auxiliar',
     'Contraloria', 'Jorge Nieto', DATE '2023-02-01', NULL::date),
    ('contabilidad', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_partida_doble_cuadrada',
     'Calidad de Datos', 'Teresa Villalba', DATE '2024-01-15', NULL::date),

    -- tesoreria: la proyeccion es simulada y la regla lo dice en su nombre.
    ('tesorería', 1, 'origen', 'TES-Flu', 'Flujo de efectivo TES',
     'origin_capture', 'TES-Flu.FLUJO_DIA',
     'Tecnologia de Tesorería', 'Bruno Lara', DATE '2019-07-01', NULL::date),
    ('tesorería', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'stream_extract', 'stream_tesoreria_intradia',
     'Plataforma de Datos', 'Nadia Robles', DATE '2023-03-01', NULL::date),
    ('tesorería', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'business_rule', 'regla_flujo_proyectado_simulado',
     'Tesorería', 'Adriana Cortes', DATE '2024-02-15', NULL::date),
    ('tesorería', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_colateral_disponible_no_negativo',
     'Calidad de Datos', 'Oscar Medina', DATE '2024-08-01', NULL::date),

    -- riesgo_mercado: las sensibilidades llegan en unidades distintas y se pasan a bps.
    ('riesgo_mercado', 1, 'origen', 'RSK-Mkt', 'Motor de riesgo de mercado RSK',
     'origin_capture', 'RSK-Mkt.VAR_DIARIO',
     'Tecnologia de Riesgos', 'Karla Fonseca', DATE '2018-10-01', NULL::date),
    ('riesgo_mercado', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'stream_extract', 'stream_riesgo_mercado_cierre',
     'Plataforma de Datos', 'Nadia Robles', DATE '2022-09-01', NULL::date),
    ('riesgo_mercado', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'type_normalization', 'norm_sensibilidad_bps',
     'Riesgo de Mercado', 'Daniel Ocampo', DATE '2023-08-01', NULL::date),
    ('riesgo_mercado', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_var_contra_backtesting',
     'Calidad de Datos', 'Teresa Villalba', DATE '2024-10-01', NULL::date),

    -- canales: el tiempo de respuesta llega en tres unidades y se normaliza a segundos.
    ('canales', 1, 'origen', 'CAN-Ori', 'Originación multicanal CAN',
     'origin_capture', 'CAN-Ori.SOLICITUD',
     'Tecnologia de Canales', 'Diego Palacios', DATE '2020-01-01', NULL::date),
    ('canales', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'stream_extract', 'stream_canales_solicitudes',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2023-02-01', NULL::date),
    ('canales', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'type_normalization', 'norm_tiempo_respuesta_segundos',
     'Banca Digital', 'Renata Fuentes', DATE '2023-11-01', NULL::date),
    ('canales', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_solicitud_sin_resolucion',
     'Calidad de Datos', 'Oscar Medina', DATE '2025-01-15', NULL::date),

    -- regulatorio: lo enviado se concilia contra el acuse del regulador.
    ('regulatorio', 1, 'origen', 'REG-Rep', 'Reportes regulatorios REG',
     'origin_capture', 'REG-Rep.ACUSE_ENVIO',
     'Tecnologia Financiera', 'Gustavo Rendon', DATE '2018-02-01', NULL::date),
    ('regulatorio', 2, 'extraccion', 'KRS-Ingesta', 'Ingesta Karisma',
     'batch_extract', 'job_regulatorio_mensual',
     'Plataforma de Datos', 'Emilio Cazares', DATE '2022-01-10', NULL::date),
    ('regulatorio', 3, 'transformacion', 'KRS-Semantica', 'Capa semantica Karisma',
     'reconciliation', 'concilia_acuse_vs_envio',
     'Contraloria', 'Jorge Nieto', DATE '2023-06-01', NULL::date),
    ('regulatorio', 4, 'calidad', 'KRS-Calidad', 'Control de calidad Karisma',
     'quality_rule', 'ctrl_serie_completa_por_periodo',
     'Calidad de Datos', 'Teresa Villalba', DATE '2024-11-01', NULL::date)
) AS v(source_code, step_order, stage, system_code, system_name,
       transformation_code, transformation_detail, owner_area, owner_name,
       effective_from, effective_to)
JOIN catalog_source s ON s.code = v.source_code;

COMMIT;
