-- Generado por ml/data/seed_catalog.py. No editar a mano: la siguiente corrida
-- lo reescribe y "make db-seed" comparara byte a byte.
--
-- Semilla 20260720. 12 fuentes, 304 campos, 30 notas tribales.
--
-- Idempotente por construccion: abre transaccion, vacia las tres tablas
-- reiniciando las secuencias y vuelve a insertar. Sembrar dos veces deja la
-- base identica hasta en las claves primarias, y por eso reseembrar BORRA los
-- embedding que escriba la fase de busqueda hibrida: hay que reejecutar el job
-- de embeddings despues de cada "make db-seed".
--
-- Las columnas search_document y embedding no aparecen en ninguna lista: la
-- primera es GENERATED ALWAYS y PostgreSQL rechaza que se le escriba, la
-- segunda se queda nula hasta S5.

BEGIN;

SET client_encoding = 'UTF8';

TRUNCATE catalog_tribal_note, catalog_field, catalog_source
    RESTART IDENTITY CASCADE;

INSERT INTO catalog_source (code, display_name, description, owner_area,
                            owner_name, system_of_record, has_extract)
VALUES
    ('creditos', 'Cartera de crédito', 'Contratos de crédito vigentes y vencidos con su saldo, su mora y su tasa. Es el silo que SIC-Core exporta cada noche.', 'Dirección de Crédito', 'Ricardo Salas', 'SIC-Core', true),
    ('liquidez', 'Posiciones de liquidez', 'Posiciones diarias por cliente, divisa y bucket de vencimiento tal como las publica la mesa de tesorería.', 'Tesorería', 'Adriana Cortes', 'TESO-Pos', true),
    ('derivados', 'Operaciones de derivados', 'Operaciones vivas de la mesa de derivados con su nocional, su valor a mercado y su contraparte.', 'Mesa de Derivados', 'Hugo Beltrán', 'DRV-Front', true),
    ('clientes', 'Maestro de clientes', 'Ficha única del cliente: identificación, domicilio fiscal, segmento y marcas de cumplimiento. Es el origen de la clave que los tres silos codifican de tres maneras distintas.', 'Datos y Gobierno', 'Paola Íñiguez', 'MDM-Cli', false),
    ('garantias', 'Garantías y colaterales', 'Bienes y colaterales que respaldan los créditos, con su avalúo, su aforo y su elegibilidad regulatoria.', 'Dirección de Crédito', 'Marcela Ríos', 'GAR-Col', false),
    ('pagos', 'Pagos y cobranza', 'Pagos recibidos, su aplicación al contrato y la gestion de cobranza asociada.', 'Operaciones', 'Iván Zepeda', 'PAG-Cob', false),
    ('provisiones', 'Provisiones y reservas', 'Calificación de cartera y estimación preventiva para riesgos crediticios por contrato y periodo.', 'Riesgo de Crédito', 'Sofía Aranda', 'PRV-Res', false),
    ('contabilidad', 'Contabilidad general', 'Catalogo de cuentas y movimientos del libro mayor, con su centro de costo y su póliza.', 'Contraloría', 'Jorge Nieto', 'CTB-GL', false),
    ('tesoreria', 'Tesorería y flujo de efectivo', 'Posición consolidada de tesorería, colateral disponible y flujo proyectado del día. Las proyecciones son simuladas.', 'Tesorería', 'Adriana Cortes', 'TES-Flu', false),
    ('riesgo_mercado', 'Riesgo de mercado', 'Valor en riesgo, sensibilidades y consumo de límites por mesa y por libro de negociación.', 'Riesgo de Mercado', 'Daniel Ocampo', 'RSK-Mkt', false),
    ('canales', 'Canales y originación', 'Solicitudes originadas por cada canal, digital o presencial, con su resolución y su tiempo de respuesta.', 'Banca Digital', 'Renata Fuentes', 'CAN-Ori', false),
    ('regulatorio', 'Reportes regulatorios', 'Series que la institución envía al regulador: capital, liquidez, morosidad y rentabilidad, con su acuse.', 'Contraloría', 'Jorge Nieto', 'REG-Rep', false);

-- creditos
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_ref',
       'Referencia de cliente',
       'Clave del cliente con el prefijo CLI- que antepone SIC-Core. Es la misma entidad que id_cliente en liquidez y que ctpty_cd en derivados, con otra codificacion.',
       'Client reference',
       'cliente', 'texto',
       'interna', 'mensual',
       'certificado', NULL, 'count',
       'Sofía Aranda', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'nom_cli',
       'Nombre del cliente',
       'Razon social truncada a 30 caracteres por el origen.',
       'Client name',
       'cartera', 'texto',
       'restringida', 'mensual',
       'en_revision', NULL, NULL,
       'Marcela Ríos', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prod_cd',
       'Codigo de producto',
       'Familia de credito a la que pertenece el contrato.',
       'Product code Hipotecario Mortgage Automotriz Auto loan Crédito PyME SME loan Tarjeta de crédito Credit card Crédito personal Personal loan hipoteca crédito hipotecario crédito automotriz linea de crédito',
       'cartera', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'sdo_cap',
       'Saldo de capital',
       'Capital insoluto en pesos, sin intereses.',
       'Outstanding principal saldo insoluto adeudo lo que debe el cliente principal balance',
       'cartera', 'decimal',
       'restringida', 'mensual',
       'obsoleto', 'MXN', 'sum',
       'Renata Fuentes', DATE '2022-04-01', DATE '2025-04-01'
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'sdo_int',
       'Intereses devengados',
       'Intereses devengados no cobrados, en pesos.',
       'Accrued interest intereses por cobrar devengado',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Ricardo Salas', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'dias_mora',
       'Dias de mora',
       'Dias transcurridos desde el primer pago no cubierto.',
       'Days past due atraso días de atraso morosidad cartera vencida',
       'cartera', 'entero',
       'interna', 'diaria',
       'certificado', 'dias', 'mean',
       'Adriana Cortes', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tasa_pct',
       'Tasa anual',
       'Tasa anual fija pactada, en por ciento.',
       'Annual rate interés que paga tasa de interés costo anual',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Adriana Cortes', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'f_apert',
       'Fecha de apertura',
       'Fecha en que se origino el credito.',
       'Origination date',
       'cartera', 'fecha',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'f_venc',
       'Fecha de vencimiento',
       'Fecha de vencimiento contractual.',
       'Maturity date',
       'cartera', 'fecha',
       'interna', 'semanal',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'suc_cd',
       'Sucursal',
       'Sucursal que origino el contrato, de S-001 a S-120.',
       'Branch',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'est_cta',
       'Estatus de la cuenta',
       'Situacion contable del contrato.',
       'Account status Vigente Current Vencido Past due Castigado Charged off Liquidado Settled cartera vencida saldo vencido castigo',
       'cartera', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Renata Fuentes', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mon_cd',
       'Codigo de moneda',
       'Codigo interno de SIC-Core, no ISO-4217: 01 son pesos. Los importes de este silo estan en pesos, no en miles.',
       'Currency code Pesos mexicanos Mexican pesos',
       'cartera', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';

-- liquidez
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'fec_pos',
       'Fecha de posicion',
       'Dia habil al que corresponde la posicion.',
       'Position date',
       'liquidez', 'fecha',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'fec_val',
       'Fecha valor',
       'Fecha de liquidacion, T+1 habil sobre fec_pos. No es la fecha de la posicion y agrupar por ella corre la serie un dia.',
       'Value date liquidación',
       'liquidez', 'fecha',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Paola Íñiguez', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'id_cliente',
       'Identificador de cliente',
       'Clave del cliente sin prefijo, como entero. Es la misma entidad que cli_ref en creditos.',
       'Client identifier',
       'cliente', 'entero',
       'interna', 'intradia',
       'certificado', NULL, 'count',
       'Ricardo Salas', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cliente_desc',
       'Descripcion del cliente',
       'Razon social completa, sin truncar.',
       'Client description',
       'liquidez', 'texto',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'bucket_venc',
       'Bucket de vencimiento',
       'Banda de vencimiento de la posicion.',
       'Maturity bucket A la vista Overnight Un dia One day Una semana One week Dos semanas Two weeks Un mes One month Dos meses Two months Tres meses Three months Seis meses Six months Un anio One year Mas de un anio Over one year plazo banda de plazo por bucket',
       'liquidez', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'divisa',
       'Divisa',
       'Divisa de la posicion, en ISO-4217.',
       'Currency Peso mexicano Mexican peso Dólar estadounidense US dollar Euro Libra esterlina Pound sterling Yen japones Japanese yen',
       'liquidez', 'categoria',
       'interna', 'semanal',
       'obsoleto', NULL, NULL,
       'Renata Fuentes', DATE '2025-01-01', DATE '2026-01-01'
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'unidad_negocio',
       'Unidad de negocio',
       'Unidad que reporta la posicion.',
       'Business unit Tesorería Treasury Banca de empresas Business banking Banca de personas Retail banking Mercados Markets Corporativo Corporate',
       'liquidez', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mto_disp',
       'Monto disponible',
       'Monto disponible en MILES de la divisa de la fila. Sumarlo sin multiplicar por mil y sin convertir la divisa es el error que este conjunto de datos existe para dramatizar.',
       'Available amount dinero disponible efectivo disponible disponibilidad',
       'liquidez', 'entero',
       'restringida', 'diaria',
       'certificado', NULL, 'sum',
       'Paola Íñiguez', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mto_comp',
       'Monto comprometido',
       'Monto ya comprometido, en miles de la divisa.',
       'Committed amount',
       'liquidez', 'entero',
       'interna', 'diaria',
       'en_revision', NULL, 'sum',
       'Renata Fuentes', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'ratio_lcr',
       'Razon de cobertura',
       'Razon de cobertura de liquidez de la posicion.',
       'Coverage ratio lcr cobertura de liquidez coeficiente de cobertura de liquidez liquidity coverage ratio',
       'liquidez', 'decimal',
       'restringida', 'mensual',
       'certificado', NULL, 'mean',
       'Ricardo Salas', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tipo_pos',
       'Tipo de posicion',
       'Activo o pasivo.',
       'Position type Activo Asset Pasivo Liability',
       'liquidez', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';

