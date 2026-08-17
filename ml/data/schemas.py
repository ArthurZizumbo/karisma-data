"""Frozen column contracts of the synthetic silos and of the dashboard series.

This module is the single source consumed by the semantic catalog seed: every
physical column carries its business label in both locales, its unit and its
default aggregation. It contains no generation logic on purpose, so that
importing it costs nothing and nobody has to retype a column name.

The three silos imitate three internal systems that never agreed on anything:
the same client is CLI-100042 in SIC-Core, 100042 in TESO-Pos and C100042C in
DRV-Front, amounts are pesos in one, thousands in another and dollars in the
third, and dates are native in two of them and fixed width text in the last
one. That heterogeneity is the product problem, not an accident.
"""

from dataclasses import dataclass
from datetime import date
from typing import Final

import polars as pl


@dataclass(frozen=True, slots=True)
class FieldSpec:
    """One physical column of a source system."""

    name: str
    dtype: pl.DataType
    label_es: str
    label_en: str
    description_es: str
    description_en: str
    unit: str | None = None
    domain: tuple[str, ...] | None = None
    is_client_key: bool = False
    aggregation: str | None = None


@dataclass(frozen=True, slots=True)
class SiloSpec:
    """One synthetic silo: its origin system, its owner and its columns."""

    name: str
    source_system: str
    owner: str
    rows: int
    fields: tuple[FieldSpec, ...]

    @property
    def columns(self) -> tuple[str, ...]:
        """Return the physical column names, in file order."""
        return tuple(field.name for field in self.fields)

    def polars_schema(self) -> dict[str, pl.DataType]:
        """Return the mapping the writer uses to pin every dtype."""
        return {field.name: field.dtype for field in self.fields}

    def field(self, name: str) -> FieldSpec:
        """Return one column by its physical name.

        Args:
            name: Physical column name.

        Returns:
            The matching specification.

        Raises:
            KeyError: If the column does not belong to this silo.
        """
        for field in self.fields:
            if field.name == name:
                return field
        raise KeyError(f"{self.name} has no column named {name!r}")


# --- Shared dimensions of the dashboard grid --------------------------------
# Their product is exactly 250, which is what makes the published series
# 2 000 dates x 250 keys = 500 000 rows. Adding one currency would silently
# turn the series into 600 000 points and no test outside this file would
# notice, which is why test_grid_dimensions_multiply_to_250 exists.
UNIDADES_NEGOCIO: Final[tuple[str, ...]] = (
    "TESORERIA",
    "BANCA_EMP",
    "BANCA_PER",
    "MERCADOS",
    "CORPORATIVO",
)
DIVISAS: Final[tuple[str, ...]] = ("MXN", "USD", "EUR", "GBP", "JPY")
BUCKETS_VENC: Final[tuple[str, ...]] = (
    "ON",
    "1D",
    "1S",
    "2S",
    "1M",
    "2M",
    "3M",
    "6M",
    "1A",
    ">1A",
)
N_SERIES: Final[int] = len(UNIDADES_NEGOCIO) * len(DIVISAS) * len(BUCKETS_VENC)

PRODUCTOS: Final[tuple[str, ...]] = ("HIP", "AUT", "PYM", "TDC", "PER")
ESTATUS_CUENTA: Final[tuple[str, ...]] = ("VIG", "VEN", "CAS", "LIQ")
TIPOS_POSICION: Final[tuple[str, ...]] = ("ACT", "PAS")
SUBYACENTES: Final[tuple[str, ...]] = (
    "TIIE28",
    "CETES91",
    "USDMXN",
    "EURMXN",
    "IPC",
    "UDI",
)
TIPOS_INSTRUMENTO: Final[tuple[str, ...]] = ("SWAP", "FWD", "OPC", "FUT")
CALIFICACIONES: Final[tuple[str, ...]] = ("AAA", "AA", "A", "BBB", "BB", "B")
MONEDA_INTERNA: Final[tuple[str, ...]] = ("01",)

