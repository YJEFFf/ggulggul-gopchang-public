"""실제 점포 자료를 사용하지 않는 합성 실행 예제."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from smallbiz_analysis.basket import baskets_app, pairs, basket_patterns
from smallbiz_analysis.sales import food_sales, glm, coef_row
from smallbiz_analysis.reviews import parse_generic
from smallbiz_analysis.trade_area import WalkField


def run():
    rng = np.random.default_rng(2026)
    rows = []
    for i in range(60):
        menu = ["가상메뉴A"] if i % 3 else ["가상메뉴B"]
        if i % 2 == 0:
            menu.append("가상사이드")
        for item in menu:
            rows.append({"채널": "DEMO", "주문번호": f"DEMO-{i:03d}",
                         "메뉴_표준": item, "메뉴분류": "사이드" if item == "가상사이드" else "메인",
                         "수량": 1, "옵션": None, "수령": "배달", "월": 1,
                         "시각": 12 + i % 8, "음식금액": 10000 + 2000 * (len(menu) - 1)})
    baskets = baskets_app(pd.DataFrame(rows))
    rules, _, n = pairs(baskets, "배달")
    amounts = pd.DataFrame({"음식금액": [10000, np.nan], "가게즉시할인": [500, 0],
                            "고객결제금액": [11500, 13000], "서비스유형": ["가게배달", "가게배달"]})
    x = rng.normal(size=180)
    counts = rng.poisson(np.exp(1.4 + 0.2 * x))
    model = glm("orders ~ feature", pd.DataFrame({"orders": counts, "feature": x}))
    roads = pd.DataFrame({"x": [0., 100., 200.], "y": [0., 0., 0.], "net_m": [0., 100., 200.]})
    distance = WalkField(roads, max_access_m=50)([10., 110.], [0., 10.])
    html = '<html><head><title>가상 후기</title></head><body><article><p>파서 실행용으로 직접 작성한 문장입니다.</p></article></body></html>'
    result = {
        "notice": "모든 입력과 결과는 합성 예제입니다. 실제 점포 수치가 아닙니다.",
        "synthetic_order_count": n,
        "synthetic_food_sales": food_sales(amounts, tip=2000).tolist(),
        "association_rules": rules.to_dict(orient="records"),
        "basket_patterns": basket_patterns(baskets, "배달", main_items=["가상메뉴A", "가상메뉴B"]).to_dict(orient="records"),
        "synthetic_model": coef_row(model, "feature", "합성 변수", "Poisson", "가상구역", len(x)),
        "synthetic_walk_distance_m": distance.tolist(),
        "synthetic_html": parse_generic(html),
    }
    dest = Path("demo_output/summary.json")
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(result["notice"])
    print(f"합성 주문 {n}건 분석 완료: {dest}")


if __name__ == "__main__":
    run()
