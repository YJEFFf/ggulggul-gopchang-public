"""매출 금액 정리와 주문 건수 회귀. 입력값·계수는 포함하지 않습니다."""

import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf


def food_sales(orders, tip):
    """음식금액에서 즉시할인을 차감하고, 결측 시 결제금액과 전달된 배달료로 추정합니다."""
    known = orders["음식금액"] - orders["가게즉시할인"].fillna(0)
    estimated = orders["고객결제금액"] - np.where(
        orders["서비스유형"] == "가게배달", tip, 0)
    return known.where(orders["음식금액"].notna(), estimated)


def glm(formula, data, family="poisson"):
    fam = sm.families.Poisson() if family == "poisson" else sm.families.NegativeBinomial(alpha=1.0)
    if family == "nb":
        # alpha 추정: statsmodels NegativeBinomial(이산 모형)으로 alpha를 구해 GLM에 넣는다
        try:
            nbm = smf.negativebinomial(formula, data).fit(disp=0, maxiter=200)
            alpha = float(nbm.params.get("alpha", 1.0))
            alpha = min(max(alpha, 1e-3), 10)
        except Exception:
            alpha = 1.0
        fam = sm.families.NegativeBinomial(alpha=alpha)
    return smf.glm(formula, data, family=fam).fit()


def coef_row(res, var, label, model, zone, n, extra=""):
    b, se, p = res.params[var], res.bse[var], res.pvalues[var]
    ci = res.conf_int().loc[var]
    return {"구역": zone, "모형": model, "변수": label, "계수(log)": round(b, 4), "표준오차": round(se, 4),
            "1단위당 변화(%)": round((np.exp(b) - 1) * 100, 1), "95%CI 하한(%)": round((np.exp(ci[0]) - 1) * 100, 1),
            "95%CI 상한(%)": round((np.exp(ci[1]) - 1) * 100, 1), "p": round(p, 4), "n(일)": n, "비고": extra}