# Value level labels. The interface is bilingual, so a code that reaches the
# screen without both locales shows up as a raw code in one of the two.
DOMAIN_LABELS: Final[dict[str, dict[str, tuple[str, str]]]] = {
    "prod_cd": {
        "HIP": ("Hipotecario", "Mortgage"),
        "AUT": ("Automotriz", "Auto loan"),
        "PYM": ("Crédito PyME", "SME loan"),
        "TDC": ("Tarjeta de crédito", "Credit card"),
        "PER": ("Crédito personal", "Personal loan"),
    },
    "est_cta": {
        "VIG": ("Vigente", "Current"),
        "VEN": ("Vencido", "Past due"),
        "CAS": ("Castigado", "Charged off"),
        "LIQ": ("Liquidado", "Settled"),
    },
    "mon_cd": {
        "01": ("Pesos mexicanos", "Mexican pesos"),
    },
    "unidad_negocio": {
        "TESORERIA": ("Tesorería", "Treasury"),
        "BANCA_EMP": ("Banca de empresas", "Business banking"),
        "BANCA_PER": ("Banca de personas", "Retail banking"),
        "MERCADOS": ("Mercados", "Markets"),
        "CORPORATIVO": ("Corporativo", "Corporate"),
    },
    "divisa": {
        "MXN": ("Peso mexicano", "Mexican peso"),
        "USD": ("Dólar estadounidense", "US dollar"),
        "EUR": ("Euro", "Euro"),
        "GBP": ("Libra esterlina", "Pound sterling"),
        "JPY": ("Yen japones", "Japanese yen"),
    },
    "bucket_venc": {
        "ON": ("A la vista", "Overnight"),
        "1D": ("Un dia", "One day"),
        "1S": ("Una semana", "One week"),
        "2S": ("Dos semanas", "Two weeks"),
        "1M": ("Un mes", "One month"),
        "2M": ("Dos meses", "Two months"),
        "3M": ("Tres meses", "Three months"),
        "6M": ("Seis meses", "Six months"),
        "1A": ("Un anio", "One year"),
        ">1A": ("Mas de un anio", "Over one year"),
    },
    "tipo_pos": {
        "ACT": ("Activo", "Asset"),
        "PAS": ("Pasivo", "Liability"),
    },
    "subyacente": {
        "TIIE28": ("TIIE 28 dias", "TIIE 28 days"),
        "CETES91": ("Cetes 91 dias", "Cetes 91 days"),
        "USDMXN": ("Dólar contra peso", "US dollar against peso"),
        "EURMXN": ("Euro contra peso", "Euro against peso"),
        "IPC": ("Indice de precios y cotizaciones", "Mexican stock index"),
        "UDI": ("Unidad de inversion", "Investment unit"),
    },
    "tipo_instr": {
        "SWAP": ("Swap", "Swap"),
        "FWD": ("Forward", "Forward"),
        "OPC": ("Opcion", "Option"),
        "FUT": ("Futuro", "Future"),
    },
    "cpty_rtg": {
        "AAA": ("Calificacion AAA", "AAA rating"),
        "AA": ("Calificacion AA", "AA rating"),
        "A": ("Calificacion A", "A rating"),
        "BBB": ("Calificacion BBB", "BBB rating"),
        "BB": ("Calificacion BB", "BB rating"),
        "B": ("Calificacion B", "B rating"),
    },
}

# Synthetic fixed exchange rate, in pesos per unit of currency. It is not a
# market quote and it is declared as synthetic in data/README.md and in the
# sidecar of the series, in both locales.
FX_MXN: Final[dict[str, float]] = {
    "MXN": 1.0,
    "USD": 17.85,
    "EUR": 19.40,
    "GBP": 22.60,
    "JPY": 0.118,
}

FECHA_FIN: Final[date] = date(2026, 6, 30)
DIAS_HABILES: Final[int] = 2000

N_CLIENTES: Final[int] = 60_000
N_CLIENTES_LIQUIDEZ: Final[int] = 8_000
N_CONTRAPARTES: Final[int] = 1_200
CLIENT_KEY_BASE: Final[int] = 100_000

# Check letter of the DRV-Front encoding. The I is out on purpose, the way a
# legacy fixed width export leaves out the letters it confuses with digits.
LETRAS_VERIFICADORAS: Final[str] = "ABCDEFGHJK"


