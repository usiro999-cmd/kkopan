from __future__ import annotations

import math
from dataclasses import dataclass

ELECTRON_VOLT_J = 1.602176634e-19
MU_0 = 4e-7 * math.pi
DT_ENERGY_J = 17.6e6 * ELECTRON_VOLT_J
LAWSON_REFERENCE = 3e21

DISCLAIMER = (
    "Educational zero-dimensional D-T plasma model. Results are not suitable "
    "for reactor design, safety analysis, control decisions, or facility operation."
)

REACTIVITY_TABLE = (
    (1.0, 6.9e-27),
    (2.0, 2.9e-25),
    (5.0, 1.3e-23),
    (10.0, 1.1e-22),
    (15.0, 2.5e-22),
    (20.0, 4.2e-22),
    (30.0, 6.5e-22),
    (50.0, 8.7e-22),
    (100.0, 8.5e-22),
)


@dataclass(frozen=True)
class FusionInputs:
    temperature_kev: float
    density_1e20_m3: float
    confinement_time_s: float
    magnetic_field_t: float
    major_radius_m: float
    minor_radius_m: float
    elongation: float
    external_heating_mw: float


def _reactivity(temperature_kev: float) -> float:
    for (lower_t, lower_rate), (upper_t, upper_rate) in zip(
        REACTIVITY_TABLE, REACTIVITY_TABLE[1:]
    ):
        if lower_t <= temperature_kev <= upper_t:
            fraction = math.log(temperature_kev / lower_t) / math.log(
                upper_t / lower_t
            )
            return math.exp(
                math.log(lower_rate)
                + fraction * math.log(upper_rate / lower_rate)
            )
    return REACTIVITY_TABLE[0][1] if temperature_kev < 1 else REACTIVITY_TABLE[-1][1]


def analyze_plasma(values: FusionInputs) -> dict:
    density = values.density_1e20_m3 * 1e20
    thermal_energy_j = values.temperature_kev * 1e3 * ELECTRON_VOLT_J
    volume = (
        2
        * math.pi**2
        * values.major_radius_m
        * values.minor_radius_m**2
        * values.elongation
    )
    pressure_pa = 2 * density * thermal_energy_j
    magnetic_pressure_pa = values.magnetic_field_t**2 / (2 * MU_0)
    beta_percent = 100 * pressure_pa / magnetic_pressure_pa
    triple_product = density * values.temperature_kev * values.confinement_time_s
    stored_energy_mj = 3 * density * thermal_energy_j * volume / 1e6
    transport_loss_mw = stored_energy_mj / values.confinement_time_s

    reactivity = _reactivity(values.temperature_kev)
    fusion_power_mw = density**2 * reactivity * DT_ENERGY_J * volume / 4e6
    alpha_heating_mw = fusion_power_mw * 3.5 / 17.6
    plasma_gain = (
        fusion_power_mw / values.external_heating_mw
        if values.external_heating_mw > 0
        else None
    )
    net_heating_margin_mw = (
        values.external_heating_mw + alpha_heating_mw - transport_loss_mw
    )

    diagnostics = []
    lawson_ratio = triple_product / LAWSON_REFERENCE
    if lawson_ratio >= 1:
        diagnostics.append(
            "The reference Lawson triple-product threshold is exceeded in this model."
        )
    else:
        diagnostics.append(
            f"Triple product reaches {lawson_ratio:.1%} of the educational D-T reference."
        )
    if beta_percent > 5:
        diagnostics.append(
            "High beta indicates that MHD stability constraints require detailed analysis."
        )
    else:
        diagnostics.append(
            "Volume-averaged beta is moderate in this zero-dimensional estimate."
        )
    if net_heating_margin_mw < 0:
        diagnostics.append(
            "Estimated heating is below transport loss; the assumed state is not self-consistent."
        )
    else:
        diagnostics.append(
            "Estimated external plus alpha heating covers the modeled transport loss."
        )

    return {
        "volume_m3": round(volume, 3),
        "plasma_pressure_kpa": round(pressure_pa / 1e3, 3),
        "beta_percent": round(beta_percent, 3),
        "triple_product_kev_s_m3": triple_product,
        "lawson_reference_ratio": round(lawson_ratio, 4),
        "stored_energy_mj": round(stored_energy_mj, 3),
        "dt_reactivity_m3_s": reactivity,
        "fusion_power_mw": round(fusion_power_mw, 3),
        "alpha_heating_mw": round(alpha_heating_mw, 3),
        "transport_loss_mw": round(transport_loss_mw, 3),
        "plasma_gain_q": round(plasma_gain, 3) if plasma_gain is not None else None,
        "net_heating_margin_mw": round(net_heating_margin_mw, 3),
        "diagnostics": diagnostics,
        "assumptions": [
            "Equal electron and ion temperatures",
            "50:50 deuterium-tritium ion mixture",
            "Uniform density and temperature",
            "Toroidal volume with elliptical cross-section",
            "Tabulated log-interpolated D-T reactivity",
        ],
        "disclaimer": DISCLAIMER,
    }