-- derivados
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'op_id',
       'Folio de operacion',
       'Folio consecutivo de la operacion.',
       'Trade identifier operación',
       'mercado', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, 'count',
       'Marcela Ríos', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'ctpty_cd',
       'Codigo de contraparte',
       'Clave de contraparte con prefijo C, seis digitos y letra verificadora. Es la misma entidad que cli_ref en creditos.',
       'Counterparty code exposición con contrapartes riesgo de contraparte',
       'cliente', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'ctpty_name',
       'Contraparte',
       'Razon social en mayusculas y sin acentos.',
       'Counterparty',
       'mercado', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'subyacente',
       'Subyacente',
       'Activo subyacente del contrato.',
       'Underlying TIIE 28 dias TIIE 28 days Cetes 91 dias Cetes 91 days Dólar contra peso US dollar against peso Euro contra peso Euro against peso Indice de precios y cotizaciones Mexican stock index Unidad de inversion Investment unit',
       'mercado', 'categoria',
       'interna', 'intradia',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tipo_instr',
       'Instrumento',
       'Familia del instrumento derivado.',
       'Instrument Swap Forward Opcion Option Futuro Future swaps derivados productos derivados',
       'mercado', 'categoria',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Jorge Nieto', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'nocional_usd',
       'Nocional',
       'Nocional en dolares. Este silo no lleva columna de divisa: todo esta en USD de forma implicita.',
       'Notional nocional en dólares notional amount',
       'mercado', 'decimal',
       'interna', 'mensual',
       'certificado', 'USD', 'sum',
       'Jorge Nieto', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mtm_val',
       'Valor a mercado',
       'Valuacion a mercado en dolares, positiva o negativa.',
       'Mark to market valor de mercado marca a mercado valuación a mercado',
       'mercado', 'decimal',
       'restringida', 'mensual',
       'certificado', 'USD', 'sum',
       'Renata Fuentes', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'f_trade',
       'Fecha de concertacion',
       'Fecha en TEXTO con formato AAAAMMDD, tal como la exporta el sistema legado de ancho fijo. No es un tipo fecha.',
       'Trade date',
       'mercado', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'f_settle',
       'Fecha de liquidacion',
       'Fecha de liquidacion en texto AAAAMMDD.',
       'Settlement date liquidación',
       'mercado', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Renata Fuentes', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'book_cd',
       'Libro',
       'Libro de la mesa, de BK-01 a BK-12.',
       'Book',
       'mercado', 'texto',
       'interna', 'mensual',
       'obsoleto', NULL, NULL,
       'Hugo Beltrán', DATE '2023-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cpty_rtg',
       'Calificacion',
       'Calificacion crediticia de la contraparte.',
       'Rating Calificacion AAA AAA rating Calificacion AA AA rating Calificacion A A rating Calificacion BBB BBB rating Calificacion BB BB rating Calificacion B B rating calificación',
       'mercado', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';

-- clientes
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_id',
       'Identificador de cliente',
       'Clave entera del cliente en el maestro, sin prefijo ni letra verificadora.',
       'clave de cliente id del cliente client identifier',
       'cliente', 'entero',
       'interna', 'diaria',
       'certificado', NULL, 'count',
       'Iván Zepeda', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_rfc',
       'RFC del cliente',
       'Registro Federal de Contribuyentes con homoclave: trece posiciones en persona fisica y doce en moral.',
       'rfc registro federal de contribuyentes tax id',
       'cliente', 'texto',
       'restringida', 'mensual',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_curp',
       'CURP del cliente',
       'Clave Única de Registro de Población, solo para persona fisica.',
       'curp clave única de registro de población national id',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_rzn_soc',
       'Razón social del cliente',
       'Nombre legal completo del cliente, sin truncar.',
       'razón social nombre del cliente legal name',
       'cliente', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_nom_com',
       'Nombre comercial',
       'Nombre con el que opera el cliente cuando difiere de la razón social.',
       'nombre comercial marca trade name',
       'cliente', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_tipo_per',
       'Tipo de persona',
       'Persona fisica o persona moral, según el alta fiscal.',
       'persona fisica persona moral entity type',
       'cliente', 'categoria',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_seg',
       'Segmento comercial',
       'Segmento de banca asignado al cliente: empresas, personas o corporativo.',
       'segmento banca customer segment',
       'cliente', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_sub_seg',
       'Subsegmento comercial',
       'Apertura del segmento por nivel de ingresos declarados.',
       'subsegmento sub segmento sub segment',
       'cliente', 'categoria',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_f_alta',
       'Fecha de alta del cliente',
       'Día en que el cliente entró al maestro y quedó disponible para contratar.',
       'alta del cliente fecha de alta onboarding date',
       'cliente', 'fecha',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Jorge Nieto', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_f_baja',
       'Fecha de baja del cliente',
       'Día de la baja. Nula mientras el cliente siga activo.',
       'baja del cliente fecha de baja offboarding date',
       'cliente', 'fecha',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_est',
       'Estatus del cliente',
       'Activo, inactivo o en depuración por el area de datos.',
       'estatus del cliente situación del cliente customer status',
       'cliente', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_calle',
       'Domicilio fiscal',
       'Calle y número del domicilio fiscal declarado ante el SAT.',
       'domicilio dirección fiscal address',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_cp',
       'Código postal del domicilio',
       'Código postal del domicilio fiscal, cinco dígitos.',
       'código postal cp postal code',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_edo',
       'Entidad federativa',
       'Estado del domicilio fiscal, con la clave del INEGI.',
       'estado entidad federativa state',
       'cliente', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Paola Íñiguez', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_mun',
       'Municipio o alcaldía',
       'Municipio o alcaldía del domicilio fiscal.',
       'municipio alcaldia municipality',
       'cliente', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_tel',
       'Teléfono de contacto',
       'Teléfono principal declarado por el cliente, a diez dígitos.',
       'telefono celular phone',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_mail',
       'Correo electrónico',
       'Correo de contacto usado para avisos y estados de cuenta.',
       'correo email correo electrónico',
       'cliente', 'texto',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_act_econ',
       'Actividad económica',
       'Giro del cliente según el catalogo SCIAN del INEGI.',
       'giro actividad económica industry',
       'cliente', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_ing_anual',
       'Ingreso anual declarado',
       'Ingreso anual que el cliente declaró en su última actualización.',
       'ingresos facturación anual annual income',
       'cliente', 'decimal',
       'restringida', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Ricardo Salas', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_rfc_valid',
       'RFC validado',
       'Indica si el RFC pasó la validación de estructura y homoclave.',
       'rfc válido validación de rfc tax id validated',
       'cliente', 'booleano',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Adriana Cortes', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_ejecutivo',
       'Ejecutivo responsable del cliente',
       'Persona dueña de la relación y responsable del dato del cliente ante el comite de gobierno.',
       'dueño del dato responsable del dato ejecutivo de cuenta steward',
       'cliente', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_suc_orig',
       'Sucursal de origen',
       'Sucursal que dio de alta al cliente en el maestro.',
       'sucursal oficina branch',
       'cliente', 'categoria',
       'publica', 'diaria',
       'en_revision', NULL, NULL,
       'Renata Fuentes', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_score_int',
       'Calificación interna del cliente',
       'Puntaje de comportamiento interno, de 0 a 1000.',
       'score interno calificación del cliente internal score',
       'riesgo', 'entero',
       'interna', 'intradia',
       'en_revision', NULL, 'mean',
       'Renata Fuentes', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_score_bur',
       'Calificación de buró',
       'Puntaje del buró de crédito en la última consulta autorizada.',
       'buró de crédito score de buró credit bureau score',
       'riesgo', 'entero',
       'restringida', 'diaria',
       'en_revision', NULL, 'mean',
       'Ricardo Salas', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_lista_neg',
       'Marca de lista de vigilancia',
       'Indica que el cliente aparece en una lista de vigilancia interna.',
       'lista negra lista de vigilancia watch list',
       'riesgo', 'booleano',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_pep',
       'Persona políticamente expuesta',
       'Marca de persona políticamente expuesta según la política de cumplimiento.',
       'pep políticamente expuesta politically exposed person',
       'regulatorio', 'booleano',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_kyc_f_rev',
       'Fecha de la última revisión KYC',
       'Día de la última revisión del expediente de conocimiento del cliente.',
       'kyc conoce a tu cliente know your customer',
       'regulatorio', 'fecha',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_kyc_est',
       'Estatus del expediente KYC',
       'Completo, incompleto o vencido según la política de cumplimiento.',
       'expediente estatus kyc compliance status',
       'regulatorio', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_n_prod',
       'Productos contratados',
       'Número de productos vivos que el cliente tiene contratados.',
       'productos contratados profundidad de relación product holdings',
       'cliente', 'entero',
       'interna', 'mensual',
       'en_revision', 'conteo', 'sum',
       'Jorge Nieto', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_antig_dias',
       'Antigüedad del cliente',
       'Días transcurridos desde el alta del cliente en el maestro.',
       'antiguedad tiempo como cliente tenure',
       'cliente', 'entero',
       'interna', 'intradia',
       'en_revision', 'dias', 'mean',
       'Daniel Ocampo', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';