CREDITOS: Final[SiloSpec] = SiloSpec(
    name="creditos",
    source_system="SIC-Core",
    owner="Direccion de Credito",
    rows=180_000,
    fields=(
        FieldSpec(
            name="cli_ref",
            dtype=pl.Utf8(),
            label_es="Referencia de cliente",
            label_en="Client reference",
            description_es=(
                "Clave del cliente con el prefijo CLI- que antepone SIC-Core. "
                "Es la misma entidad que id_cliente en liquidez y que ctpty_cd "
                "en derivados, con otra codificacion."
            ),
            description_en=(
                "Client key carrying the CLI- prefix that SIC-Core prepends. "
                "Same entity as id_cliente in liquidez and ctpty_cd in "
                "derivados, under a different encoding."
            ),
            is_client_key=True,
            aggregation="count",
        ),
        FieldSpec(
            name="nom_cli",
            dtype=pl.Utf8(),
            label_es="Nombre del cliente",
            label_en="Client name",
            description_es="Razon social truncada a 30 caracteres por el origen.",
            description_en="Legal name truncated to 30 characters by the source.",
        ),
        FieldSpec(
            name="prod_cd",
            dtype=pl.Utf8(),
            label_es="Codigo de producto",
            label_en="Product code",
            description_es="Familia de credito a la que pertenece el contrato.",
            description_en="Credit family the contract belongs to.",
            domain=PRODUCTOS,
        ),
        FieldSpec(
            name="sdo_cap",
            dtype=pl.Float64(),
            label_es="Saldo de capital",
            label_en="Outstanding principal",
            description_es="Capital insoluto en pesos, sin intereses.",
            description_en="Outstanding principal in pesos, interest excluded.",
            unit="MXN",
            aggregation="sum",
        ),
        FieldSpec(
            name="sdo_int",
            dtype=pl.Float64(),
            label_es="Intereses devengados",
            label_en="Accrued interest",
            description_es="Intereses devengados no cobrados, en pesos.",
            description_en="Accrued and uncollected interest, in pesos.",
            unit="MXN",
            aggregation="sum",
        ),
        FieldSpec(
            name="dias_mora",
            dtype=pl.Int16(),
            label_es="Dias de mora",
            label_en="Days past due",
            description_es="Dias transcurridos desde el primer pago no cubierto.",
            description_en="Days elapsed since the first missed payment.",
            unit="dias",
            aggregation="mean",
        ),
        FieldSpec(
            name="tasa_pct",
            dtype=pl.Float64(),
            label_es="Tasa anual",
            label_en="Annual rate",
            description_es="Tasa anual fija pactada, en por ciento.",
            description_en="Fixed annual rate agreed, in percent.",
            unit="%",
            aggregation="mean",
        ),
        FieldSpec(
            name="f_apert",
            dtype=pl.Date(),
            label_es="Fecha de apertura",
            label_en="Origination date",
            description_es="Fecha en que se origino el credito.",
            description_en="Date the credit was originated.",
        ),
        FieldSpec(
            name="f_venc",
            dtype=pl.Date(),
            label_es="Fecha de vencimiento",
            label_en="Maturity date",
            description_es="Fecha de vencimiento contractual.",
            description_en="Contractual maturity date.",
        ),
        FieldSpec(
            name="suc_cd",
            dtype=pl.Utf8(),
            label_es="Sucursal",
            label_en="Branch",
            description_es="Sucursal que origino el contrato, de S-001 a S-120.",
            description_en="Branch that originated the contract, S-001 to S-120.",
        ),
        FieldSpec(
            name="est_cta",
            dtype=pl.Utf8(),
            label_es="Estatus de la cuenta",
            label_en="Account status",
            description_es="Situacion contable del contrato.",
            description_en="Accounting situation of the contract.",
            domain=ESTATUS_CUENTA,
        ),
        FieldSpec(
            name="mon_cd",
            dtype=pl.Utf8(),
            label_es="Codigo de moneda",
            label_en="Currency code",
            description_es=(
                "Codigo interno de SIC-Core, no ISO-4217: 01 son pesos. Los "
                "importes de este silo estan en pesos, no en miles."
            ),
            description_en=(
                "SIC-Core internal code, not ISO-4217: 01 means pesos. Amounts "
                "in this silo are in pesos, not in thousands."
            ),
            domain=MONEDA_INTERNA,
        ),
    ),
)

