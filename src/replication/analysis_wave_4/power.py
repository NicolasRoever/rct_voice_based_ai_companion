from decimal import ROUND_FLOOR, Decimal
from math import floor, isfinite, sqrt

from scipy.optimize import brentq
from scipy.stats import nct, t


def calculate_two_arm_power(*, n_per_arm, smd, alpha, rho=0.0, n_covariates=0):
    """Return two-sided power; adjusted power is a planning approximation."""
    if not isinstance(n_per_arm, int) or n_per_arm < 2:
        raise ValueError("n_per_arm must be an integer of at least 2.")
    if not isinstance(n_covariates, int) or n_covariates < 0:
        raise ValueError("n_covariates must be a nonnegative integer.")
    if not isfinite(smd) or smd < 0:
        raise ValueError("smd must be a finite, nonnegative effect magnitude.")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between 0 and 1.")
    if not 0 <= rho < 1:
        raise ValueError("rho must lie in [0, 1).")
    if rho > 0 and n_covariates == 0:
        raise ValueError("Baseline adjustment requires at least one covariate.")
    degrees_freedom = 2 * n_per_arm - 2 - n_covariates
    if degrees_freedom <= 0:
        raise ValueError("The model must have positive residual degrees of freedom.")
    noncentrality = smd * sqrt(n_per_arm / (2 * (1 - rho**2)))
    critical_value = t.isf(alpha / 2, degrees_freedom)
    return float(
        nct.sf(critical_value, degrees_freedom, noncentrality)
        + nct.cdf(-critical_value, degrees_freedom, noncentrality)
    )


def calculate_preregistered_power(
    *,
    n_total=400,
    smd=0.30,
    alpha=0.05,
    attrition=0.05,
    rho=0.40,
    n_covariates=3,
    target_ancova_power=0.90,
):
    """Return assumptions, powers, and manuscript values in one dictionary."""
    if not isinstance(n_total, int) or n_total < 4 or n_total % 2:
        raise ValueError("n_total must be an even integer of at least 4.")
    if not 0 <= attrition < 1:
        raise ValueError("attrition must lie in [0, 1).")
    if not 0 < target_ancova_power < 1:
        raise ValueError("target_ancova_power must lie strictly between 0 and 1.")
    if not isinstance(n_covariates, int) or n_covariates < 1:
        raise ValueError("ANCOVA requires at least one covariate column.")
    n_per_arm = n_total // 2
    n_complete_per_arm = int(
        (Decimal(n_per_arm) * (1 - Decimal(str(attrition)))).to_integral_value(
            rounding=ROUND_FLOOR
        )
    )
    power_arguments = {
        "n_per_arm": n_complete_per_arm,
        "smd": smd,
        "alpha": alpha,
    }
    power_ttest = calculate_two_arm_power(**power_arguments)
    power_ancova = calculate_two_arm_power(
        **power_arguments, rho=rho, n_covariates=n_covariates
    )

    def target_difference(correlation):
        return (
            calculate_two_arm_power(
                **power_arguments, rho=correlation, n_covariates=n_covariates
            )
            - target_ancova_power
        )

    if target_difference(0.0) >= 0:
        rho_required = 0.0
    elif smd == 0 or target_difference(0.999999) < 0:
        rho_required = None
    else:
        rho_required = float(brentq(target_difference, 0.0, 0.999999))

    return {
        "prereg_n_total": n_total,
        "prereg_n_per_arm": n_per_arm,
        "prereg_target_smd": f"{smd:.2f}",
        "prereg_alpha": f"{alpha:.2f}",
        "prereg_attrition_assumed": f"{100 * attrition:g}",
        "prereg_rho_assumed": f"{rho:.2f}",
        "prereg_n_complete_total": 2 * n_complete_per_arm,
        "prereg_n_complete_per_arm": n_complete_per_arm,
        "prereg_ancova_n_covariates": n_covariates,
        "prereg_power": floor(100 * power_ttest),
        "prereg_power_ancova": floor(100 * power_ancova),
        "prereg_power_pct": f"{100 * power_ttest:.1f}",
        "prereg_power_ancova_pct": f"{100 * power_ancova:.1f}",
        "prereg_ancova_target_power_pct": f"{100 * target_ancova_power:g}",
        "prereg_rho_required_for_target_power": rho_required,
        "prereg_power_ttest_proportion": power_ttest,
        "prereg_power_ancova_proportion": power_ancova,
    }