-- garantias
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_folio',
       'Folio de la garantía',
       'Folio del expediente de garantía, único por bien registrado.',
       'folio de garantía expediente collateral id',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, 'count',
       'Ricardo Salas', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_contrato',
       'Contrato garantizado',
       'Clave del crédito que la garantía respalda.',
       'contrato crédito garantizado secured loan',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_cli_id',
       'Cliente propietario del bien',
       'Clave del cliente dueña del bien otorgado en garantía.',
       'cliente propietario collateral owner',
       'cliente', 'entero',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Paola Íñiguez', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_tipo',
       'Tipo de garantía',
       'Hipotecaria, prendaria, liquida, fiduciaria o aval personal.',
       'garantía hipotecaria hipoteca prenda collateral type',
       'cartera', 'categoria',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_subtipo',
       'Subtipo de garantía',
       'Apertura del tipo: casa habitación, local, maquinaria o depósito.',
       'subtipo clase de bien collateral subtype',
       'cartera', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Hugo Beltrán', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_desc',
       'Descripción del bien',
       'Descripción del inmueble o del bien mueble que respalda el crédito.',
       'descripción del bien inmueble collateral description',
       'cartera', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_val_com',
       'Valor comercial de la garantía',
       'Valor comercial del bien según el último avalúo practicado.',
       'valor de la garantía avaluo valor comercial appraisal value',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Marcela Ríos', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_val_gar',
       'Valor de garantía reconocido',
       'Porción del valor comercial que se reconoce como cobertura tras el aforo.',
       'valor reconocido cobertura de la garantía recognised value',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Jorge Nieto', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_aforo_pct',
       'Aforo aplicado',
       'Descuento aplicado al valor comercial para reconocer la cobertura.',
       'aforo descuento haircut',
       'riesgo', 'decimal',
       'restringida', 'diaria',
       'en_revision', 'porcentaje', 'mean',
       'Marcela Ríos', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_f_avaluo',
       'Fecha del avalúo',
       'Día en que el perito firmó el avalúo vigente.',
       'fecha de avalúo valuacion appraisal date',
       'cartera', 'fecha',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_perito',
       'Perito valuador',
       'Nombre del perito autorizado que practicó el avalúo.',
       'perito valuador appraiser',
       'cartera', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_f_venc_av',
       'Vigencia del avalúo',
       'Fecha en que el avalúo deja de considerarse vigente.',
       'vigencia del avalúo caducidad appraisal expiry',
       'cartera', 'fecha',
       'interna', 'intradia',
       'en_revision', NULL, NULL,
       'Marcela Ríos', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_inmueble_cp',
       'Código postal del inmueble',
       'Código postal donde se ubica el bien inmueble en garantía.',
       'cp del inmueble ubicacion property postal code',
       'cartera', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Adriana Cortes', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_inmueble_edo',
       'Entidad del inmueble',
       'Estado donde se ubica el bien inmueble en garantía.',
       'estado del inmueble plaza property state',
       'cartera', 'categoria',
       'restringida', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_uso_suelo',
       'Uso de suelo',
       'Uso de suelo autorizado del inmueble: habitacional, comercial o mixto.',
       'uso de suelo destino land use',
       'cartera', 'categoria',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_m2',
       'Superficie del inmueble',
       'Superficie en metros cuadrados registrada en el avalúo.',
       'metros cuadrados superficie surface',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'sum',
       'Marcela Ríos', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_reg_pub',
       'Folio real del registro público',
       'Folio del Registro Público de la Propiedad que ampara el inmueble.',
       'folio real registro público land registry',
       'cartera', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_grav_prev',
       'Gravámenes previos',
       'Indica que el bien tiene gravámenes anteriores a favor de terceros.',
       'gravamen hipoteca previa prior lien',
       'riesgo', 'booleano',
       'interna', 'semanal',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_prelacion',
       'Grado de prelación',
       'Lugar que ocupa la institución en el cobro frente a otros acreedores.',
       'prelacion grado lien position',
       'riesgo', 'entero',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_ltv_pct',
       'Razón crédito valor',
       'Saldo del crédito entre el valor comercial de la garantía.',
       'ltv crédito valor loan to value',
       'riesgo', 'decimal',
       'interna', 'mensual',
       'en_revision', 'porcentaje', 'mean',
       'Sofía Aranda', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_est',
       'Estatus de la garantía',
       'Vigente, liberada, adjudicada o en proceso judicial.',
       'estatus de la garantía situacion collateral status',
       'cartera', 'categoria',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Jorge Nieto', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_f_lib',
       'Fecha de liberación',
       'Día en que la garantía se liberó por pago total del crédito.',
       'liberacion cancelación de hipoteca release date',
       'cartera', 'fecha',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_adjud',
       'Marca de adjudicación',
       'Indica que el bien fue adjudicado a la institución por incumplimiento.',
       'adjudicacion bien adjudicado foreclosed',
       'riesgo', 'booleano',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_seg_pol',
       'Póliza de seguro del bien',
       'Número de póliza que cubre el bien otorgado en garantía.',
       'poliza seguro del inmueble insurance policy',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_seg_vig',
       'Vigencia del seguro',
       'Fecha en que vence la póliza de seguro del bien.',
       'vigencia del seguro vencimiento de póliza insurance expiry',
       'cartera', 'fecha',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_aseg',
       'Aseguradora',
       'Compañía que emitió la póliza del bien en garantía.',
       'aseguradora compañía de seguros insurer',
       'cartera', 'categoria',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_moneda',
       'Moneda del avalúo',
       'Divisa en que se expreso el avalúo del bien.',
       'moneda divisa del avalúo appraisal currency',
       'cartera', 'categoria',
       'interna', 'intradia',
       'obsoleto', NULL, NULL,
       'Iván Zepeda', DATE '2019-10-01', DATE '2020-10-01'
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_elegible',
       'Elegibilidad regulatoria',
       'Indica si la garantía es elegible como mitigante ante el regulador.',
       'elegible mitigante eligible collateral',
       'regulatorio', 'booleano',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_mitig_pct',
       'Mitigación de riesgo reconocida',
       'Proporción de la exposición que la garantía alcanza a mitigar.',
       'mitigacion cobertura de riesgo risk mitigation',
       'riesgo', 'decimal',
       'interna', 'semanal',
       'en_revision', 'porcentaje', 'mean',
       'Jorge Nieto', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_obs',
       'Observaciones del expediente',
       'Notas del analista sobre el expediente de la garantía.',
       'observaciones notas del expediente remarks',
       'cartera', 'texto',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';

-- pagos
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_folio',
       'Folio del pago',
       'Folio del pago recibido, único por operación de cobranza.',
       'folio del pago número de pago payment id',
       'operacion', 'texto',
       'publica', 'diaria',
       'en_revision', NULL, 'count',
       'Renata Fuentes', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_contrato',
       'Contrato al que se aplica',
       'Clave del crédito al que se aplicó el pago recibido.',
       'contrato credito loan reference',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_cli_id',
       'Cliente que paga',
       'Clave del cliente que realizó el pago.',
       'cliente pagador payer',
       'cliente', 'entero',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_f_pago',
       'Fecha de pago',
       'Día en que el cliente realizó el pago en el canal.',
       'fecha de pago día de pago payment date',
       'operacion', 'fecha',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_f_aplic',
       'Fecha de aplicación',
       'Día en que el pago quedó aplicado al contrato. Puede ser posterior a la fecha de pago.',
       'fecha de aplicación pagos aplicados posting date',
       'operacion', 'fecha',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_mto_total',
       'Monto del pago',
       'Importe total recibido antes de repartirlo entre capital, interés e IVA.',
       'monto del pago importe pagado payment amount',
       'operacion', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Daniel Ocampo', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_mto_cap',
       'Amortización de capital',
       'Parte del pago que reduce el saldo de capital del contrato.',
       'amortizacion abono a capital principal repayment amortización',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Renata Fuentes', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_mto_int',
       'Pago de intereses',
       'Parte del pago que cubre intereses ordinarios devengados.',
       'intereses pagados interés ordinario interest paid',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Renata Fuentes', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_mto_iva',
       'IVA del pago',
       'Impuesto al valor agregado trasladado en comisiones e intereses.',
       'iva impuesto value added tax',
       'contable', 'decimal',
       'restringida', 'diaria',
       'certificado', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_mto_com',
       'Comisiones cobradas',
       'Comisiones cobradas al cliente dentro del mismo pago.',
       'comisiones cargos fees',
       'operacion', 'decimal',
       'interna', 'mensual',
       'en_revision', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_mto_mora',
       'Intereses moratorios cobrados',
       'Intereses por atraso cobrados dentro del pago.',
       'moratorios intereses por atraso late interest',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Jorge Nieto', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_medio',
       'Medio de pago',
       'Ventanilla, domiciliación, transferencia o cargo a tarjeta.',
       'medio de pago forma de pago payment method',
       'operacion', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_canal',
       'Canal de captura del pago',
       'Canal por el que entró el pago: sucursal, portal, móvil o corresponsal.',
       'canal del pago punto de cobro payment channel',
       'operacion', 'categoria',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_ref_banc',
       'Referencia bancaria',
       'Referencia numérica con la que el banco identifica el depósito.',
       'referencia bancaria linea de captura bank reference',
       'operacion', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_cta_cargo',
       'Cuenta de cargo',
       'Cuenta del cliente de la que se tomó el importe domiciliado.',
       'cuenta de cargo clabe debit account',
       'operacion', 'texto',
       'restringida', 'mensual',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_banco_emis',
       'Banco emisor',
       'Institución desde la que se envio la transferencia.',
       'banco emisor institución de origen issuing bank',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_est',
       'Estatus del pago',
       'Aplicado, en transito o devuelto por el banco.',
       'estatus del pago situación del pago payment status',
       'operacion', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_dev_motivo',
       'Motivo de devolución',
       'Causa por la que el banco devolvió el pago domiciliado.',
       'devolucion rechazo del pago return reason',
       'operacion', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_f_dev',
       'Fecha de devolución',
       'Día en que el banco informó la devolución del pago.',
       'fecha de devolución día de rechazo return date',
       'operacion', 'fecha',
       'publica', 'semanal',
       'obsoleto', NULL, NULL,
       'Renata Fuentes', DATE '2020-01-01', DATE '2021-01-01'
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_conc',
       'Marca de conciliación',
       'Indica que el pago ya fue conciliado contra el estado de cuenta bancario.',
       'conciliacion conciliado reconciled conciliación',
       'contable', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_f_conc',
       'Fecha de conciliación',
       'Día en que el pago quedó conciliado con contabilidad.',
       'fecha de conciliación cuadre reconciliation date',
       'contable', 'fecha',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_poliza',
       'Póliza contable del pago',
       'Póliza del libro mayor donde quedó registrado el pago.',
       'poliza asiento contable journal entry',
       'contable', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Jorge Nieto', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_moneda',
       'Moneda del pago',
       'Divisa en que se recibió el pago, en ISO-4217.',
       'moneda del pago divisa payment currency',
       'operacion', 'categoria',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_tc',
       'Tipo de cambio aplicado',
       'Tipo de cambio con el que se valorizó un pago en moneda extranjera.',
       'tipo de cambio paridad exchange rate',
       'mercado', 'decimal',
       'publica', 'intradia',
       'certificado', NULL, 'mean',
       'Hugo Beltrán', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_anticipo',
       'Marca de pago anticipado',
       'Indica que el cliente pago antes de la fecha de exigibilidad.',
       'pago anticipado prepago prepayment',
       'operacion', 'booleano',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_parcial',
       'Marca de pago parcial',
       'Indica que el importe recibido no cubre la exhibición completa.',
       'pago parcial abono partial payment',
       'operacion', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Sofía Aranda', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_n_exhib',
       'Número de exhibición',
       'Número de la amortización del calendario que el pago cubre.',
       'exhibicion número de cuota installment number',
       'cartera', 'entero',
       'interna', 'semanal',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_dias_atraso',
       'Días de atraso al momento del pago',
       'Días que el contrato llevaba vencido cuando entró el pago.',
       'días de atraso atraso mora days past due',
       'cartera', 'entero',
       'publica', 'mensual',
       'en_revision', 'dias', 'mean',
       'Sofía Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_promesa',
       'Promesa de pago',
       'Fecha comprometida por el cliente en la gestion de cobranza.',
       'promesa de pago compromiso promise to pay',
       'operacion', 'fecha',
       'interna', 'semanal',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_gestor',
       'Gestor de cobranza',
       'Persona o despacho que gestionó la recuperación del adeudo.',
       'gestor despacho de cobranza collector',
       'operacion', 'texto',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';