LIQUIDEZ: Final[SiloSpec] = SiloSpec(
    name="liquidez",
    source_system="TESO-Pos",
    owner="Tesorería",
    rows=1_000_000,
    fields=(
        FieldSpec(
            name="fec_pos",
            dtype=pl.Date(),
            label_es="Fecha de posicion",
            label_en="Position date",
            description_es="Dia habil al que corresponde la posicion.",
            description_en="Business day the position belongs to.",
        ),
        FieldSpec(
            name="fec_val",
            dtype=pl.Date(),
            label_es="Fecha valor",
            label_en="Value date",
            description_es=(
                "Fecha de liquidacion, T+1 habil sobre fec_pos. No es la fecha "
                "de la posicion y agrupar por ella corre la serie un dia."
            ),
            description_en=(
                "Settlement date, one business day after fec_pos. It is not "
                "the position date and grouping by it shifts the series one "
                "day."
            ),
        ),
        FieldSpec(
            name="id_cliente",
            dtype=pl.Int64(),
            label_es="Identificador de cliente",
            label_en="Client identifier",
            description_es=(
                "Clave del cliente sin prefijo, como entero. Es la misma "
                "entidad que cli_ref en creditos."
            ),
            description_en=(
                "Bare integer client key. Same entity as cli_ref in creditos."
            ),
            is_client_key=True,
            aggregation="count",
        ),
        FieldSpec(
            name="cliente_desc",
            dtype=pl.Utf8(),
            label_es="Descripcion del cliente",
            label_en="Client description",
            description_es="Razon social completa, sin truncar.",
            description_en="Full legal name, not truncated.",
        ),
        FieldSpec(
            name="bucket_venc",
            dtype=pl.Utf8(),
            label_es="Bucket de vencimiento",
            label_en="Maturity bucket",
            description_es="Banda de vencimiento de la posicion.",
            description_en="Maturity band of the position.",
            domain=BUCKETS_VENC,
        ),
        FieldSpec(
            name="divisa",
            dtype=pl.Utf8(),
            label_es="Divisa",
            label_en="Currency",
            description_es="Divisa de la posicion, en ISO-4217.",
            description_en="Currency of the position, in ISO-4217.",
            domain=DIVISAS,
        ),
        FieldSpec(
            name="unidad_negocio",
            dtype=pl.Utf8(),
            label_es="Unidad de negocio",
            label_en="Business unit",
            description_es="Unidad que reporta la posicion.",
            description_en="Unit that reports the position.",
            domain=UNIDADES_NEGOCIO,
        ),
        FieldSpec(
            name="mto_disp",
            dtype=pl.Int64(),
            label_es="Monto disponible",
            label_en="Available amount",
            description_es=(
                "Monto disponible en MILES de la divisa de la fila. Sumarlo "
                "sin multiplicar por mil y sin convertir la divisa es el error "
                "que este conjunto de datos existe para dramatizar."
            ),
            description_en=(
                "Available amount in THOUSANDS of the row currency. Summing it "
                "without the factor of one thousand and without converting the "
                "currency is the mistake this dataset exists to dramatize."
            ),
            unit="miles de la divisa",
            aggregation="sum",
        ),
        FieldSpec(
            name="mto_comp",
            dtype=pl.Int64(),
            label_es="Monto comprometido",
            label_en="Committed amount",
            description_es="Monto ya comprometido, en miles de la divisa.",
            description_en="Committed amount, also in thousands of the currency.",
            unit="miles de la divisa",
            aggregation="sum",
        ),
        FieldSpec(
            name="ratio_lcr",
            dtype=pl.Float64(),
            label_es="Razon de cobertura",
            label_en="Coverage ratio",
            description_es="Razon de cobertura de liquidez de la posicion.",
            description_en="Liquidity coverage ratio of the position.",
            aggregation="mean",
        ),
        FieldSpec(
            name="tipo_pos",
            dtype=pl.Utf8(),
            label_es="Tipo de posicion",
            label_en="Position type",
            description_es="Activo o pasivo.",
            description_en="Asset or liability.",
            domain=TIPOS_POSICION,
        ),
    ),
)

