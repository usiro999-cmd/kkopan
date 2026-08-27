import math

from app.services.fusion import FusionInputs, analyze_plasma


def baseline() -> FusionInputs:
    return FusionInputs(
        temperature_kev=15,
        density_1e20_m3=1,
        confinement_time_s=3,
        magnetic_field_t=5.3,
        major_radius_m=6.2,
        minor_radius_m=2,
        elongation=1.7,
        external_heating_mw=50,
    )


def test_baseline_analysis_has_physical_accounting() -> None:
    result = analyze_plasma(baseline())

    assert math.isclose(result["triple_product_kev_s_m3"], 4.5e21)
    assert result["lawson_reference_ratio"] == 1.5
    assert result["volume_m3"] > 800
    assert result["fusion_power_mw"] > 0
    assert math.isclose(
        result["alpha_heating_mw"],
        result["fusion_power_mw"] * 3.5 / 17.6,
        rel_tol=0.01,
    )


def test_density_increases_fusion_power_quadratically() -> None:
    base = analyze_plasma(baseline())
    dense_values = baseline().__dict__ | {"density_1e20_m3": 2}
    dense = analyze_plasma(FusionInputs(**dense_values))

    assert math.isclose(
        dense["fusion_power_mw"], base["fusion_power_mw"] * 4, rel_tol=1e-3
    )


def test_zero_external_heating_has_no_gain_ratio() -> None:
    values = baseline().__dict__ | {"external_heating_mw": 0}

    assert analyze_plasma(FusionInputs(**values))["plasma_gain_q"] is None