-- provisiones
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_periodo',
       'Periodo de calculo',
       'Mes de cierre al que corresponde la calificación de la cartera.',
       'periodo mes de calculo reporting period',
       'riesgo', 'texto',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_contrato',
       'Contrato calificado',
       'Clave del crédito al que se le calculo la reserva.',
       'contrato crédito calificado rated loan',
       'cartera', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_cli_id',
       'Cliente calificado',
       'Clave del cliente titular del contrato calificado.',
       'cliente acreditado borrower',
       'cliente', 'entero',
       'interna', 'semanal',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_eprc',
       'Estimación preventiva para riesgos crediticios',
       'Estimación preventiva para riesgos crediticios del contrato en el periodo.',
       'eprc estimación preventiva provision loan loss provisión',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Sofía Aranda', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_reserva',
       'Reserva preventiva constituida',
       'Reservas preventivas ya constituidas contra el resultado del ejercicio.',
       'reservas preventivas reserva provisiones allowance',
       'riesgo', 'decimal',
       'interna', 'mensual',
       'en_revision', 'MXN', 'sum',
       'Daniel Ocampo', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_pi',
       'Probabilidad de incumplimiento',
       'Probabilidad de que el acreditado incumpla en los proximos doce meses.',
       'probabilidad de incumplimiento pd probability of default',
       'riesgo', 'decimal',
       'restringida', 'semanal',
       'certificado', 'porcentaje', 'mean',
       'Jorge Nieto', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_sp',
       'Severidad de la pérdida',
       'Porción de la exposición que se pierde si el acreditado incumple.',
       'severidad lgd loss given default',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Daniel Ocampo', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_ei',
       'Exposición al incumplimiento',
       'Saldo expuesto al momento del incumplimiento, con lineas dispuestas.',
       'exposicion ead exposure at default',
       'riesgo', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Ricardo Salas', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_pe',
       'Pérdida esperada',
       'Producto de probabilidad, severidad y exposición del contrato.',
       'pérdida esperada expected loss pe',
       'riesgo', 'decimal',
       'interna', 'mensual',
       'obsoleto', 'MXN', 'sum',
       'Daniel Ocampo', DATE '2023-07-01', DATE '2026-07-01'
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_grado',
       'Grado de riesgo',
       'Grado de riesgo asignado, de A-1 a E, según la metodología vigente.',
       'grado de riesgo calificación de cartera risk grade',
       'riesgo', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_metodo',
       'Metodología de calificación',
       'Metodología general del regulador o interna autorizada.',
       'metodologia modelo de calificación rating methodology',
       'regulatorio', 'categoria',
       'publica', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_cartera_tipo',
       'Tipo de cartera',
       'Comercial, de consumo o de vivienda, para elegir la metodología.',
       'tipo de cartera portafolio portfolio type',
       'cartera', 'categoria',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_f_calif',
       'Fecha de calificación',
       'Día en que el comite fijo la calificación del acreditado.',
       'fecha de calificación comite de crédito rating date',
       'riesgo', 'fecha',
       'restringida', 'mensual',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_mto_exp',
       'Monto expuesto',
       'Saldo del contrato considerado en el calculo de la reserva.',
       'monto expuesto saldo calificado exposure amount',
       'riesgo', 'decimal',
       'interna', 'intradia',
       'en_revision', 'MXN', 'sum',
       'Iván Zepeda', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_gar_recon',
       'Garantía reconocida',
       'Porción del saldo cubierta por garantías elegibles como mitigante.',
       'garantía reconocida cobertura recognised collateral',
       'riesgo', 'decimal',
       'interna', 'intradia',
       'certificado', 'MXN', 'sum',
       'Adriana Cortes', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_exp_neta',
       'Exposición neta de garantías',
       'Saldo expuesto una vez descontada la garantía reconocida.',
       'exposición neta descubierto net exposure',
       'riesgo', 'decimal',
       'interna', 'intradia',
       'certificado', 'MXN', 'sum',
       'Marcela Ríos', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_castigo',
       'Marca de castigo',
       'Indica que el contrato fue castigado y salió del balance.',
       'castigo quebranto charge off',
       'riesgo', 'booleano',
       'restringida', 'mensual',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_f_castigo',
       'Fecha de castigo',
       'Día en que se aplicó el castigo contable del contrato.',
       'fecha de castigo quebranto charge off date',
       'riesgo', 'fecha',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_quita',
       'Quita otorgada',
       'Importe condonado al acreditado dentro de un convenio de pago.',
       'quita condonacion debt forgiveness',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Adriana Cortes', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_reest',
       'Marca de reestructura',
       'Indica que el crédito fue reestructurado o renovado.',
       'reestructura renovacion restructured',
       'cartera', 'booleano',
       'publica', 'diaria',
       'en_revision', NULL, NULL,
       'Jorge Nieto', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_f_reest',
       'Fecha de reestructura',
       'Día en que se formalizó la reestructura del crédito.',
       'fecha de reestructura renovacion restructure date',
       'cartera', 'fecha',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_etapa',
       'Etapa de deterioro',
       'Etapa uno, dos o tres del modelo de pérdida crediticia esperada.',
       'etapa deterioro stage',
       'riesgo', 'categoria',
       'interna', 'semanal',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_dias_atr',
       'Días de atraso considerados',
       'Días de atraso con los que se calificó el contrato en el periodo.',
       'días de atraso atraso mora days past due',
       'riesgo', 'entero',
       'interna', 'diaria',
       'en_revision', 'dias', 'mean',
       'Iván Zepeda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_sensib',
       'Sensibilidad de la reserva',
       'Cambio en la reserva ante un movimiento de un punto en la probabilidad.',
       'sensibilidad elasticidad de la reserva provisión sensitivity',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Renata Fuentes', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_var_mes',
       'Variación mensual de la reserva',
       'Diferencia de la reserva contra el cierre del mes anterior.',
       'variacion movimiento de reservas monthly change',
       'riesgo', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Renata Fuentes', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_cob_pct',
       'Índice de cobertura de reservas',
       'Reservas constituidas entre la cartera vencida del periodo.',
       'cobertura de reservas icor coverage ratio',
       'riesgo', 'decimal',
       'interna', 'mensual',
       'obsoleto', 'porcentaje', 'mean',
       'Renata Fuentes', DATE '2021-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_mto_adic',
       'Reservas adicionales',
       'Reservas por encima de la metodología, autorizadas por el consejo.',
       'reservas adicionales reserva voluntaria additional provisions',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Ricardo Salas', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_libera',
       'Liberación de reservas',
       'Reservas liberadas al mejorar la calificación o al recuperar el crédito.',
       'liberación de reservas cancelación de reserva provisión release',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Daniel Ocampo', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_resp',
       'Area responsable del calculo',
       'Area que firma el calculo de reservas del periodo.',
       'responsable area de riesgos owner area',
       'riesgo', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Paola Íñiguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_obs',
       'Nota metodológica',
       'Explicación de los ajustes aplicados fuera de la metodología estándar.',
       'nota metodológica observaciones methodology note',
       'riesgo', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';