DERIVADOS: Final[SiloSpec] = SiloSpec(
    name="derivados",
    source_system="DRV-Front",
    owner="Mesa de Derivados",
    rows=80_000,
    fields=(
        FieldSpec(
            name="op_id",
            dtype=pl.Utf8(),
            label_es="Folio de operacion",
            label_en="Trade identifier",
            description_es="Folio consecutivo de la operacion.",
            description_en="Consecutive trade number.",
            aggregation="count",
        ),
        FieldSpec(
            name="ctpty_cd",
            dtype=pl.Utf8(),
            label_es="Codigo de contraparte",
            label_en="Counterparty code",
            description_es=(
                "Clave de contraparte con prefijo C, seis digitos y letra "
                "verificadora. Es la misma entidad que cli_ref en creditos."
            ),
            description_en=(
                "Counterparty key with a C prefix, six digits and a check "
                "letter. Same entity as cli_ref in creditos."
            ),
            is_client_key=True,
        ),
        FieldSpec(
            name="ctpty_name",
            dtype=pl.Utf8(),
            label_es="Contraparte",
            label_en="Counterparty",
            description_es="Razon social en mayusculas y sin acentos.",
            description_en="Legal name in upper case and without accents.",
        ),
        FieldSpec(
            name="subyacente",
            dtype=pl.Utf8(),
            label_es="Subyacente",
            label_en="Underlying",
            description_es="Activo subyacente del contrato.",
            description_en="Underlying asset of the contract.",
            domain=SUBYACENTES,
        ),
        FieldSpec(
            name="tipo_instr",
            dtype=pl.Utf8(),
            label_es="Instrumento",
            label_en="Instrument",
            description_es="Familia del instrumento derivado.",
            description_en="Family of the derivative instrument.",
            domain=TIPOS_INSTRUMENTO,
        ),
        FieldSpec(
            name="nocional_usd",
            dtype=pl.Float64(),
            label_es="Nocional",
            label_en="Notional",
            description_es=(
                "Nocional en dolares. Este silo no lleva columna de divisa: "
                "todo esta en USD de forma implicita."
            ),
            description_en=(
                "Notional in US dollars. This silo carries no currency column: "
                "everything is implicitly in USD."
            ),
            unit="USD",
            aggregation="sum",
        ),
        FieldSpec(
            name="mtm_val",
            dtype=pl.Float64(),
            label_es="Valor a mercado",
            label_en="Mark to market",
            description_es="Valuacion a mercado en dolares, positiva o negativa.",
            description_en="Mark to market valuation in dollars, signed.",
            unit="USD",
            aggregation="sum",
        ),
        FieldSpec(
            name="f_trade",
            dtype=pl.Utf8(),
            label_es="Fecha de concertacion",
            label_en="Trade date",
            description_es=(
                "Fecha en TEXTO con formato AAAAMMDD, tal como la exporta el "
                "sistema legado de ancho fijo. No es un tipo fecha."
            ),
            description_en=(
                "Date as TEXT in YYYYMMDD form, the way the legacy fixed width "
                "system exports it. It is not a date type."
            ),
        ),
        FieldSpec(
            name="f_settle",
            dtype=pl.Utf8(),
            label_es="Fecha de liquidacion",
            label_en="Settlement date",
            description_es="Fecha de liquidacion en texto AAAAMMDD.",
            description_en="Settlement date as YYYYMMDD text.",
        ),
        FieldSpec(
            name="book_cd",
            dtype=pl.Utf8(),
            label_es="Libro",
            label_en="Book",
            description_es="Libro de la mesa, de BK-01 a BK-12.",
            description_en="Trading book, BK-01 to BK-12.",
        ),
        FieldSpec(
            name="cpty_rtg",
            dtype=pl.Utf8(),
            label_es="Calificacion",
            label_en="Rating",
            description_es="Calificacion crediticia de la contraparte.",
            description_en="Credit rating of the counterparty.",
            domain=CALIFICACIONES,
        ),
    ),
)

