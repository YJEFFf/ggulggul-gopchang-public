import unittest

import numpy as np
import pandas as pd

from smallbiz_analysis.basket import baskets_app, baskets_receipt, pairs, basket_patterns
from smallbiz_analysis.sales import food_sales, glm
from smallbiz_analysis.reviews import parse_generic, parse_naver
from smallbiz_analysis.trade_area import WalkField


class BasketTests(unittest.TestCase):
    def test_pair_support_counts_each_order_once(self):
        baskets = pd.DataFrame({"구분": ["배달"] * 4,
                                "items": [["A", "A", "B"], ["A", "B"], ["A"], ["C"]]})
        rules, singles, n = pairs(baskets, "배달", min_cnt=1)
        self.assertEqual(n, 4)
        self.assertEqual(singles["A"], 3)
        rule = rules.iloc[0]
        self.assertEqual(rule["건수"], 2)
        self.assertEqual(rule["지지도(%)"], 50.0)
        self.assertEqual(rule["신뢰도 A→B(%)"], 66.7)
        self.assertEqual(rule["신뢰도 B→A(%)"], 100.0)
        self.assertEqual(rule["향상도"], 1.33)

    def test_empty_orders_and_no_frequent_pair(self):
        for build in (baskets_app, baskets_receipt):
            self.assertTrue(build(pd.DataFrame()).empty)
        baskets = pd.DataFrame({"구분": ["배달"], "items": [["A"]]})
        rules, _, n = pairs(baskets, "배달")
        self.assertTrue(rules.empty)
        self.assertEqual(n, 1)
        self.assertTrue(pairs(baskets, "홀")[0].empty)
        self.assertTrue(basket_patterns(baskets, "홀").empty)

    def test_options_do_not_create_fake_items(self):
        rows = pd.DataFrame([
            {"채널": "DEMO", "주문번호": "DEMO-1", "메뉴_표준": "A", "메뉴분류": "메인", "수량": 1,
             "옵션": None, "수령": "배달", "월": 1, "시각": 12, "음식금액": 100},
            {"채널": "DEMO", "주문번호": "DEMO-1", "메뉴_표준": "B", "메뉴분류": "사이드", "수량": 1,
             "옵션": " + C + ", "수령": "배달", "월": 1, "시각": 12, "음식금액": 100},
        ])
        basket = baskets_app(rows).iloc[0]
        self.assertEqual(basket["items"], ["A", "B", "C"])
        self.assertEqual(basket["음식금액"], 100)


class SalesTests(unittest.TestCase):
    def test_known_amount_precedes_estimate_and_tip_only_applies_to_delivery(self):
        orders = pd.DataFrame({"음식금액": [100., np.nan, np.nan], "가게즉시할인": [10., 0., 0.],
                               "고객결제금액": [999., 120., 120.], "서비스유형": ["가게배달", "가게배달", "포장"]})
        self.assertEqual(food_sales(orders, tip=20).tolist(), [90., 100., 120.])

    def test_poisson_intercept_matches_mean_count(self):
        counts = pd.DataFrame({"n": [1, 2, 3, 2, 4, 6]})
        model = glm("n ~ 1", counts)
        self.assertAlmostEqual(np.exp(model.params["Intercept"]), counts.n.mean(), places=6)


class WalkTests(unittest.TestCase):
    def test_single_road_point_and_unreachable_location(self):
        roads = pd.DataFrame({"x": [0.], "y": [0.], "net_m": [100.]})
        distances = WalkField(roads, 20)([3., 100.], [4., 0.])
        self.assertEqual(distances[0], 105.)
        self.assertTrue(np.isinf(distances[1]))

    def test_selects_minimum_combined_distance(self):
        roads = pd.DataFrame({"x": [0., 10.], "y": [0., 0.], "net_m": [100., 0.]})
        self.assertEqual(WalkField(roads, 20)(0., 0.)[0], 10.)

    def test_invalid_roads(self):
        with self.assertRaises(ValueError):
            WalkField(pd.DataFrame(), 10)


class ReviewTests(unittest.TestCase):
    def test_nested_blocks_are_not_counted_twice(self):
        result = parse_generic('<html><body><article><blockquote><p>가상 문장</p></blockquote></article></body></html>')
        self.assertEqual(result["text"].count("가상 문장"), 1)

    def test_empty_html(self):
        self.assertEqual(parse_generic("")["text"], "")
        self.assertEqual(parse_naver("")["images"], [])

    def test_naver_synthetic_components(self):
        html = '<div class="se-main-container"><div class="se-component se-text"><p class="se-text-paragraph">가상 첫 줄<br>가상 둘째 줄</p></div></div>'
        self.assertEqual(parse_naver(html)["text"], "가상 첫 줄\n가상 둘째 줄")


if __name__ == "__main__":
    unittest.main()