-- contabilidad
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_ctble',
       'Cuenta contable',
       'Cuenta del catalogo institucional donde se registra el movimiento.',
       'cuenta contable número de cuenta ledger account',
       'contable', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_nivel',
       'Nivel de la cuenta',
       'Nivel jerárquico de la cuenta dentro del catalogo contable.',
       'nivel jerarquía de la cuenta account level',
       'contable', 'entero',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_desc',
       'Nombre de la cuenta',
       'Descripción de la cuenta contable tal como aparece en el catalogo.',
       'nombre de la cuenta descripción contable account name',
       'contable', 'texto',
       'interna', 'mensual',
       'obsoleto', NULL, NULL,
       'Paola Íñiguez', DATE '2022-10-01', DATE '2025-10-01'
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_natur',
       'Naturaleza de la cuenta',
       'Deudora o acreedora, según el saldo que la cuenta acumula.',
       'naturaleza deudora o acreedora account nature',
       'contable', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Renata Fuentes', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_rubro',
       'Rubro del balance',
       'Rubro del balance o del estado de resultados donde suma la cuenta.',
       'rubro renglón del balance balance sheet line',
       'contable', 'categoria',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Renata Fuentes', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_grupo',
       'Agrupador regulatorio',
       'Agrupador con el que la cuenta se reporta al regulador.',
       'agrupador mapeo regulatorio regulatory grouping',
       'regulatorio', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_poliza',
       'Número de póliza',
       'Número de la póliza contable que agrupa las partidas del asiento.',
       'poliza asiento journal entry',
       'contable', 'texto',
       'interna', 'diaria',
       'certificado', NULL, 'count',
       'Paola Íñiguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_tipo_pol',
       'Tipo de póliza',
       'Ingreso, egreso o diario, según el origen del asiento.',
       'tipo de póliza clase de asiento entry type',
       'contable', 'categoria',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_f_conta',
       'Fecha contable',
       'Día al que se afecta el resultado, que manda sobre la fecha de captura.',
       'fecha contable fecha de afectación accounting date',
       'contable', 'fecha',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_f_reg',
       'Fecha de registro',
       'Día en que el asiento se capturó en el sistema contable.',
       'fecha de registro captura entry date',
       'contable', 'fecha',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_imp_cargo',
       'Importe cargo',
       'Importe cargado a la cuenta en la partida.',
       'cargo debe debit amount',
       'contable', 'decimal',
       'interna', 'mensual',
       'certificado', 'MXN', 'sum',
       'Daniel Ocampo', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_imp_abono',
       'Importe abono',
       'Importe abonado a la cuenta en la partida.',
       'abono haber credit amount',
       'contable', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Renata Fuentes', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_moneda',
       'Moneda del movimiento',
       'Divisa original de la partida, en ISO-4217.',
       'moneda divisa currency',
       'contable', 'categoria',
       'publica', 'diaria',
       'obsoleto', NULL, NULL,
       'Sofía Aranda', DATE '2021-04-01', DATE '2022-04-01'
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_tc',
       'Tipo de cambio contable',
       'Tipo de cambio del cierre con el que se valorizó la partida.',
       'tipo de cambio paridad contable exchange rate',
       'contable', 'decimal',
       'restringida', 'diaria',
       'certificado', NULL, 'mean',
       'Hugo Beltrán', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_imp_mxn',
       'Importe valorizado en pesos',
       'Importe de la partida ya convertido a pesos con el tipo de cambio.',
       'importe en pesos valorizado amount in pesos',
       'contable', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Renata Fuentes', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_cco',
       'Centro de costo',
       'Centro de costo al que se imputa el gasto o el ingreso.',
       'centro de costo gasto por area cost center',
       'contable', 'categoria',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_ue',
       'Unidad de negocio contable',
       'Unidad de negocio a la que se asigna el resultado de la partida.',
       'unidad de negocio linea de negocio business unit',
       'contable', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_suc',
       'Sucursal contable',
       'Sucursal a la que pertenece el movimiento del libro mayor.',
       'sucursal oficina contable branch',
       'contable', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_concepto',
       'Concepto del movimiento',
       'Descripción del gasto, del ingreso o del traspaso registrado.',
       'concepto glosa del gasto description',
       'contable', 'texto',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_ref',
       'Referencia del origen',
       'Clave con la que el sistema de origen identifica la operación.',
       'referencia folio de origen source reference',
       'contable', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Iván Zepeda', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_origen',
       'Sistema de origen',
       'Sistema que generó la partida: crédito, tesorería, nómina o manual.',
       'sistema de origen aplicativo source system',
       'contable', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_usuario',
       'Usuario que registro',
       'Usuario que capturó la póliza manual en el sistema contable.',
       'usuario capturista user',
       'contable', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_est',
       'Estatus de la póliza',
       'Borrador, autorizada o cancelada.',
       'estatus de la póliza situación del asiento entry status',
       'contable', 'categoria',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_f_cierre',
       'Fecha de cierre contable',
       'Día en que se cerró el periodo y la partida dejó de ser modificable.',
       'cierre contable fecha de cierre closing date',
       'contable', 'fecha',
       'interna', 'intradia',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_periodo',
       'Periodo contable',
       'Ejercicio y mes contable al que pertenece la partida.',
       'periodo contable mes accounting period',
       'contable', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_conc',
       'Marca de conciliación contable',
       'Indica que la partida fue conciliada contra el auxiliar del sistema origen.',
       'conciliacion cuadre reconciled conciliación',
       'contable', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Marcela Ríos', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_partida',
       'Número de partida',
       'Consecutivo de la partida dentro de la póliza.',
       'partida renglón del asiento line number',
       'contable', 'entero',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_cta_contra',
       'Cuenta de contrapartida',
       'Cuenta que recibe el movimiento contrario dentro del mismo asiento.',
       'contrapartida cuenta espejo offset account',
       'contable', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_ajuste',
       'Marca de ajuste',
       'Indica que la partida corrige un registro previo del mismo periodo.',
       'ajuste corrección contable adjustment',
       'contable', 'booleano',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_obs',
       'Glosa de la partida',
       'Texto libre que el capturista deja para explicar el asiento.',
       'glosa observaciones memo',
       'contable', 'texto',
       'interna', 'semanal',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';

-- tesoreria
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_f_pos',
       'Fecha de la posición de tesorería',
       'Día al que corresponde la posición consolidada de tesorería.',
       'posición de tesorería fecha de posición treasury position date',
       'liquidez', 'fecha',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_hora_corte',
       'Hora de corte',
       'Hora en que se congeló la posición de tesorería del día.',
       'hora de corte corte del día cut off time',
       'liquidez', 'texto',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_cta_teso',
       'Cuenta de tesorería',
       'Cuenta operativa de tesorería donde se concentra el efectivo.',
       'cuenta de tesorería cuenta concentradora treasury account',
       'liquidez', 'texto',
       'interna', 'semanal',
       'obsoleto', NULL, NULL,
       'Marcela Ríos', DATE '2021-01-01', DATE '2024-01-01'
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_banco',
       'Banco corresponsal',
       'Institución donde la tesorería mantiene la cuenta.',
       'banco corresponsal corresponsalia correspondent bank',
       'liquidez', 'categoria',
       'restringida', 'intradia',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_saldo_ini',
       'Saldo inicial del día',
       'Efectivo en tesorería al abrir la jornada.',
       'saldo inicial apertura opening balance',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Iván Zepeda', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_entradas',
       'Entradas del día',
       'Suma de las entradas de efectivo registradas en la jornada.',
       'entradas ingresos de efectivo cash in',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Adriana Cortes', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_salidas',
       'Salidas del día',
       'Suma de las salidas de efectivo registradas en la jornada.',
       'salidas egresos de efectivo cash out',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_saldo_fin',
       'Posición de cierre de tesorería',
       'Efectivo en tesorería al cerrar la jornada.',
       'saldo final posición de cierre closing balance',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'obsoleto', 'MXN', 'sum',
       'Ricardo Salas', DATE '2025-04-01', DATE '2027-04-01'
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_saldo_disp',
       'Disponible en tesorería',
       'Efectivo disponible para operar, sin considerar el comprometido.',
       'dinero disponible efectivo disponible available cash',
       'liquidez', 'decimal',
       'interna', 'mensual',
       'en_revision', 'MXN', 'sum',
       'Jorge Nieto', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_moneda',
       'Moneda de la posición',
       'Divisa de la cuenta de tesorería, en ISO-4217.',
       'moneda divisa currency',
       'liquidez', 'categoria',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_tc',
       'Tipo de cambio de la posición',
       'Tipo de cambio con el que se valoriza la posición en pesos.',
       'tipo de cambio paridad exchange rate',
       'mercado', 'decimal',
       'publica', 'semanal',
       'certificado', NULL, 'mean',
       'Adriana Cortes', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_saldo_mxn',
       'Posición valorizada en pesos',
       'Posición de tesorería convertida a pesos con el tipo de cambio del día.',
       'posición en pesos valorizado position in pesos',
       'liquidez', 'decimal',
       'interna', 'mensual',
       'en_revision', 'MXN', 'sum',
       'Jorge Nieto', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_flujo_neto',
       'Flujo neto del día',
       'Entradas menos salidas de efectivo de la jornada.',
       'flujo neto flujo de efectivo net cash flow',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_proy_1d',
       'Flujo proyectado a un día',
       'Proyección simulada del flujo de efectivo del siguiente día hábil.',
       'proyección a un día pronostico one day forecast',
       'liquidez', 'decimal',
       'interna', 'semanal',
       'certificado', 'MXN', 'sum',
       'Renata Fuentes', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_proy_5d',
       'Flujo proyectado a cinco días',
       'Proyección simulada del flujo acumulado de la siguiente semana hábil.',
       'proyección a cinco días pronóstico semanal five day forecast',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_proy_30d',
       'Flujo proyectado a treinta días',
       'Proyección simulada del flujo acumulado del siguiente mes.',
       'proyección a treinta días pronóstico mensual thirty day forecast',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_col_dispo',
       'Colateral disponible',
       'Títulos libres que la tesorería puede dar en garantía.',
       'colateral disponible títulos libres available collateral',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_col_compr',
       'Colateral comprometido',
       'Títulos ya entregados en garantía y no disponibles para operar.',
       'colateral comprometido títulos gravados pledged collateral',
       'liquidez', 'decimal',
       'interna', 'mensual',
       'certificado', 'MXN', 'sum',
       'Jorge Nieto', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_lin_credito',
       'Lineas de crédito disponibles',
       'Lineas interbancarias autorizadas y no dispuestas.',
       'lineas disponibles crédito interbancario credit lines',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Iván Zepeda', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_lin_usada',
       'Lineas dispuestas',
       'Importe ya dispuesto de las lineas interbancarias autorizadas.',
       'lineas dispuestas uso de lineas drawn lines',
       'liquidez', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Iván Zepeda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_call_money',
       'Fondeo interbancario a un día',
       'Fondeo tomado o colocado a un día en el mercado interbancario.',
       'call money fondeo a un día overnight funding',
       'liquidez', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_reporto',
       'Posición en reporto',
       'Saldo de operaciones de reporto vivas al cierre del día.',
       'reporto repo repurchase agreement',
       'liquidez', 'decimal',
       'interna', 'mensual',
       'obsoleto', 'MXN', 'sum',
       'Marcela Ríos', DATE '2021-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_encaje',
       'Depósito de regulación monetaria',
       'Depósito obligatorio en el banco central que no computa como disponible.',
       'encaje regulación monetaria reserve requirement',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Adriana Cortes', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_hqla',
       'Activos liquidos de alta calidad',
       'Títulos que califican como activos liquidos ante el regulador.',
       'hqla activos liquidos high quality liquid assets',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Iván Zepeda', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_salidas_30d',
       'Salidas netas a treinta días',
       'Salidas netas de efectivo estimadas para los proximos treinta días.',
       'salidas netas flujo a treinta días net cash outflows',
       'regulatorio', 'decimal',
       'interna', 'intradia',
       'certificado', 'MXN', 'sum',
       'Iván Zepeda', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_cash_pool',
       'Concentración de saldos',
       'Saldo barrido de las cuentas operativas hacia la concentradora.',
       'cash pooling barrido de saldos cash concentration',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_gap_1d',
       'Brecha de liquidez a un día',
       'Diferencia entre activos y pasivos que vencen al siguiente día hábil.',
       'brecha gap de liquidez liquidity gap',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Ricardo Salas', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_f_valor',
       'Fecha valor de la operación',
       'Día en que la operación de tesorería liquida efectivamente.',
       'fecha valor liquidacion value date liquidación',
       'liquidez', 'fecha',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_resp',
       'Responsable de la posición',
       'Operador de la mesa que firma la posición del día.',
       'responsable operador de mesa desk owner',
       'liquidez', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_obs',
       'Observaciones de la posición',
       'Notas del operador sobre movimientos extraordinarios del día.',
       'observaciones notas de la mesa remarks',
       'liquidez', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';