SILOS: Final[dict[str, SiloSpec]] = {
    "creditos": CREDITOS,
    "liquidez": LIQUIDEZ,
    "derivados": DERIVADOS,
}

SERIE_TABLERO: Final[SiloSpec] = SiloSpec(
    name="serie_tablero",
    source_system="Karisma Data",
    owner="Portal Centralizado",
    rows=DIAS_HABILES * N_SERIES,
    fields=(
        FieldSpec(
            name="serie_id",
            dtype=pl.UInt16(),
            label_es="Identificador de serie",
            label_en="Series identifier",
            description_es=(
                "Clave 0-249 derivada de unidad, divisa y bucket: "
                "unidad * 50 + divisa * 10 + bucket."
            ),
            description_en=(
                "0-249 key derived from unit, currency and bucket: "
                "unit * 50 + currency * 10 + bucket."
            ),
        ),
        FieldSpec(
            name="fecha",
            dtype=pl.Date(),
            label_es="Fecha",
            label_en="Date",
            description_es="Dia habil de la serie.",
            description_en="Business day of the series.",
        ),
        FieldSpec(
            name="unidad_negocio",
            dtype=pl.Utf8(),
            label_es="Unidad de negocio",
            label_en="Business unit",
            description_es="Unidad de negocio de la serie.",
            description_en="Business unit of the series.",
            domain=UNIDADES_NEGOCIO,
        ),
        FieldSpec(
            name="divisa",
            dtype=pl.Utf8(),
            label_es="Divisa",
            label_en="Currency",
            description_es="Divisa original de las posiciones agregadas.",
            description_en="Original currency of the aggregated positions.",
            domain=DIVISAS,
        ),
        FieldSpec(
            name="bucket_venc",
            dtype=pl.Utf8(),
            label_es="Bucket de vencimiento",
            label_en="Maturity bucket",
            description_es="Banda de vencimiento de las posiciones agregadas.",
            description_en="Maturity band of the aggregated positions.",
            domain=BUCKETS_VENC,
        ),
        FieldSpec(
            name="saldo_disponible_mxn",
            dtype=pl.Float64(),
            label_es="Saldo disponible",
            label_en="Available balance",
            description_es=(
                "Suma de mto_disp ya multiplicada por mil y convertida a pesos "
                "con el tipo de cambio sintetico fijo."
            ),
            description_en=(
                "Sum of mto_disp already multiplied by one thousand and "
                "converted to pesos with the fixed synthetic exchange rate."
            ),
            unit="MXN",
            aggregation="sum",
        ),
        FieldSpec(
            name="ratio_lcr",
            dtype=pl.Float64(),
            label_es="Razon de cobertura",
            label_en="Coverage ratio",
            description_es="Media de ratio_lcr ponderada por mto_disp.",
            description_en="Mean of ratio_lcr weighted by mto_disp.",
            aggregation="mean",
        ),
        FieldSpec(
            name="n_posiciones",
            dtype=pl.UInt32(),
            label_es="Posiciones",
            label_en="Positions",
            description_es="Filas crudas detras del punto. Siempre uno o mas.",
            description_en="Raw rows behind the point. Always one or more.",
            unit="filas",
            aggregation="sum",
        ),
    ),
)


def client_key_creditos(key: int) -> str:
    """Render a client key the way SIC-Core does, as CLI-100042.

    Args:
        key: Shared key in the range of N_CLIENTES.

    Returns:
        The prefixed reference.
    """
    return f"CLI-{CLIENT_KEY_BASE + key:06d}"


def client_key_liquidez(key: int) -> int:
    """Render a client key the way TESO-Pos does, as a bare integer.

    Args:
        key: Shared key in the range of N_CLIENTES.

    Returns:
        The integer identifier.
    """
    return CLIENT_KEY_BASE + key


def client_key_derivados(key: int) -> str:
    """Render a client key the way DRV-Front does, as C100042C.

    Args:
        key: Shared key in the range of N_CLIENTES.

    Returns:
        The prefixed code with its check letter.
    """
    number = CLIENT_KEY_BASE + key
    return f"C{number:06d}{LETRAS_VERIFICADORAS[number % 10]}"


