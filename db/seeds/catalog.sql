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
    ('creditos', 'Cartera de credito', 'Contratos de credito vigentes y vencidos con su saldo, su mora y su tasa. Es el silo que SIC-Core exporta cada noche.', 'Direccion de Credito', 'Ricardo Salas', 'SIC-Core', true),
    ('liquidez', 'Posiciones de liquidez', 'Posiciones diarias por cliente, divisa y bucket de vencimiento tal como las publica la mesa de tesoreria.', 'Tesoreria', 'Adriana Cortes', 'TESO-Pos', true),
    ('derivados', 'Operaciones de derivados', 'Operaciones vivas de la mesa de derivados con su nocional, su valor a mercado y su contraparte.', 'Mesa de Derivados', 'Hugo Beltran', 'DRV-Front', true),
    ('clientes', 'Maestro de clientes', 'Ficha unica del cliente: identificacion, domicilio fiscal, segmento y marcas de cumplimiento. Es el origen de la clave que los tres silos codifican de tres maneras distintas.', 'Datos y Gobierno', 'Paola Iniguez', 'MDM-Cli', false),
    ('garantias', 'Garantias y colaterales', 'Bienes y colaterales que respaldan los creditos, con su avaluo, su aforo y su elegibilidad regulatoria.', 'Direccion de Credito', 'Marcela Rios', 'GAR-Col', false),
    ('pagos', 'Pagos y cobranza', 'Pagos recibidos, su aplicacion al contrato y la gestion de cobranza asociada.', 'Operaciones', 'Ivan Zepeda', 'PAG-Cob', false),
    ('provisiones', 'Provisiones y reservas', 'Calificacion de cartera y estimacion preventiva para riesgos crediticios por contrato y periodo.', 'Riesgo de Credito', 'Sofia Aranda', 'PRV-Res', false),
    ('contabilidad', 'Contabilidad general', 'Catalogo de cuentas y movimientos del libro mayor, con su centro de costo y su poliza.', 'Contraloria', 'Jorge Nieto', 'CTB-GL', false),
    ('tesoreria', 'Tesoreria y flujo de efectivo', 'Posicion consolidada de tesoreria, colateral disponible y flujo proyectado del dia. Las proyecciones son simuladas.', 'Tesoreria', 'Adriana Cortes', 'TES-Flu', false),
    ('riesgo_mercado', 'Riesgo de mercado', 'Valor en riesgo, sensibilidades y consumo de limites por mesa y por libro de negociacion.', 'Riesgo de Mercado', 'Daniel Ocampo', 'RSK-Mkt', false),
    ('canales', 'Canales y originacion', 'Solicitudes originadas por cada canal, digital o presencial, con su resolucion y su tiempo de respuesta.', 'Banca Digital', 'Renata Fuentes', 'CAN-Ori', false),
    ('regulatorio', 'Reportes regulatorios', 'Series que la institucion envia al regulador: capital, liquidez, morosidad y rentabilidad, con su acuse.', 'Contraloria', 'Jorge Nieto', 'REG-Rep', false);

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
       'Sofia Aranda', DATE '2024-10-01', NULL
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
       'Marcela Rios', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'creditos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prod_cd',
       'Codigo de producto',
       'Familia de credito a la que pertenece el contrato.',
       'Product code Hipotecario Mortgage Automotriz Auto loan Credito PyME SME loan Tarjeta de credito Credit card Credito personal Personal loan hipoteca credito hipotecario credito automotriz linea de credito',
       'cartera', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2025-07-01', NULL
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
       'Days past due atraso dias de atraso morosidad cartera vencida',
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
       'Annual rate interes que paga tasa de interes costo anual',
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
       'Paola Iniguez', DATE '2020-01-01', NULL
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
       'Paola Iniguez', DATE '2025-04-01', NULL
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
       'Ivan Zepeda', DATE '2025-04-01', NULL
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
       'Paola Iniguez', DATE '2025-10-01', NULL
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
       'Sofia Aranda', DATE '2022-07-01', NULL
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
       'Ivan Zepeda', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'liquidez';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'divisa',
       'Divisa',
       'Divisa de la posicion, en ISO-4217.',
       'Currency Peso mexicano Mexican peso Dolar estadounidense US dollar Euro Libra esterlina Pound sterling Yen japones Japanese yen',
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
       'Business unit Tesoreria Treasury Banca de empresas Business banking Banca de personas Retail banking Mercados Markets Corporativo Corporate tesorería',
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
       'Paola Iniguez', DATE '2021-10-01', NULL
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
       'Paola Iniguez', DATE '2022-04-01', NULL
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
       'Marcela Rios', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'ctpty_cd',
       'Codigo de contraparte',
       'Clave de contraparte con prefijo C, seis digitos y letra verificadora. Es la misma entidad que cli_ref en creditos.',
       'Counterparty code exposicion con contrapartes riesgo de contraparte',
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
       'Marcela Rios', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'derivados';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'subyacente',
       'Subyacente',
       'Activo subyacente del contrato.',
       'Underlying TIIE 28 dias TIIE 28 days Cetes 91 dias Cetes 91 days Dolar contra peso US dollar against peso Euro contra peso Euro against peso Indice de precios y cotizaciones Mexican stock index Unidad de inversion Investment unit',
       'mercado', 'categoria',
       'interna', 'intradia',
       'en_revision', NULL, NULL,
       'Ivan Zepeda', DATE '2019-04-01', NULL
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
       'Notional nocional en dolares notional amount',
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
       'Mark to market valor de mercado marca a mercado valuacion a mercado',
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
       'Sofia Aranda', DATE '2023-10-01', NULL
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
       'Hugo Beltran', DATE '2023-10-01', DATE '2024-10-01'
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
       'Ivan Zepeda', DATE '2023-04-01', NULL
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
       'Marcela Rios', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_curp',
       'CURP del cliente',
       'Clave Unica de Registro de Poblacion, solo para persona fisica.',
       'curp clave unica de registro de poblacion national id',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_rzn_soc',
       'Razon social del cliente',
       'Nombre legal completo del cliente, sin truncar.',
       'razon social nombre del cliente legal name',
       'cliente', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Ivan Zepeda', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_nom_com',
       'Nombre comercial',
       'Nombre con el que opera el cliente cuando difiere de la razon social.',
       'nombre comercial marca trade name',
       'cliente', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_tipo_per',
       'Tipo de persona',
       'Persona fisica o persona moral, segun el alta fiscal.',
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
       'Ivan Zepeda', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_f_alta',
       'Fecha de alta del cliente',
       'Dia en que el cliente entro al maestro y quedo disponible para contratar.',
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
       'Dia de la baja. Nula mientras el cliente siga activo.',
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
       'Activo, inactivo o en depuracion por el area de datos.',
       'estatus del cliente situacion del cliente customer status',
       'cliente', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_calle',
       'Domicilio fiscal',
       'Calle y numero del domicilio fiscal declarado ante el SAT.',
       'domicilio direccion fiscal address',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_cp',
       'Codigo postal del domicilio',
       'Codigo postal del domicilio fiscal, cinco digitos.',
       'codigo postal cp postal code',
       'cliente', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2024-04-01', NULL
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
       'Paola Iniguez', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_dom_mun',
       'Municipio o alcaldia',
       'Municipio o alcaldia del domicilio fiscal.',
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
       'Telefono de contacto',
       'Telefono principal declarado por el cliente, a diez digitos.',
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
       'Correo electronico',
       'Correo de contacto usado para avisos y estados de cuenta.',
       'correo email correo electronico',
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
       'Actividad economica',
       'Giro del cliente segun el catalogo SCIAN del INEGI.',
       'giro actividad economica industry',
       'cliente', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Ivan Zepeda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_ing_anual',
       'Ingreso anual declarado',
       'Ingreso anual que el cliente declaro en su ultima actualizacion.',
       'ingresos facturacion anual annual income',
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
       'Indica si el RFC paso la validacion de estructura y homoclave.',
       'rfc valido validacion de rfc tax id validated',
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
       'Persona duena de la relacion y responsable del dato del cliente ante el comite de gobierno.',
       'dueno del dato responsable del dato ejecutivo de cuenta steward dueño',
       'cliente', 'texto',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2019-04-01', NULL
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
       'Calificacion interna del cliente',
       'Puntaje de comportamiento interno, de 0 a 1000.',
       'score interno calificacion del cliente internal score calificación',
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
       'Calificacion de buro',
       'Puntaje del buro de credito en la ultima consulta autorizada.',
       'buro de credito score de buro credit bureau score calificación',
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
       'Sofia Aranda', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_pep',
       'Persona politicamente expuesta',
       'Marca de persona politicamente expuesta segun la politica de cumplimiento.',
       'pep politicamente expuesta politically exposed person',
       'regulatorio', 'booleano',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'clientes';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cli_kyc_f_rev',
       'Fecha de la ultima revision KYC',
       'Dia de la ultima revision del expediente de conocimiento del cliente.',
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
       'Completo, incompleto o vencido segun la politica de cumplimiento.',
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
       'Numero de productos vivos que el cliente tiene contratados.',
       'productos contratados profundidad de relacion product holdings',
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
       'Antiguedad del cliente',
       'Dias transcurridos desde el alta del cliente en el maestro.',
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
       'Folio de la garantia',
       'Folio del expediente de garantia, unico por bien registrado.',
       'folio de garantia expediente collateral id garantía',
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
       'Clave del credito que la garantia respalda.',
       'contrato credito garantizado secured loan garantía',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_cli_id',
       'Cliente propietario del bien',
       'Clave del cliente duena del bien otorgado en garantia.',
       'cliente propietario collateral owner garantía',
       'cliente', 'entero',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Paola Iniguez', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_tipo',
       'Tipo de garantia',
       'Hipotecaria, prendaria, liquida, fiduciaria o aval personal.',
       'garantia hipotecaria hipoteca prenda collateral type garantía',
       'cartera', 'categoria',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_subtipo',
       'Subtipo de garantia',
       'Apertura del tipo: casa habitacion, local, maquinaria o deposito.',
       'subtipo clase de bien collateral subtype garantía',
       'cartera', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Hugo Beltran', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_desc',
       'Descripcion del bien',
       'Descripcion del inmueble o del bien mueble que respalda el credito.',
       'descripcion del bien inmueble collateral description',
       'cartera', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Ivan Zepeda', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_val_com',
       'Valor comercial de la garantia',
       'Valor comercial del bien segun el ultimo avaluo practicado.',
       'valor de la garantia avaluo valor comercial appraisal value garantía',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Marcela Rios', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_val_gar',
       'Valor de garantia reconocido',
       'Porcion del valor comercial que se reconoce como cobertura tras el aforo.',
       'valor reconocido cobertura de la garantia recognised value garantía',
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
       'Marcela Rios', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_f_avaluo',
       'Fecha del avaluo',
       'Dia en que el perito firmo el avaluo vigente.',
       'fecha de avaluo valuacion appraisal date',
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
       'Nombre del perito autorizado que practico el avaluo.',
       'perito valuador appraiser',
       'cartera', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_f_venc_av',
       'Vigencia del avaluo',
       'Fecha en que el avaluo deja de considerarse vigente.',
       'vigencia del avaluo caducidad appraisal expiry',
       'cartera', 'fecha',
       'interna', 'intradia',
       'en_revision', NULL, NULL,
       'Marcela Rios', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_inmueble_cp',
       'Codigo postal del inmueble',
       'Codigo postal donde se ubica el bien inmueble en garantia.',
       'cp del inmueble ubicacion property postal code garantía',
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
       'Estado donde se ubica el bien inmueble en garantia.',
       'estado del inmueble plaza property state garantía',
       'cartera', 'categoria',
       'restringida', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2019-10-01', NULL
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
       'Sofia Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_m2',
       'Superficie del inmueble',
       'Superficie en metros cuadrados registrada en el avaluo.',
       'metros cuadrados superficie surface',
       'cartera', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'sum',
       'Marcela Rios', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_reg_pub',
       'Folio real del registro publico',
       'Folio del Registro Publico de la Propiedad que ampara el inmueble.',
       'folio real registro publico land registry',
       'cartera', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_grav_prev',
       'Gravamenes previos',
       'Indica que el bien tiene gravamenes anteriores a favor de terceros.',
       'gravamen hipoteca previa prior lien',
       'riesgo', 'booleano',
       'interna', 'semanal',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_prelacion',
       'Grado de prelacion',
       'Lugar que ocupa la institucion en el cobro frente a otros acreedores.',
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
       'Razon credito valor',
       'Saldo del credito entre el valor comercial de la garantia.',
       'ltv credito valor loan to value garantía',
       'riesgo', 'decimal',
       'interna', 'mensual',
       'en_revision', 'porcentaje', 'mean',
       'Sofia Aranda', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_est',
       'Estatus de la garantia',
       'Vigente, liberada, adjudicada o en proceso judicial.',
       'estatus de la garantia situacion collateral status garantía',
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
       'Fecha de liberacion',
       'Dia en que la garantia se libero por pago total del credito.',
       'liberacion cancelacion de hipoteca release date garantía',
       'cartera', 'fecha',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_adjud',
       'Marca de adjudicacion',
       'Indica que el bien fue adjudicado a la institucion por incumplimiento.',
       'adjudicacion bien adjudicado foreclosed',
       'riesgo', 'booleano',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_seg_pol',
       'Poliza de seguro del bien',
       'Numero de poliza que cubre el bien otorgado en garantia.',
       'poliza seguro del inmueble insurance policy garantía',
       'cartera', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2024-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_seg_vig',
       'Vigencia del seguro',
       'Fecha en que vence la poliza de seguro del bien.',
       'vigencia del seguro vencimiento de poliza insurance expiry',
       'cartera', 'fecha',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_aseg',
       'Aseguradora',
       'Compania que emitio la poliza del bien en garantia.',
       'aseguradora compania de seguros insurer garantía',
       'cartera', 'categoria',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_moneda',
       'Moneda del avaluo',
       'Divisa en que se expreso el avaluo del bien.',
       'moneda divisa del avaluo appraisal currency',
       'cartera', 'categoria',
       'interna', 'intradia',
       'obsoleto', NULL, NULL,
       'Ivan Zepeda', DATE '2019-10-01', DATE '2020-10-01'
  FROM catalog_source s WHERE s.code = 'garantias';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'g_elegible',
       'Elegibilidad regulatoria',
       'Indica si la garantia es elegible como mitigante ante el regulador.',
       'elegible mitigante eligible collateral garantía',
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
       'Mitigacion de riesgo reconocida',
       'Proporcion de la exposicion que la garantia alcanza a mitigar.',
       'mitigacion cobertura de riesgo risk mitigation garantía',
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
       'Notas del analista sobre el expediente de la garantia.',
       'observaciones notas del expediente remarks garantía',
       'cartera', 'texto',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'garantias';