-- riesgo_mercado
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_f_val',
       'Fecha de valuación',
       'Día de mercado con el que se valuó la posición.',
       'fecha de valuación corte de mercado valuation date',
       'mercado', 'fecha',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_port',
       'Portafolio o mesa',
       'Mesa de operación a la que pertenece la posición valuada.',
       'mesa portafolio trading desk',
       'mercado', 'categoria',
       'interna', 'semanal',
       'obsoleto', NULL, NULL,
       'Paola Íñiguez', DATE '2025-10-01', DATE '2026-10-01'
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_libro',
       'Libro de negociación',
       'Libro contable donde vive la posición: negociación o disponible.',
       'libro book trading book',
       'mercado', 'categoria',
       'publica', 'semanal',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_instr',
       'Instrumento valuado',
       'Instrumento financiero de la posición: bono, swap, opción o divisa.',
       'instrumento producto instrument',
       'mercado', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Hugo Beltrán', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_factor',
       'Factor de riesgo',
       'Factor que mueve el valor de la posición: tasa, tipo de cambio o precio.',
       'factor de riesgo variable de mercado risk factor',
       'mercado', 'categoria',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Hugo Beltrán', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_pos_mtm',
       'Valor a mercado de la posición',
       'Valuación a mercado de la posición al cierre del día.',
       'valor de mercado mark to market marca a mercado',
       'mercado', 'decimal',
       'interna', 'mensual',
       'obsoleto', 'MXN', 'sum',
       'Sofía Aranda', DATE '2023-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_var_1d',
       'Valor en riesgo a un día',
       'Pérdida máxima esperada de la mesa en un día al nivel de confianza fijado.',
       'var valor en riesgo value at risk',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Sofía Aranda', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_var_10d',
       'Valor en riesgo a diez días',
       'Valor en riesgo escalado al horizonte regulatorio de diez días.',
       'var a diez días var regulatorio ten day value at risk',
       'regulatorio', 'decimal',
       'interna', 'intradia',
       'en_revision', 'MXN', 'sum',
       'Ricardo Salas', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_var_conf',
       'Nivel de confianza del VaR',
       'Nivel de confianza con el que se calculo el valor en riesgo.',
       'nivel de confianza percentil confidence level',
       'mercado', 'decimal',
       'interna', 'semanal',
       'en_revision', 'porcentaje', 'mean',
       'Adriana Cortes', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_metodo_var',
       'Metodología del VaR',
       'Histórica, paramétrica o simulación de Montecarlo.',
       'metodología del var modelo de riesgo var methodology',
       'mercado', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Paola Íñiguez', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_es',
       'Pérdida esperada en la cola',
       'Pérdida promedio en los escenarios peores que el valor en riesgo.',
       'expected shortfall cvar pérdida en la cola',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Iván Zepeda', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_bpv',
       'Sensibilidad a un punto base',
       'Cambio en el valor de la posición ante un movimiento de un punto base.',
       'bpv dv01 sensibilidad a tasa',
       'mercado', 'decimal',
       'interna', 'semanal',
       'certificado', 'MXN', 'sum',
       'Adriana Cortes', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_dur',
       'Duración',
       'Duración modificada del instrumento de tasa.',
       'duracion plazo promedio duration',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'mean',
       'Adriana Cortes', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_conv',
       'Convexidad',
       'Curvatura de la relación entre precio y tasa del instrumento.',
       'convexidad segunda derivada convexity',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'mean',
       'Hugo Beltrán', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_delta',
       'Delta de la posición',
       'Sensibilidad del valor de la opción al precio del subyacente.',
       'delta sensibilidad al subyacente option delta',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'sum',
       'Sofía Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_gamma',
       'Gamma de la posición',
       'Cambio de la delta ante un movimiento del subyacente.',
       'gamma convexidad de la opción option gamma',
       'mercado', 'decimal',
       'interna', 'mensual',
       'certificado', NULL, 'sum',
       'Daniel Ocampo', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_vega',
       'Vega de la posición',
       'Sensibilidad del valor de la opción a la volatilidad implicita.',
       'vega sensibilidad a volatilidad option vega',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', NULL, 'sum',
       'Paola Íñiguez', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_theta',
       'Theta de la posición',
       'Pérdida de valor de la opción por el paso del tiempo.',
       'theta decaimiento temporal option theta',
       'mercado', 'decimal',
       'restringida', 'mensual',
       'en_revision', NULL, 'sum',
       'Hugo Beltrán', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_stress_1',
       'Pérdida en escenario de estrés',
       'Pérdida de la mesa en el escenario de estrés principal del comite.',
       'estres escenario adverso stress loss',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Daniel Ocampo', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_backtest_exc',
       'Excepciones de backtesting',
       'Días del último año en que la pérdida superó el valor en riesgo.',
       'excepciones backtesting var breaches',
       'regulatorio', 'entero',
       'interna', 'diaria',
       'obsoleto', 'conteo', 'sum',
       'Jorge Nieto', DATE '2023-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_limite_var',
       'Límite de VaR autorizado',
       'Límite de valor en riesgo que el comite autorizó a la mesa.',
       'límite de var límite autorizado var limit',
       'mercado', 'decimal',
       'interna', 'intradia',
       'en_revision', 'MXN', 'max',
       'Paola Íñiguez', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_uso_limite',
       'Uso del límite',
       'Proporción del límite de riesgo que la mesa esta consumiendo.',
       'uso del límite consumo de límite limit usage',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Paola Íñiguez', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_exceso',
       'Marca de exceso de límite',
       'Indica que la mesa rebasó el límite autorizado en el día.',
       'exceso rebase de límite limit breach',
       'mercado', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_pnl_dia',
       'Resultado del día',
       'Resultado de la mesa por valuación y por operación en la jornada.',
       'resultado del día pnl daily profit and loss',
       'mercado', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_pnl_mtd',
       'Resultado del mes',
       'Resultado acumulado de la mesa en el mes en curso.',
       'resultado del mes pnl mensual month to date',
       'mercado', 'decimal',
       'interna', 'intradia',
       'en_revision', 'MXN', 'sum',
       'Renata Fuentes', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_pnl_ytd',
       'Resultado del ejercicio',
       'Resultado acumulado de la mesa en el ejercicio en curso.',
       'resultado del año pnl acumulado year to date',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_curva',
       'Curva de descuento',
       'Curva con la que se descuentan los flujos de la posición.',
       'curva curva de descuento discount curve',
       'mercado', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Íñiguez', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_tc_val',
       'Tipo de cambio de valuación',
       'Tipo de cambio de cierre usado para valuar posiciones en divisa.',
       'tipo de cambio paridad de cierre closing exchange rate',
       'mercado', 'decimal',
       'interna', 'mensual',
       'certificado', NULL, 'mean',
       'Paola Íñiguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_resp',
       'Responsable de la mesa',
       'Operador responsable del libro y de su consumo de límites.',
       'responsable de la mesa head de mesa desk head',
       'mercado', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_obs',
       'Observaciones de riesgo',
       'Notas del area de riesgos sobre la posición o el exceso del día.',
       'observaciones notas de riesgo risk remarks',
       'mercado', 'texto',
       'interna', 'intradia',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';

-- canales
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_cd',
       'Código de canal',
       'Clave del canal por el que entró la solicitud.',
       'código de canal clave de canal channel code',
       'operacion', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_desc',
       'Nombre del canal',
       'Sucursal, portal, aplicación móvil, fuerza de venta o corresponsal.',
       'canal punto de contacto channel',
       'operacion', 'categoria',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_tipo',
       'Tipo de canal',
       'Canal digital o canal presencial, para separar la venta remota.',
       'canal digital digital o presencial channel type',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_f_orig',
       'Fecha de originación',
       'Día en que se originó la solicitud en el canal.',
       'originacion fecha de originación origination date originación',
       'operacion', 'fecha',
       'publica', 'intradia',
       'certificado', NULL, NULL,
       'Adriana Cortes', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_folio_sol',
       'Folio de la solicitud',
       'Folio con el que el canal identifica la solicitud del cliente.',
       'folio de solicitud número de solicitud application id',
       'operacion', 'texto',
       'interna', 'intradia',
       'certificado', NULL, 'count',
       'Paola Íñiguez', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_cli_id',
       'Cliente solicitante',
       'Clave del cliente que presentó la solicitud.',
       'cliente solicitante applicant',
       'cliente', 'entero',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_prod',
       'Producto solicitado',
       'Producto de crédito que el cliente pidió en el canal.',
       'producto solicitado producto requested product',
       'cartera', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Sofía Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_mto_sol',
       'Monto solicitado',
       'Importe que el cliente pidió en la solicitud.',
       'monto solicitado importe pedido requested amount',
       'cartera', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Ricardo Salas', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_mto_aut',
       'Monto autorizado',
       'Importe que el comite o el motor de decisión autorizó.',
       'monto autorizado importe aprobado approved amount',
       'cartera', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Sofía Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_est_sol',
       'Estatus de la solicitud',
       'En tramite, autorizada, rechazada o desistida.',
       'estatus de la solicitud situacion application status',
       'operacion', 'categoria',
       'restringida', 'mensual',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_motivo_rech',
       'Motivo de rechazo',
       'Causa por la que la solicitud no prospero.',
       'motivo de rechazo causa de negativa rejection reason',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_f_resol',
       'Fecha de resolución',
       'Día en que la solicitud recibió respuesta definitiva.',
       'fecha de resolución respuesta decisión date',
       'operacion', 'fecha',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_t_resp_dias',
       'Tiempo de respuesta',
       'Días entre la solicitud y su resolución definitiva.',
       'tiempo de respuesta días de tramite turnaround time',
       'operacion', 'entero',
       'interna', 'diaria',
       'obsoleto', 'dias', 'mean',
       'Sofía Aranda', DATE '2019-01-01', DATE '2022-01-01'
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_promotor',
       'Promotor',
       'Persona de la fuerza de venta que atendió la solicitud.',
       'promotor asesor sales agent',
       'operacion', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_suc',
       'Sucursal de captura',
       'Sucursal donde se capturó la solicitud presencial.',
       'sucursal oficina branch',
       'operacion', 'categoria',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Ricardo Salas', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_disp',
       'Marca de disposición',
       'Indica que el crédito autorizado llegó a disponerse.',
       'disposicion crédito dispuesto disbursed',
       'cartera', 'booleano',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_f_disp',
       'Fecha de disposición',
       'Día en que el cliente dispuso el crédito autorizado.',
       'fecha de disposición desembolso disbursement date',
       'cartera', 'fecha',
       'interna', 'semanal',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_conv_pct',
       'Tasa de conversión',
       'Proporción de solicitudes del canal que terminan en crédito dispuesto.',
       'conversion tasa de conversión conversión rate',
       'operacion', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Marcela Ríos', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_costo_orig',
       'Costo de originación',
       'Costo atribuido a originar la solicitud por ese canal.',
       'costo de originación costo de adquisición acquisition cost',
       'operacion', 'decimal',
       'interna', 'mensual',
       'certificado', 'MXN', 'sum',
       'Jorge Nieto', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_camp',
       'Campana comercial',
       'Campana a la que se atribuye la solicitud.',
       'campana promocion campaign',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Ríos', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_utm',
       'Origen de la campana digital',
       'Etiqueta de origen con la que el portal atribuye la visita.',
       'utm origen de tráfico traffic source',
       'operacion', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Jorge Nieto', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_disp_movil',
       'Dispositivo de la solicitud',
       'Tipo de dispositivo desde el que se capturó la solicitud digital.',
       'dispositivo móvil o escritorio device',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_so',
       'Sistema operativo del dispositivo',
       'Sistema operativo del dispositivo desde el que se solicitó.',
       'sistema operativo plataforma operating system',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_geo_edo',
       'Entidad de la solicitud',
       'Estado desde el que se presentó la solicitud.',
       'estado entidad state',
       'operacion', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_abandono',
       'Marca de abandono',
       'Indica que el cliente dejó el flujo digital sin terminarlo.',
       'abandono flujo incompleto drop off',
       'operacion', 'booleano',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Renata Fuentes', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_paso_abandono',
       'Paso de abandono',
       'Paso del flujo digital donde el cliente se detuvo.',
       'paso de abandono etapa del flujo drop off step',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Iván Zepeda', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_nps',
       'Calificación de satisfacción',
       'Calificación que el cliente dio al canal al cerrar el tramite.',
       'satisfaccion nps satisfaction score',
       'operacion', 'entero',
       'interna', 'diaria',
       'certificado', NULL, 'mean',
       'Iván Zepeda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_reintento',
       'Número de reintentos',
       'Veces que el cliente reintento la solicitud tras un error del flujo.',
       'reintentos intentos retries',
       'operacion', 'entero',
       'interna', 'diaria',
       'en_revision', 'conteo', 'sum',
       'Paola Íñiguez', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_biometria',
       'Validación biometrica',
       'Indica que la identidad se válido con biometría en el canal digital.',
       'biometria validación de identidad biometric check',
       'operacion', 'booleano',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_obs',
       'Observaciones del canal',
       'Notas del promotor o del analista sobre la solicitud.',
       'observaciones notas del canal remarks',
       'operacion', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Jorge Nieto', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';