def normalize_client_key(value: str | int, silo: str) -> int:
    """Reduce any of the three encodings to the shared integer key.

    This is the first piece of executable tribal knowledge of the project: the
    catalog documents it as a note and the lineage graph joins with it. The
    three encodings of the same client return the same number.

    A key that decodes correctly but falls outside the pool is returned, not
    rejected: that is exactly how the orphan counterparty anomaly becomes
    detectable downstream. What raises is a value written in the encoding of
    another silo, because returning a plausible integer for it would turn a
    reconciliation failure into a false match.

    Args:
        value: Column value as the silo stores it.
        silo: One of creditos, liquidez or derivados.

    Returns:
        The shared integer key.

    Raises:
        ValueError: If the silo is unknown or the value does not match the
            encoding of that silo.
    """
    if silo == "creditos":
        text = str(value)
        digits = text.removeprefix("CLI-")
        if not text.startswith("CLI-") or len(digits) != 6 or not digits.isdigit():
            raise ValueError(f"{value!r} is not a SIC-Core client reference")
        return int(digits)
    if silo == "liquidez":
        if isinstance(value, str):
            if not value.isdigit():
                raise ValueError(f"{value!r} is not a TESO-Pos client identifier")
            return int(value)
        return int(value)
    if silo == "derivados":
        text = str(value)
        digits = text[1:7]
        if (
            len(text) != 8
            or not text.startswith("C")
            or not digits.isdigit()
            or text[7] != LETRAS_VERIFICADORAS[int(digits) % 10]
        ):
            raise ValueError(f"{value!r} is not a DRV-Front counterparty code")
        return int(digits)
    raise ValueError(f"unknown silo {silo!r}")


def client_key_expr(silo: str) -> pl.Expr:
    """Return the vectorized twin of :func:`normalize_client_key`.

    The scalar function is the readable statement of the rule and this one is
    what a whole column goes through, so both have to say the same thing:
    test_client_key_expr_agrees_with_the_scalar_rule is what keeps them from
    drifting apart.

    Unlike the scalar function this expression does not reject a foreign
    encoding, it yields null for it: a column is audited row by row and a
    single malformed value must not abort the audit of the other million.

    Args:
        silo: One of creditos, liquidez or derivados.

    Returns:
        An expression that yields the shared integer key, or null when the
        value does not follow the encoding of that silo.

    Raises:
        ValueError: If the silo is unknown.
    """
    if silo == "creditos":
        return (
            pl.col("cli_ref")
            .str.extract(r"^CLI-(\d{6})$", 1)
            .cast(pl.Int64, strict=False)
        )
    if silo == "liquidez":
        return pl.col("id_cliente").cast(pl.Int64, strict=False)
    if silo == "derivados":
        digits = pl.col("ctpty_cd").str.extract(r"^C(\d{6})[A-HJK]$", 1)
        letra = pl.col("ctpty_cd").str.slice(7, 1)
        esperada = (
            pl.lit(LETRAS_VERIFICADORAS)
            .str.slice(digits.cast(pl.Int64, strict=False) % 10, 1)
            .alias("esperada")
        )
        return (
            pl.when(letra == esperada)
            .then(digits.cast(pl.Int64, strict=False))
            .otherwise(None)
        )
    raise ValueError(f"unknown silo {silo!r}")


def serie_id(unidad: str, divisa: str, bucket: str) -> int:
    """Return the 0-249 identifier of a dashboard series.

    Args:
        unidad: Business unit, from UNIDADES_NEGOCIO.
        divisa: Currency, from DIVISAS.
        bucket: Maturity bucket, from BUCKETS_VENC.

    Returns:
        The identifier used as the physical sort key of the published series.

    Raises:
        ValueError: If any of the three values is outside its dimension.
    """
    try:
        unidad_idx = UNIDADES_NEGOCIO.index(unidad)
        divisa_idx = DIVISAS.index(divisa)
        bucket_idx = BUCKETS_VENC.index(bucket)
    except ValueError as error:
        raise ValueError(
            f"({unidad!r}, {divisa!r}, {bucket!r}) is not a cell of the grid"
        ) from error
    return unidad_idx * 50 + divisa_idx * 10 + bucket_idx