-- pagos
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_folio',
       'Folio del pago',
       'Folio del pago recibido, unico por operacion de cobranza.',
       'folio del pago numero de pago payment id operación',
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
       'Clave del credito al que se aplico el pago recibido.',
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
       'Clave del cliente que realizo el pago.',
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
       'Dia en que el cliente realizo el pago en el canal.',
       'fecha de pago dia de pago payment date',
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
       'Fecha de aplicacion',
       'Dia en que el pago quedo aplicado al contrato. Puede ser posterior a la fecha de pago.',
       'fecha de aplicacion pagos aplicados posting date aplicación',
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
       'Importe total recibido antes de repartirlo entre capital, interes e IVA.',
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
       'Amortizacion de capital',
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
       'intereses pagados interes ordinario interest paid',
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
       'Paola Iniguez', DATE '2023-04-01', NULL
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
       'Paola Iniguez', DATE '2024-04-01', NULL
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
       'Ventanilla, domiciliacion, transferencia o cargo a tarjeta.',
       'medio de pago forma de pago payment method',
       'operacion', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Ivan Zepeda', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_canal',
       'Canal de captura del pago',
       'Canal por el que entro el pago: sucursal, portal, movil o corresponsal.',
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
       'Referencia numerica con la que el banco identifica el deposito.',
       'referencia bancaria linea de captura bank reference',
       'operacion', 'texto',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_cta_cargo',
       'Cuenta de cargo',
       'Cuenta del cliente de la que se tomo el importe domiciliado.',
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
       'Institucion desde la que se envio la transferencia.',
       'banco emisor institucion de origen issuing bank',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_est',
       'Estatus del pago',
       'Aplicado, en transito o devuelto por el banco.',
       'estatus del pago situacion del pago payment status',
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
       'Motivo de devolucion',
       'Causa por la que el banco devolvio el pago domiciliado.',
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
       'Fecha de devolucion',
       'Dia en que el banco informo la devolucion del pago.',
       'fecha de devolucion dia de rechazo return date',
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
       'Marca de conciliacion',
       'Indica que el pago ya fue conciliado contra el estado de cuenta bancario.',
       'conciliacion conciliado reconciled conciliación',
       'contable', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_f_conc',
       'Fecha de conciliacion',
       'Dia en que el pago quedo conciliado con contabilidad.',
       'fecha de conciliacion cuadre reconciliation date conciliación',
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
       'Poliza contable del pago',
       'Poliza del libro mayor donde quedo registrado el pago.',
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
       'Divisa en que se recibio el pago, en ISO-4217.',
       'moneda del pago divisa payment currency',
       'operacion', 'categoria',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Ivan Zepeda', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_tc',
       'Tipo de cambio aplicado',
       'Tipo de cambio con el que se valorizo un pago en moneda extranjera.',
       'tipo de cambio paridad exchange rate',
       'mercado', 'decimal',
       'publica', 'intradia',
       'certificado', NULL, 'mean',
       'Hugo Beltran', DATE '2020-04-01', NULL
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
       'Paola Iniguez', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_parcial',
       'Marca de pago parcial',
       'Indica que el importe recibido no cubre la exhibicion completa.',
       'pago parcial abono partial payment',
       'operacion', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Sofia Aranda', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'pagos';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'pg_n_exhib',
       'Numero de exhibicion',
       'Numero de la amortizacion del calendario que el pago cubre.',
       'exhibicion numero de cuota installment number amortización',
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
       'Dias de atraso al momento del pago',
       'Dias que el contrato llevaba vencido cuando entro el pago.',
       'dias de atraso atraso mora days past due',
       'cartera', 'entero',
       'publica', 'mensual',
       'en_revision', 'dias', 'mean',
       'Sofia Aranda', DATE '2025-01-01', NULL
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
       'Persona o despacho que gestiono la recuperacion del adeudo.',
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
       'Mes de cierre al que corresponde la calificacion de la cartera.',
       'periodo mes de calculo reporting period calificación',
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
       'Clave del credito al que se le calculo la reserva.',
       'contrato credito calificado rated loan',
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
       'Estimacion preventiva para riesgos crediticios',
       'Estimacion preventiva para riesgos crediticios del contrato en el periodo.',
       'eprc estimacion preventiva provision loan loss provision estimación',
       'riesgo', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Sofia Aranda', DATE '2022-04-01', NULL
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
       'Severidad de la perdida',
       'Porcion de la exposicion que se pierde si el acreditado incumple.',
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
       'Exposicion al incumplimiento',
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
       'Perdida esperada',
       'Producto de probabilidad, severidad y exposicion del contrato.',
       'perdida esperada expected loss pe',
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
       'Grado de riesgo asignado, de A-1 a E, segun la metodologia vigente.',
       'grado de riesgo calificacion de cartera risk grade calificación',
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
       'Metodologia de calificacion',
       'Metodologia general del regulador o interna autorizada.',
       'metodologia modelo de calificacion rating methodology calificación',
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
       'Comercial, de consumo o de vivienda, para elegir la metodologia.',
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
       'Fecha de calificacion',
       'Dia en que el comite fijo la calificacion del acreditado.',
       'fecha de calificacion comite de credito rating date calificación',
       'riesgo', 'fecha',
       'restringida', 'mensual',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2019-01-01', NULL
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
       'Ivan Zepeda', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_gar_recon',
       'Garantia reconocida',
       'Porcion del saldo cubierta por garantias elegibles como mitigante.',
       'garantia reconocida cobertura recognised collateral garantía garantías',
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
       'Exposicion neta de garantias',
       'Saldo expuesto una vez descontada la garantia reconocida.',
       'exposicion neta descubierto net exposure garantías garantía',
       'riesgo', 'decimal',
       'interna', 'intradia',
       'certificado', 'MXN', 'sum',
       'Marcela Rios', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_castigo',
       'Marca de castigo',
       'Indica que el contrato fue castigado y salio del balance.',
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
       'Dia en que se aplico el castigo contable del contrato.',
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
       'Indica que el credito fue reestructurado o renovado.',
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
       'Dia en que se formalizo la reestructura del credito.',
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
       'Etapa uno, dos o tres del modelo de perdida crediticia esperada.',
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
       'Dias de atraso considerados',
       'Dias de atraso con los que se califico el contrato en el periodo.',
       'dias de atraso atraso mora days past due',
       'riesgo', 'entero',
       'interna', 'diaria',
       'en_revision', 'dias', 'mean',
       'Ivan Zepeda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_sensib',
       'Sensibilidad de la reserva',
       'Cambio en la reserva ante un movimiento de un punto en la probabilidad.',
       'sensibilidad elasticidad de la reserva provision sensitivity',
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
       'Variacion mensual de la reserva',
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
       'Indice de cobertura de reservas',
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
       'Reservas por encima de la metodologia, autorizadas por el consejo.',
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
       'Liberacion de reservas',
       'Reservas liberadas al mejorar la calificacion o al recuperar el credito.',
       'liberacion de reservas cancelacion de reserva provision release calificación',
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
       'Paola Iniguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'provisiones';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'prv_obs',
       'Nota metodologica',
       'Explicacion de los ajustes aplicados fuera de la metodologia estandar.',
       'nota metodologica observaciones methodology note',
       'riesgo', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Ivan Zepeda', DATE '2019-10-01', NULL
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
       'cuenta contable numero de cuenta ledger account',
       'contable', 'texto',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Ivan Zepeda', DATE '2021-07-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_nivel',
       'Nivel de la cuenta',
       'Nivel jerarquico de la cuenta dentro del catalogo contable.',
       'nivel jerarquia de la cuenta account level',
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
       'Descripcion de la cuenta contable tal como aparece en el catalogo.',
       'nombre de la cuenta descripcion contable account name',
       'contable', 'texto',
       'interna', 'mensual',
       'obsoleto', NULL, NULL,
       'Paola Iniguez', DATE '2022-10-01', DATE '2025-10-01'
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'cta_natur',
       'Naturaleza de la cuenta',
       'Deudora o acreedora, segun el saldo que la cuenta acumula.',
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
       'rubro renglon del balance balance sheet line',
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
       'Hugo Beltran', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_poliza',
       'Numero de poliza',
       'Numero de la poliza contable que agrupa las partidas del asiento.',
       'poliza asiento journal entry',
       'contable', 'texto',
       'interna', 'diaria',
       'certificado', NULL, 'count',
       'Paola Iniguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_tipo_pol',
       'Tipo de poliza',
       'Ingreso, egreso o diario, segun el origen del asiento.',
       'tipo de poliza clase de asiento entry type',
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
       'Dia al que se afecta el resultado, que manda sobre la fecha de captura.',
       'fecha contable fecha de afectacion accounting date',
       'contable', 'fecha',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_f_reg',
       'Fecha de registro',
       'Dia en que el asiento se capturo en el sistema contable.',
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
       'Sofia Aranda', DATE '2021-04-01', DATE '2022-04-01'
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_tc',
       'Tipo de cambio contable',
       'Tipo de cambio del cierre con el que se valorizo la partida.',
       'tipo de cambio paridad contable exchange rate',
       'contable', 'decimal',
       'restringida', 'diaria',
       'certificado', NULL, 'mean',
       'Hugo Beltran', DATE '2022-07-01', NULL
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
       'Sofia Aranda', DATE '2021-01-01', NULL
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
       'Ivan Zepeda', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_concepto',
       'Concepto del movimiento',
       'Descripcion del gasto, del ingreso o del traspaso registrado.',
       'concepto glosa del gasto description',
       'contable', 'texto',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2024-04-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_ref',
       'Referencia del origen',
       'Clave con la que el sistema de origen identifica la operacion.',
       'referencia folio de origen source reference operación',
       'contable', 'texto',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Ivan Zepeda', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_origen',
       'Sistema de origen',
       'Sistema que genero la partida: credito, tesoreria, nomina o manual.',
       'sistema de origen aplicativo source system tesorería',
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
       'Usuario que capturo la poliza manual en el sistema contable.',
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
       'Estatus de la poliza',
       'Borrador, autorizada o cancelada.',
       'estatus de la poliza situacion del asiento entry status',
       'contable', 'categoria',
       'restringida', 'diaria',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_f_cierre',
       'Fecha de cierre contable',
       'Dia en que se cerro el periodo y la partida dejo de ser modificable.',
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
       'Hugo Beltran', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_conc',
       'Marca de conciliacion contable',
       'Indica que la partida fue conciliada contra el auxiliar del sistema origen.',
       'conciliacion cuadre reconciled conciliación',
       'contable', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Marcela Rios', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'contabilidad';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mov_partida',
       'Numero de partida',
       'Consecutivo de la partida dentro de la poliza.',
       'partida renglon del asiento line number',
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
       'ajuste correccion contable adjustment',
       'contable', 'booleano',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2020-10-01', NULL
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
       'Fecha de la posicion de tesoreria',
       'Dia al que corresponde la posicion consolidada de tesoreria.',
       'posicion de tesoreria fecha de posicion treasury position date tesorería',
       'liquidez', 'fecha',
       'publica', 'mensual',
       'certificado', NULL, NULL,
       'Ivan Zepeda', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_hora_corte',
       'Hora de corte',
       'Hora en que se congelo la posicion de tesoreria del dia.',
       'hora de corte corte del dia cut off time tesorería',
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
       'Cuenta de tesoreria',
       'Cuenta operativa de tesoreria donde se concentra el efectivo.',
       'cuenta de tesoreria cuenta concentradora treasury account tesorería',
       'liquidez', 'texto',
       'interna', 'semanal',
       'obsoleto', NULL, NULL,
       'Marcela Rios', DATE '2021-01-01', DATE '2024-01-01'
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_banco',
       'Banco corresponsal',
       'Institucion donde la tesoreria mantiene la cuenta.',
       'banco corresponsal corresponsalia correspondent bank tesorería',
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
       'Saldo inicial del dia',
       'Efectivo en tesoreria al abrir la jornada.',
       'saldo inicial apertura opening balance tesorería',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Ivan Zepeda', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_entradas',
       'Entradas del dia',
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
       'Salidas del dia',
       'Suma de las salidas de efectivo registradas en la jornada.',
       'salidas egresos de efectivo cash out',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Hugo Beltran', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_saldo_fin',
       'Posicion de cierre de tesoreria',
       'Efectivo en tesoreria al cerrar la jornada.',
       'saldo final posicion de cierre closing balance tesorería',
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
       'Disponible en tesoreria',
       'Efectivo disponible para operar, sin considerar el comprometido.',
       'dinero disponible efectivo disponible available cash tesorería',
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
       'Moneda de la posicion',
       'Divisa de la cuenta de tesoreria, en ISO-4217.',
       'moneda divisa currency tesorería',
       'liquidez', 'categoria',
       'restringida', 'intradia',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_tc',
       'Tipo de cambio de la posicion',
       'Tipo de cambio con el que se valoriza la posicion en pesos.',
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
       'Posicion valorizada en pesos',
       'Posicion de tesoreria convertida a pesos con el tipo de cambio del dia.',
       'posicion en pesos valorizado position in pesos tesorería',
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
       'Flujo neto del dia',
       'Entradas menos salidas de efectivo de la jornada.',
       'flujo neto flujo de efectivo net cash flow',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltran', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_proy_1d',
       'Flujo proyectado a un dia',
       'Proyeccion simulada del flujo de efectivo del siguiente dia habil.',
       'proyeccion a un dia pronostico one day forecast',
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
       'Flujo proyectado a cinco dias',
       'Proyeccion simulada del flujo acumulado de la siguiente semana habil.',
       'proyeccion a cinco dias pronostico semanal five day forecast',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Paola Iniguez', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_proy_30d',
       'Flujo proyectado a treinta dias',
       'Proyeccion simulada del flujo acumulado del siguiente mes.',
       'proyeccion a treinta dias pronostico mensual thirty day forecast',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltran', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_col_dispo',
       'Colateral disponible',
       'Titulos libres que la tesoreria puede dar en garantia.',
       'colateral disponible titulos libres available collateral tesorería garantía',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Paola Iniguez', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_col_compr',
       'Colateral comprometido',
       'Titulos ya entregados en garantia y no disponibles para operar.',
       'colateral comprometido titulos gravados pledged collateral garantía',
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
       'Lineas de credito disponibles',
       'Lineas interbancarias autorizadas y no dispuestas.',
       'lineas disponibles credito interbancario credit lines',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Ivan Zepeda', DATE '2022-07-01', NULL
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
       'Ivan Zepeda', DATE '2023-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_call_money',
       'Fondeo interbancario a un dia',
       'Fondeo tomado o colocado a un dia en el mercado interbancario.',
       'call money fondeo a un dia overnight funding',
       'liquidez', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Paola Iniguez', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_reporto',
       'Posicion en reporto',
       'Saldo de operaciones de reporto vivas al cierre del dia.',
       'reporto repo repurchase agreement',
       'liquidez', 'decimal',
       'interna', 'mensual',
       'obsoleto', 'MXN', 'sum',
       'Marcela Rios', DATE '2021-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_encaje',
       'Deposito de regulacion monetaria',
       'Deposito obligatorio en el banco central que no computa como disponible.',
       'encaje regulacion monetaria reserve requirement regulación',
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
       'Titulos que califican como activos liquidos ante el regulador.',
       'hqla activos liquidos high quality liquid assets',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Ivan Zepeda', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_salidas_30d',
       'Salidas netas a treinta dias',
       'Salidas netas de efectivo estimadas para los proximos treinta dias.',
       'salidas netas flujo a treinta dias net cash outflows',
       'regulatorio', 'decimal',
       'interna', 'intradia',
       'certificado', 'MXN', 'sum',
       'Ivan Zepeda', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_cash_pool',
       'Concentracion de saldos',
       'Saldo barrido de las cuentas operativas hacia la concentradora.',
       'cash pooling barrido de saldos cash concentration concentración',
       'liquidez', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltran', DATE '2021-01-01', NULL
  FROM catalog_source s WHERE s.code = 'tesoreria';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'tes_gap_1d',
       'Brecha de liquidez a un dia',
       'Diferencia entre activos y pasivos que vencen al siguiente dia habil.',
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
       'Fecha valor de la operacion',
       'Dia en que la operacion de tesoreria liquida efectivamente.',
       'fecha valor liquidacion value date operación tesorería liquidación',
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
       'Responsable de la posicion',
       'Operador de la mesa que firma la posicion del dia.',
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
       'Observaciones de la posicion',
       'Notas del operador sobre movimientos extraordinarios del dia.',
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
       'Fecha de valuacion',
       'Dia de mercado con el que se valuo la posicion.',
       'fecha de valuacion corte de mercado valuation date',
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
       'Mesa de operacion a la que pertenece la posicion valuada.',
       'mesa portafolio trading desk operación',
       'mercado', 'categoria',
       'interna', 'semanal',
       'obsoleto', NULL, NULL,
       'Paola Iniguez', DATE '2025-10-01', DATE '2026-10-01'
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_libro',
       'Libro de negociacion',
       'Libro contable donde vive la posicion: negociacion o disponible.',
       'libro book trading book',
       'mercado', 'categoria',
       'publica', 'semanal',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_instr',
       'Instrumento valuado',
       'Instrumento financiero de la posicion: bono, swap, opcion o divisa.',
       'instrumento producto instrument',
       'mercado', 'categoria',
       'publica', 'diaria',
       'certificado', NULL, NULL,
       'Hugo Beltran', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_factor',
       'Factor de riesgo',
       'Factor que mueve el valor de la posicion: tasa, tipo de cambio o precio.',
       'factor de riesgo variable de mercado risk factor',
       'mercado', 'categoria',
       'restringida', 'semanal',
       'certificado', NULL, NULL,
       'Hugo Beltran', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_pos_mtm',
       'Valor a mercado de la posicion',
       'Valuacion a mercado de la posicion al cierre del dia.',
       'valor de mercado mark to market marca a mercado',
       'mercado', 'decimal',
       'interna', 'mensual',
       'obsoleto', 'MXN', 'sum',
       'Sofia Aranda', DATE '2023-10-01', DATE '2024-10-01'
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_var_1d',
       'Valor en riesgo a un dia',
       'Perdida maxima esperada de la mesa en un dia al nivel de confianza fijado.',
       'var valor en riesgo value at risk',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Sofia Aranda', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_var_10d',
       'Valor en riesgo a diez dias',
       'Valor en riesgo escalado al horizonte regulatorio de diez dias.',
       'var a diez dias var regulatorio ten day value at risk',
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
       'Metodologia del VaR',
       'Historica, parametrica o simulacion de Montecarlo.',
       'metodologia del var modelo de riesgo var methodology',
       'mercado', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Paola Iniguez', DATE '2023-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_es',
       'Perdida esperada en la cola',
       'Perdida promedio en los escenarios peores que el valor en riesgo.',
       'expected shortfall cvar perdida en la cola',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Ivan Zepeda', DATE '2021-10-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_bpv',
       'Sensibilidad a un punto base',
       'Cambio en el valor de la posicion ante un movimiento de un punto base.',
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
       'Duracion',
       'Duracion modificada del instrumento de tasa.',
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
       'Curvatura de la relacion entre precio y tasa del instrumento.',
       'convexidad segunda derivada convexity',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'mean',
       'Hugo Beltran', DATE '2020-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_delta',
       'Delta de la posicion',
       'Sensibilidad del valor de la opcion al precio del subyacente.',
       'delta sensibilidad al subyacente option delta',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', NULL, 'sum',
       'Sofia Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_gamma',
       'Gamma de la posicion',
       'Cambio de la delta ante un movimiento del subyacente.',
       'gamma convexidad de la opcion option gamma',
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
       'Vega de la posicion',
       'Sensibilidad del valor de la opcion a la volatilidad implicita.',
       'vega sensibilidad a volatilidad option vega',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', NULL, 'sum',
       'Paola Iniguez', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_theta',
       'Theta de la posicion',
       'Perdida de valor de la opcion por el paso del tiempo.',
       'theta decaimiento temporal option theta',
       'mercado', 'decimal',
       'restringida', 'mensual',
       'en_revision', NULL, 'sum',
       'Hugo Beltran', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_stress_1',
       'Perdida en escenario de estres',
       'Perdida de la mesa en el escenario de estres principal del comite.',
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
       'Dias del ultimo anio en que la perdida supero el valor en riesgo.',
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
       'Limite de VaR autorizado',
       'Limite de valor en riesgo que el comite autorizo a la mesa.',
       'limite de var limite autorizado var limit',
       'mercado', 'decimal',
       'interna', 'intradia',
       'en_revision', 'MXN', 'max',
       'Paola Iniguez', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_uso_limite',
       'Uso del limite',
       'Proporcion del limite de riesgo que la mesa esta consumiendo.',
       'uso del limite consumo de limite limit usage',
       'mercado', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Paola Iniguez', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_exceso',
       'Marca de exceso de limite',
       'Indica que la mesa rebaso el limite autorizado en el dia.',
       'exceso rebase de limite limit breach',
       'mercado', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2019-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_pnl_dia',
       'Resultado del dia',
       'Resultado de la mesa por valuacion y por operacion en la jornada.',
       'resultado del dia pnl daily profit and loss operación',
       'mercado', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Paola Iniguez', DATE '2023-10-01', NULL
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
       'resultado del anio pnl acumulado year to date',
       'mercado', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Hugo Beltran', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_curva',
       'Curva de descuento',
       'Curva con la que se descuentan los flujos de la posicion.',
       'curva curva de descuento discount curve',
       'mercado', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Paola Iniguez', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_tc_val',
       'Tipo de cambio de valuacion',
       'Tipo de cambio de cierre usado para valuar posiciones en divisa.',
       'tipo de cambio paridad de cierre closing exchange rate',
       'mercado', 'decimal',
       'interna', 'mensual',
       'certificado', NULL, 'mean',
       'Paola Iniguez', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'riesgo_mercado';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'mkt_resp',
       'Responsable de la mesa',
       'Operador responsable del libro y de su consumo de limites.',
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
       'Notas del area de riesgos sobre la posicion o el exceso del dia.',
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
       'Codigo de canal',
       'Clave del canal por el que entro la solicitud.',
       'codigo de canal clave de canal channel code',
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
       'Sucursal, portal, aplicacion movil, fuerza de venta o corresponsal.',
       'canal punto de contacto channel aplicación',
       'operacion', 'categoria',
       'interna', 'intradia',
       'certificado', NULL, NULL,
       'Marcela Rios', DATE '2020-04-01', NULL
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
       'Marcela Rios', DATE '2025-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_f_orig',
       'Fecha de originacion',
       'Dia en que se origino la solicitud en el canal.',
       'originacion fecha de originacion origination date originación',
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
       'folio de solicitud numero de solicitud application id',
       'operacion', 'texto',
       'interna', 'intradia',
       'certificado', NULL, 'count',
       'Paola Iniguez', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_cli_id',
       'Cliente solicitante',
       'Clave del cliente que presento la solicitud.',
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
       'Producto de credito que el cliente pidio en el canal.',
       'producto solicitado producto requested product',
       'cartera', 'categoria',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Sofia Aranda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_mto_sol',
       'Monto solicitado',
       'Importe que el cliente pidio en la solicitud.',
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
       'Importe que el comite o el motor de decision autorizo.',
       'monto autorizado importe aprobado approved amount',
       'cartera', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Sofia Aranda', DATE '2019-01-01', NULL
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
       'Fecha de resolucion',
       'Dia en que la solicitud recibio respuesta definitiva.',
       'fecha de resolucion respuesta decision date',
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
       'Dias entre la solicitud y su resolucion definitiva.',
       'tiempo de respuesta dias de tramite turnaround time',
       'operacion', 'entero',
       'interna', 'diaria',
       'obsoleto', 'dias', 'mean',
       'Sofia Aranda', DATE '2019-01-01', DATE '2022-01-01'
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_promotor',
       'Promotor',
       'Persona de la fuerza de venta que atendio la solicitud.',
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
       'Sucursal donde se capturo la solicitud presencial.',
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
       'Marca de disposicion',
       'Indica que el credito autorizado llego a disponerse.',
       'disposicion credito dispuesto disbursed',
       'cartera', 'booleano',
       'interna', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2024-07-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_f_disp',
       'Fecha de disposicion',
       'Dia en que el cliente dispuso el credito autorizado.',
       'fecha de disposicion desembolso disbursement date',
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
       'Tasa de conversion',
       'Proporcion de solicitudes del canal que terminan en credito dispuesto.',
       'conversion tasa de conversion conversion rate',
       'operacion', 'decimal',
       'interna', 'diaria',
       'certificado', 'porcentaje', 'mean',
       'Marcela Rios', DATE '2022-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_costo_orig',
       'Costo de originacion',
       'Costo atribuido a originar la solicitud por ese canal.',
       'costo de originacion costo de adquisicion acquisition cost originación',
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
       'Marcela Rios', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_utm',
       'Origen de la campana digital',
       'Etiqueta de origen con la que el portal atribuye la visita.',
       'utm origen de trafico traffic source',
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
       'Tipo de dispositivo desde el que se capturo la solicitud digital.',
       'dispositivo movil o escritorio device',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2019-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_so',
       'Sistema operativo del dispositivo',
       'Sistema operativo del dispositivo desde el que se solicito.',
       'sistema operativo plataforma operating system',
       'operacion', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Ivan Zepeda', DATE '2025-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_geo_edo',
       'Entidad de la solicitud',
       'Estado desde el que se presento la solicitud.',
       'estado entidad state',
       'operacion', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_abandono',
       'Marca de abandono',
       'Indica que el cliente dejo el flujo digital sin terminarlo.',
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
       'Ivan Zepeda', DATE '2021-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_nps',
       'Calificacion de satisfaccion',
       'Calificacion que el cliente dio al canal al cerrar el tramite.',
       'satisfaccion nps satisfaction score calificación',
       'operacion', 'entero',
       'interna', 'diaria',
       'certificado', NULL, 'mean',
       'Ivan Zepeda', DATE '2025-01-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_reintento',
       'Numero de reintentos',
       'Veces que el cliente reintento la solicitud tras un error del flujo.',
       'reintentos intentos retries',
       'operacion', 'entero',
       'interna', 'diaria',
       'en_revision', 'conteo', 'sum',
       'Paola Iniguez', DATE '2020-04-01', NULL
  FROM catalog_source s WHERE s.code = 'canales';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'can_biometria',
       'Validacion biometrica',
       'Indica que la identidad se valido con biometria en el canal digital.',
       'biometria validacion de identidad biometric check',
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
       'Clave de la serie que se envia al regulador, del tipo R01 o R04.',
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
       'Mes o trimestre al que corresponde la informacion enviada.',
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
       'Dia en que la institucion transmitio el reporte al regulador.',
       'fecha de envio transmision submission date',
       'regulatorio', 'fecha',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Hugo Beltran', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_est_envio',
       'Estatus del envio',
       'Enviado, observado, en reproceso o aceptado por el regulador.',
       'estatus del envio situacion del reporte submission status',
       'regulatorio', 'categoria',
       'interna', 'mensual',
       'certificado', NULL, NULL,
       'Hugo Beltran', DATE '2023-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_icap',
       'Indice de capitalizacion',
       'Capital neto entre activos ponderados por riesgo totales.',
       'icap indice de capitalizacion capital adequacy ratio capitalización',
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
       'Capital basico',
       'Capital fundamental mas capital basico no fundamental del periodo.',
       'capital basico tier uno tier one capital',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Marcela Rios', DATE '2023-04-01', NULL
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
       'Ivan Zepeda', DATE '2019-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_cap_neto',
       'Capital neto',
       'Suma del capital basico y del complementario, neta de deducciones.',
       'capital neto capital regulatorio net capital',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'en_revision', 'MXN', 'sum',
       'Hugo Beltran', DATE '2019-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_apr_credito',
       'Activos en riesgo de credito',
       'Activos ponderados por riesgo de credito del periodo.',
       'apr de credito activos ponderados credit risk weighted assets',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'certificado', 'MXN', 'sum',
       'Hugo Beltran', DATE '2019-01-01', NULL
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
       'Hugo Beltran', DATE '2024-10-01', NULL
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
       'Hugo Beltran', DATE '2020-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_ccl',
       'Coeficiente de cobertura de liquidez reportado',
       'Activos liquidos entre salidas netas a treinta dias, como se reporto.',
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
       'Ivan Zepeda', DATE '2023-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_imor',
       'Indice de morosidad',
       'Cartera vencida entre cartera total al cierre del periodo.',
       'imor morosidad cartera vencida non performing loan ratio',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'certificado', 'porcentaje', 'mean',
       'Ivan Zepeda', DATE '2022-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_icor',
       'Indice de cobertura de cartera vencida',
       'Reservas entre cartera vencida al cierre del periodo.',
       'icor cobertura de cartera coverage ratio',
       'regulatorio', 'decimal',
       'interna', 'mensual',
       'certificado', 'porcentaje', 'mean',
       'Sofia Aranda', DATE '2023-07-01', NULL
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
       'Hugo Beltran', DATE '2020-04-01', NULL
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
       'margen financiero margen de interes net interest income',
       'regulatorio', 'decimal',
       'interna', 'semanal',
       'en_revision', 'MXN', 'sum',
       'Paola Iniguez', DATE '2022-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_eficiencia',
       'Indice de eficiencia operativa',
       'Gasto de administracion entre ingresos totales de la operacion.',
       'eficiencia indice de eficiencia efficiency ratio operación',
       'regulatorio', 'decimal',
       'interna', 'diaria',
       'en_revision', 'porcentaje', 'mean',
       'Paola Iniguez', DATE '2020-04-01', NULL
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
       'Marcela Rios', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_f_corte',
       'Fecha de corte del reporte',
       'Dia de cierre de la informacion contenida en el envio.',
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
       'Version del envio',
       'Numero de version del envio cuando hubo reprocesos.',
       'version reenvio submission version',
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
       'Resultado de la validacion',
       'Resultado de las validaciones automaticas del regulador sobre el envio.',
       'validacion resultado de validacion validation result',
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
       'Observacion del regulador',
       'Texto de la observacion que el regulador levanto sobre el envio.',
       'observacion del regulador requerimiento regulator finding',
       'regulatorio', 'texto',
       'restringida', 'mensual',
       'en_revision', NULL, NULL,
       'Hugo Beltran', DATE '2025-07-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_resp',
       'Area responsable del envio',
       'Area que firma y responde por la informacion enviada.',
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
       'Funcionario facultado que firma electronicamente el envio.',
       'firmante funcionario signing officer',
       'regulatorio', 'texto',
       'restringida', 'diaria',
       'en_revision', NULL, NULL,
       'Marcela Rios', DATE '2022-04-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_medio_env',
       'Medio de envio',
       'Canal por el que se transmitio el reporte al regulador.',
       'medio de envio canal de transmision submission channel',
       'regulatorio', 'categoria',
       'interna', 'diaria',
       'certificado', NULL, NULL,
       'Sofia Aranda', DATE '2024-01-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';