-- regulatorio
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_reporte',
       'Clave del reporte regulatorio',
       'Clave de la serie que se envía al regulador, del tipo R01 o R04.',
       'reporte regulatorio serie regulatory report',
       'regulatorio', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Daniel Ocampo', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_periodo',
       'Periodo reportado',
       'Mes o trimestre al que corresponde la información enviada.',
       'periodo reportado mes del reporte reporting period',
       'regulatorio', 'texto',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_f_envio',
       'Fecha de envio',
       'Día en que la institución transmitió el reporte al regulador.',
       'fecha de envio transmision submissión date',
       'regulatorio', 'fecha',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Hugo Beltrán', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_est_envio',
       'Estatus del envio',
       'Enviado, observado, en reproceso o aceptado por el regulador.',
       'estatus del envio situación del reporte submissión status',
       'regulatorio', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Hugo Beltrán', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_icap',
       'Índice de capitalización',
       'Capital neto entre activos ponderados por riesgo totales.',
       'icap índice de capitalización capital adequacy ratio',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'en_revision', 'porcentaje', 'mean',
       'Daniel Ocampo', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_cap_basico',
       'Capital básico',
       'Capital fundamental más capital básico no fundamental del periodo.',
       'capital básico tier uno tier one capital',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Marcela Ríos', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_cap_compl',
       'Capital complementario',
       'Instrumentos subordinados y reservas que computan como complementario.',
       'capital complementario tier dos tier two capital',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Iván Zepeda', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_cap_neto',
       'Capital neto',
       'Suma del capital básico y del complementario, neta de deducciones.',
       'capital neto capital regulatorio net capital',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_apr_credito',
       'Activos en riesgo de crédito',
       'Activos ponderados por riesgo de crédito del periodo.',
       'apr de crédito activos ponderados credit risk weighted assets',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_apr_mercado',
       'Activos en riesgo de mercado',
       'Activos ponderados por riesgo de mercado del periodo.',
       'apr de mercado riesgo de mercado market risk weighted assets',
       'regulatorio', 'decimal',
       'interna', 'semanal',
       'certificado', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_apr_oper',
       'Activos en riesgo operacional',
       'Activos ponderados por riesgo operacional del periodo.',
       'apr operacional riesgo operacional operational risk assets',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Renata Fuentes', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_apr_total',
       'Activos ponderados totales',
       'Suma de los activos ponderados por los tres tipos de riesgo.',
       'apr total activos ponderados totales total risk weighted assets',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'certificado', 'MXN', 'sum',
       'Hugo Beltrán', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_ccl',
       'Coeficiente de cobertura de liquidez reportado',
       'Activos liquidos entre salidas netas a treinta días, como se reporto.',
       'ccl coeficiente reportado reported liquidity ratio',
       'regulatorio', 'decimal',
       'interna', 'intradia',
       'certificado', 'porcentaje', 'mean',
       'Adriana Cortes', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_cfen',
       'Coeficiente de financiamiento estable',
       'Financiamiento estable disponible entre el requerido.',
       'cfen financiamiento estable net stable funding ratio',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'en_revision', 'porcentaje', 'mean',
       'Iván Zepeda', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_imor',
       'Índice de morosidad',
       'Cartera vencida entre cartera total al cierre del periodo.',
       'imor morosidad cartera vencida non performing loan ratio',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'certificado', 'porcentaje', 'mean',
       'Iván Zepeda', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_icor',
       'Índice de cobertura de cartera vencida',
       'Reservas entre cartera vencida al cierre del periodo.',
       'icor cobertura de cartera coverage ratio',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'certificado', 'porcentaje', 'mean',
       'Sofía Aranda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_roa',
       'Rendimiento sobre activos',
       'Resultado neto de doce meses entre activo total promedio.',
       'roa rendimiento sobre activos return on assets',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Hugo Beltrán', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_roe',
       'Rendimiento sobre capital',
       'Resultado neto de doce meses entre capital contable promedio.',
       'roe rendimiento sobre capital return on equity',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'en_revision', 'porcentaje', 'mean',
       'Adriana Cortes', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_mfin',
       'Margen financiero',
       'Ingresos por intereses menos gastos por intereses del periodo.',
       'margen financiero margen de interés net interest income',
       'regulatorio', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Paola Íñiguez', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_eficiencia',
       'Índice de eficiencia operativa',
       'Gasto de administración entre ingresos totales de la operación.',
       'eficiencia índice de eficiencia efficiency ratio',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'en_revision', 'porcentaje', 'mean',
       'Paola Íñiguez', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_r04c_saldo',
       'Saldo reportado en el R04-C',
       'Saldo de cartera comercial tal como se envio en el reporte R04-C.',
       'r04 cartera comercial reportada commercial loan report',
       'regulatorio', 'decimal',
       'interna', 'intradia',
       'en_revision', 'MXN', 'sum',
       'Marcela Ríos', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_f_corte',
       'Fecha de corte del reporte',
       'Día de cierre de la información contenida en el envio.',
       'fecha de corte corte cut off date',
       'regulatorio', 'fecha',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Daniel Ocampo', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_version',
       'Versión del envio',
       'Número de versión del envio cuando hubo reprocesos.',
       'version reenvio submissión versión',
       'regulatorio', 'entero',
       'restringida', 'semanal',
       'certificado', NULL, 'max',
       'Adriana Cortes', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_valid_est',
       'Resultado de la validación',
       'Resultado de las validaciones automáticas del regulador sobre el envio.',
       'validacion resultado de validación validation result',
       'regulatorio', 'categoria',
       'restringida', 'intradia',
       'en_revision', NULL, NULL,
       'Adriana Cortes', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_obs_cnbv',
       'Observación del regulador',
       'Texto de la observación que el regulador levantó sobre el envio.',
       'observación del regulador requerimiento regulator finding',
       'regulatorio', 'texto',
       'restringida', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltrán', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_resp',
       'Area responsable del envio',
       'Area que firma y responde por la información enviada.',
       'area responsable responsable del reporte owner area',
       'regulatorio', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Adriana Cortes', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_firma',
       'Funcionario que firma',
       'Funcionario facultado que firma electrónicamente el envio.',
       'firmante funcionario signing officer',
       'regulatorio', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Marcela Ríos', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_medio_env',
       'Medio de envio',
       'Canal por el que se transmitió el reporte al regulador.',
       'medio de envio canal de transmisión submissión channel',
       'regulatorio', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofía Aranda', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_acuse',
       'Acuse de recibo',
       'Folio del acuse con el que el regulador confirmó la recepción.',
       'acuse folio de acuse acknowledgement',
       'regulatorio', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Ricardo Salas', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_reproc',
       'Marca de reproceso',
       'Indica que la serie tuvo que reenviarse tras una observación.',
       'reproceso reenvio resubmission',
       'regulatorio', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Sofía Aranda', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';