INSERT INTO catalog_field (source_id, physical_name, business_name,
                           definition, aliases, domain, data_type,
                           sensitivity, refresh_frequency,
                           certification, unit, metric_agg, steward,
                           valid_from, valid_to)
SELECT s.id, 'reg_acuse',
       'Acuse de recibo',
       'Folio del acuse con el que el regulador confirmo la recepcion.',
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
       'Indica que la serie tuvo que reenviarse tras una observacion.',
       'reproceso reenvio resubmission',
       'regulatorio', 'booleano',
       'interna', 'diaria',
       'en_revision', NULL, NULL,
       'Sofia Aranda', DATE '2020-10-01', NULL
  FROM catalog_source s WHERE s.code = 'regulatorio';

-- notas tribales
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Los importes de SIC-Core estan en pesos, no en miles. Sumarlos junto con mto_disp de liquidez sin escalar produce un total que no cuadra con contabilidad y que nadie detecta hasta el cierre.',
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
SELECT f.id, 'La mora se corta al cierre de mes: un contrato que se pone al corriente el dia dos sigue apareciendo con la mora del cierre anterior durante todo el mes.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Sofia Aranda', DATE '2025-10-02'
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
SELECT f.id, 'El 01 es el codigo interno de pesos de SIC-Core, no el 484 de la norma ISO-4217. Un cruce por codigo de moneda contra TESO-Pos no casa ni una fila y no falla: devuelve vacio.',
       'Aplica al cruzar moneda con otro sistema.',
       'moneda divisa cruce iso',
       'Paola Iniguez', DATE '2025-11-06'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'mon_cd';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'En una reestructura el origen sobreescribe la fecha de vencimiento sin conservar la original, asi que la vida promedio del portafolio se alarga sin que ninguna columna lo explique.',
       'Aplica al analizar plazos, vencimientos o reestructuras.',
       'vencimiento plazo reestructura vida',
       'Marcela Rios', DATE '2025-12-11'
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
       'Paola Iniguez', DATE '2025-08-14'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'creditos'
   AND f.physical_name = 'cli_ref';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Esta en MILES de la divisa de la fila. El error clasico es sumarlo directo y publicar una cifra mil veces menor que la real.',
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
SELECT f.id, 'Agrupar por fecha valor en vez de fecha de posicion corre la serie un dia habil. Los tableros del portal agrupan por fec_pos y por eso no coinciden con el reporte que la mesa saca de su propia terminal.',
       'Aplica solo a series de tiempo y agrupaciones por fecha.',
       'fecha valor posicion serie agrupar',
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
       'Aplica al sumar importes de mas de una divisa.',
       'suma total divisa moneda tipo de cambio',
       'Adriana Cortes', DATE '2025-10-09'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'divisa';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El bucket ON junta saldos a la vista y overnight; tesoreria los reporta por separado, y por eso los dos numeros nunca cuadran al primer intento.',
       'Aplica al comparar buckets contra el reporte de tesoreria.',
       'bucket vista overnight tesoreria plazo',
       'Adriana Cortes', DATE '2026-01-15'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'bucket_venc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'TESO-Pos solo conoce a ocho mil clientes de los sesenta mil del maestro: los que operan posiciones. Un cruce por cliente contra creditos pierde el resto sin avisar.',
       'Aplica al cruzar clientes entre liquidez y credito.',
       'cliente cruce clave cobertura universo',
       'Paola Iniguez', DATE '2025-12-03'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'liquidez'
   AND f.physical_name = 'id_cliente';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La fecha llega como TEXTO en formato AAAAMMDD del exportador de ancho fijo. Ordenar por esa columna funciona por casualidad y compararla con una fecha real falla; ademas hay veinte filas que no parsean.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Hugo Beltran', DATE '2025-09-11'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'f_trade';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'DRV-Front no tiene columna de divisa: todo esta en dolares de forma implicita. Mezclar este nocional con importes en pesos sin convertir infla el total por el tipo de cambio entero.',
       'Aplica al sumar nocional con importes de otro silo.',
       'divisa moneda pesos suma nocional',
       'Hugo Beltran', DATE '2025-10-16'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'nocional_usd';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La letra verificadora se calcula sobre los seis digitos. Hay veinte contrapartes cuya clave decodifica fuera del universo de clientes y quedan huerfanas al cruzar: no son un error de captura, son operaciones con entidades que nunca entraron al maestro.',
       'Aplica al cruzar contrapartes con el maestro de clientes.',
       'contraparte cliente cruce huerfano maestro',
       'Paola Iniguez', DATE '2025-11-27'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'ctpty_cd';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El valor a mercado viene con signo. Sumarlo sin separar activo de pasivo compensa exposiciones que el area de riesgos reporta brutas, y el total resultante no es comparable con el reporte regulatorio.',
       'Aplica al totalizar exposicion o valor a mercado.',
       'exposicion suma neto bruto valor',
       'Daniel Ocampo', DATE '2025-12-18'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'mtm_val';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La calificacion es la del ultimo comite, no la del dia de la operacion. Para riesgo vigente hay que leerla del maestro de clientes, que si se actualiza.',
       'Aplica al analizar calificacion o riesgo de contraparte.',
       'calificacion riesgo contraparte vigente',
       'Sofia Aranda', DATE '2026-02-05'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'cpty_rtg';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El folio es consecutivo por libro, no global: dos libros pueden repetir el mismo numero. Contar operaciones sin agrupar por libro duplica el conteo.',
       'Aplica al contar operaciones.',
       'folio conteo operaciones libro duplicado',
       'Hugo Beltran', DATE '2026-01-22'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'derivados'
   AND f.physical_name = 'op_id';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El RFC llega del alta y no se revalida despues. Los registros anteriores a 2019 traen homoclave capturada a mano y por eso cli_rfc_valid existe.',
       'Aplica al usar el RFC como clave o al validar identidad.',
       'rfc validacion homoclave identidad',
       'Paola Iniguez', DATE '2025-10-30'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'clientes'
   AND f.physical_name = 'cli_rfc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El ejecutivo responsable es el dueno del dato ante el comite de gobierno: cualquier correccion de la ficha del cliente pasa por el, no por el area de sistemas.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Paola Iniguez', DATE '2025-08-21'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'clientes'
   AND f.physical_name = 'cli_ejecutivo';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El valor comercial es el del ultimo avaluo, no el de hoy. Con avaluos de mas de dos anios el area de riesgos aplica un castigo del veinte por ciento que esta columna no refleja.',
       'Aplica al usar el valor de la garantia como cobertura.',
       'valor avaluo garantia vigencia cobertura',
       'Marcela Rios', DATE '2025-11-13'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'garantias'
   AND f.physical_name = 'g_val_com';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Solo las garantias hipotecarias tienen folio real. El resto se identifica por contrato y no se puede cruzar con el registro publico de la propiedad.',
       'Aplica al cruzar garantias con el registro publico.',
       'hipotecaria registro folio real cruce',
       'Marcela Rios', DATE '2026-01-08'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'garantias'
   AND f.physical_name = 'g_tipo';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La fecha de aplicacion puede ser posterior a la de pago: un pago del viernes por la tarde se aplica el lunes y, en fin de mes, aparece en el mes siguiente.',
       'Aplica al cerrar el mes o al comparar pagos con cobranza.',
       'fecha pago mes cierre aplicacion',
       'Ivan Zepeda', DATE '2025-12-09'
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
       'Ivan Zepeda', DATE '2026-02-12'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'pagos'
   AND f.physical_name = 'pg_mto_mora';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'La estimacion del cierre se recalcula hasta el dia diez del mes siguiente. Antes de esa fecha la cifra es preliminar y no coincide con la que se envia al regulador.',
       'Aplica al leer el cierre del mes en curso.',
       'estimacion reserva cierre preliminar',
       'Sofia Aranda', DATE '2025-11-20'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'provisiones'
   AND f.physical_name = 'prv_eprc';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El grado lo fija la metodologia general del regulador salvo en cartera comercial, donde la institucion usa metodologia interna autorizada. Comparar grados entre tipos de cartera no significa nada.',
       'Aplica siempre que se lea esta columna.',
       '',
       'Sofia Aranda', DATE '2025-09-04'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'provisiones'
   AND f.physical_name = 'prv_grado';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El catalogo contable cambio de estructura en 2024. Las cuentas anteriores se mapean con una tabla de equivalencias que vive en una hoja de calculo fuera del sistema, y es la razon de la mitad de las diferencias historicas.',
       'Aplica al comparar periodos anteriores a 2024.',
       'cuenta contable historico equivalencia periodo',
       'Jorge Nieto', DATE '2025-10-07'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'contabilidad'
   AND f.physical_name = 'cta_ctble';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'Las tres columnas de flujo proyectado son una proyeccion simulada del prototipo, no un pronostico del area de tesoreria. No se presentan como cifra oficial en ninguna pantalla.',
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
SELECT f.id, 'El valor en riesgo de la mesa se calcula al cierre con datos de mercado del dia anterior. Compararlo contra el resultado del mismo dia desalinea las dos series y hace ver excesos que no existieron.',
       'Aplica al comparar el VaR con el resultado del dia.',
       'var mesa resultado comparar limite',
       'Daniel Ocampo', DATE '2026-01-29'
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = 'riesgo_mercado'
   AND f.physical_name = 'mkt_var_1d';
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author,
                                 recorded_at)
SELECT f.id, 'El indice publicado es el del reporte enviado, que puede diferir del calculo interno hasta que llega el acuse de conformidad. La cifra de gestion y la regulatoria no son la misma hasta ese momento.',
       'Aplica al comparar cifras internas contra las reportadas.',
       'icap capital reporte acuse comparar',
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