-- notas tribales
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Los importes de SIC-Core están en pesos, no en miles. Sumarlos junto con mto_disp de liquidez sin escalar produce un total que no cuadra con contabilidad y que nadie detecta hasta el cierre.',
       'Aplica al sumar o comparar importes con el silo de liquidez.',
       'liquidez miles suma total importe',
       'Ricardo Salas', DATE '2025-09-18'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'sdo_cap';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La mora se corta al cierre de mes: un contrato que se pone al corriente el día dos sigue apareciendo con la mora del cierre anterior durante todo el mes.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Sofía Aranda', DATE '2025-10-02'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'dias_mora';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El estatus CAS es cartera castigada: sale del balance pero no del archivo. Cualquier suma de saldo que no lo excluya sobrestima la cartera viva.',
       'Aplica al totalizar saldos o cartera.',
       'saldo cartera total castigado suma',
       'Ricardo Salas', DATE '2025-09-25'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'est_cta';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El 01 es el código interno de pesos de SIC-Core, no el 484 de la norma ISO-4217. Un cruce por código de moneda contra TESO-Pos no casa ni una fila y no falla: devuelve vacio.',
       'Aplica al cruzar moneda con otro sistema.',
       'moneda divisa cruce iso',
       'Paola Íñiguez', DATE '2025-11-06'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'mon_cd';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'En una reestructura el origen sobreescribe la fecha de vencimiento sin conservar la original, así que la vida promedio del portafolio se alarga sin que ninguna columna lo explique.',
       'Aplica al analizar plazos, vencimientos o reestructuras.',
       'vencimiento plazo reestructura vida',
       'Marcela Ríos', DATE '2025-12-11'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'f_venc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'SIC-Core escribe la clave con el prefijo CLI-, TESO-Pos como entero pelado y DRV-Front con una letra verificadora. Cruzar por cadena da cero coincidencias; hay que normalizar a la clave entera compartida.',
       'Aplica siempre que se cruce el cliente con otro silo.',
       'cliente cruce clave contraparte identificador',
       'Paola Íñiguez', DATE '2025-08-14'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'cli_ref';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Esta en MILES de la divisa de la fila. El error clásico es sumarlo directo y publicar una cifra mil veces menor que la real.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Adriana Cortes', DATE '2025-09-30'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'mto_disp';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Agrupar por fecha valor en vez de fecha de posición corre la serie un día hábil. Los tableros del portal agrupan por fec_pos y por eso no coinciden con el reporte que la mesa saca de su propia terminal.',
       'Aplica solo a series de tiempo y agrupaciones por fecha.',
       'fecha valor posición serie agrupar',
       'Adriana Cortes', DATE '2025-11-04'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'fec_val';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El promedio simple del ratio no es el ratio del portafolio: hay que ponderar por mto_disp, que es lo que hace la serie preagregada del tablero.',
       'Aplica al promediar o agregar el ratio.',
       'promedio media ratio cobertura agregado',
       'Daniel Ocampo', DATE '2025-10-21'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'ratio_lcr';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El silo mezcla cinco divisas y no trae ninguna columna valorizada. Sumar sin convertir con el tipo de cambio es el error que este conjunto de datos existe para dramatizar.',
       'Aplica al sumar importes de más de una divisa.',
       'suma total divisa moneda tipo de cambio',
       'Adriana Cortes', DATE '2025-10-09'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'divisa';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El bucket ON junta saldos a la vista y overnight; tesorería los reporta por separado, y por eso los dos números nunca cuadran al primer intento.',
       'Aplica al comparar buckets contra el reporte de tesorería.',
       'bucket vista overnight tesorería plazo',
       'Adriana Cortes', DATE '2026-01-15'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'bucket_venc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'TESO-Pos solo conoce a ocho mil clientes de los sesenta mil del maestro: los que operan posiciones. Un cruce por cliente contra créditos pierde el resto sin avisar.',
       'Aplica al cruzar clientes entre liquidez y crédito.',
       'cliente cruce clave cobertura universo',
       'Paola Íñiguez', DATE '2025-12-03'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'id_cliente';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La fecha llega como TEXTO en formato AAAAMMDD del exportador de ancho fijo. Ordenar por esa columna funciona por casualidad y compararla con una fecha real falla; además hay veinte filas que no parsean.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Hugo Beltrán', DATE '2025-09-11'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'f_trade';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'DRV-Front no tiene columna de divisa: todo esta en dólares de forma implicita. Mezclar este nocional con importes en pesos sin convertir infla el total por el tipo de cambio entero.',
       'Aplica al sumar nocional con importes de otro silo.',
       'divisa moneda pesos suma nocional',
       'Hugo Beltrán', DATE '2025-10-16'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'nocional_usd';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La letra verificadora se calcula sobre los seis dígitos. Hay veinte contrapartes cuya clave decodifica fuera del universo de clientes y quedan huérfanas al cruzar: no son un error de captura, son operaciones con entidades que nunca entraron al maestro.',
       'Aplica al cruzar contrapartes con el maestro de clientes.',
       'contraparte cliente cruce huérfano maestro',
       'Paola Íñiguez', DATE '2025-11-27'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'ctpty_cd';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El valor a mercado viene con signo. Sumarlo sin separar activo de pasivo compensa exposiciones que el area de riesgos reporta brutas, y el total resultante no es comparable con el reporte regulatorio.',
       'Aplica al totalizar exposición o valor a mercado.',
       'exposición suma neto bruto valor',
       'Daniel Ocampo', DATE '2025-12-18'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'mtm_val';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La calificación es la del último comite, no la del día de la operación. Para riesgo vigente hay que leerla del maestro de clientes, que si se actualiza.',
       'Aplica al analizar calificación o riesgo de contraparte.',
       'calificación riesgo contraparte vigente',
       'Sofía Aranda', DATE '2026-02-05'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'cpty_rtg';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El folio es consecutivo por libro, no global: dos libros pueden repetir el mismo número. Contar operaciones sin agrupar por libro duplica el conteo.',
       'Aplica al contar operaciones.',
       'folio conteo operaciones libro duplicado',
       'Hugo Beltrán', DATE '2026-01-22'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'op_id';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El RFC llega del alta y no se revalida después. Los registros anteriores a 2019 traen homoclave capturada a mano y por eso cli_rfc_valid existe.',
       'Aplica al usar el RFC como clave o al validar identidad.',
       'rfc validación homoclave identidad',
       'Paola Íñiguez', DATE '2025-10-30'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'clientes'
   AND f.physical_name = 'cli_rfc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El ejecutivo responsable es el dueño del dato ante el comite de gobierno: cualquier corrección de la ficha del cliente pasa por el, no por el area de sistemas.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Paola Íñiguez', DATE '2025-08-21'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'clientes'
   AND f.physical_name = 'cli_ejecutivo';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El valor comercial es el del último avalúo, no el de hoy. Con avalúos de más de dos años el area de riesgos aplica un castigo del veinte por ciento que esta columna no refleja.',
       'Aplica al usar el valor de la garantía como cobertura.',
       'valor avalúo garantía vigencia cobertura',
       'Marcela Ríos', DATE '2025-11-13'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'garantias'
   AND f.physical_name = 'g_val_com';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Solo las garantías hipotecarias tienen folio real. El resto se identifica por contrato y no se puede cruzar con el registro público de la propiedad.',
       'Aplica al cruzar garantías con el registro público.',
       'hipotecaria registro folio real cruce',
       'Marcela Ríos', DATE '2026-01-08'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'garantias'
   AND f.physical_name = 'g_tipo';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La fecha de aplicación puede ser posterior a la de pago: un pago del viernes por la tarde se aplica el lunes y, en fin de mes, aparece en el mes siguiente.',
       'Aplica al cerrar el mes o al comparar pagos con cobranza.',
       'fecha pago mes cierre aplicación',
       'Iván Zepeda', DATE '2025-12-09'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'pagos'
   AND f.physical_name = 'pg_f_aplic';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Los intereses moratorios cobrados no reducen la mora del contrato: son un ingreso y viven en otra cuenta contable. Restarlos del saldo vencido es un error que se repite cada trimestre.',
       'Aplica al conciliar mora con cartera vencida.',
       'mora atraso ingreso vencida conciliar',
       'Iván Zepeda', DATE '2026-02-12'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'pagos'
   AND f.physical_name = 'pg_mto_mora';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La estimación del cierre se recalcula hasta el día diez del mes siguiente. Antes de esa fecha la cifra es preliminar y no coincide con la que se envía al regulador.',
       'Aplica al leer el cierre del mes en curso.',
       'estimación reserva cierre preliminar',
       'Sofía Aranda', DATE '2025-11-20'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'provisiones'
   AND f.physical_name = 'prv_eprc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El grado lo fija la metodología general del regulador salvo en cartera comercial, donde la institución usa metodología interna autorizada. Comparar grados entre tipos de cartera no significa nada.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Sofía Aranda', DATE '2025-09-04'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'provisiones'
   AND f.physical_name = 'prv_grado';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El catalogo contable cambio de estructura en 2024. Las cuentas anteriores se mapean con una tabla de equivalencias que vive en una hoja de calculo fuera del sistema, y es la razón de la mitad de las diferencias históricas.',
       'Aplica al comparar periodos anteriores a 2024.',
       'cuenta contable histórico equivalencia periodo',
       'Jorge Nieto', DATE '2025-10-07'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'contabilidad'
   AND f.physical_name = 'cta_ctble';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Las tres columnas de flujo proyectado son una proyección simulada del prototipo, no un pronóstico del area de tesorería. No se presentan como cifra oficial en ninguna pantalla.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Adriana Cortes', DATE '2026-02-19'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'tesoreria'
   AND f.physical_name = 'tes_proy_1d';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El valor en riesgo de la mesa se calcula al cierre con datos de mercado del día anterior. Compararlo contra el resultado del mismo día desalinea las dos series y hace ver excesos que no existieron.',
       'Aplica al comparar el VaR con el resultado del día.',
       'var mesa resultado comparar límite',
       'Daniel Ocampo', DATE '2026-01-29'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'riesgo_mercado'
   AND f.physical_name = 'mkt_var_1d';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El índice publicado es el del reporte enviado, que puede diferir del calculo interno hasta que llega el acuse de conformidad. La cifra de gestion y la regulatoria no son la misma hasta ese momento.',
       'Aplica al comparar cifras internas contra las reportadas.',
       'ICAP capital reporte acuse comparar',
       'Jorge Nieto', DATE '2026-03-05'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'regulatorio'
   AND f.physical_name = 'reg_icap';

COMMIT;

-- Lo que quedo sembrado, medido y no prometido. Es la unica salida
-- de make db-seed cuando psql corre en modo silencioso.
SELECT (SELECT count(*) FROM catalog_source)      AS fuentes,
       (SELECT count(*) FROM catalog_field)       AS campos,
       (SELECT count(*) FROM catalog_tribal_note) AS notas;
