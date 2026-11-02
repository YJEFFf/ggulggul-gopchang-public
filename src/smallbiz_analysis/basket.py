"""주문별 품목 표준화, 동시 구매 지지도·신뢰도·향상도 계산."""

from itertools import combinations
import numpy as np
import pandas as pd


def norm_app(row):
    name = str(row["메뉴_표준"])
    cls = row["메뉴분류"]
    if cls == "음료":
        return "음료"
    if cls == "주류":
        return "주류"
    if cls == "점심특선":
        return "점심특선"
    return {"당면추가": "당면", "중화면 추가": "중화면"}.get(name, name)


def baskets_app(it):
    if it.empty:
        return pd.DataFrame(columns=["채널", "주문번호", "수령", "월", "시각", "음식금액", "items", "메인수", "구분"])
    rows = []
    for (ch, no), g in it.groupby(["채널", "주문번호"]):
        items = []
        for _, x in g.iterrows():
            q = int(x["수량"]) if pd.notna(x["수량"]) else 1
            items += [norm_app(x)] * max(q, 1)
            opt = str(x["옵션"])
            if pd.notna(x["옵션"]) and opt.strip():
                for p in opt.split("+"):
                    if p.strip():
                        items.append({"당면추가": "당면"}.get(p.strip(), p.strip()))
        rows.append({"채널": ch, "주문번호": no, "수령": g["수령"].iloc[0], "월": g["월"].iloc[0], "시각": g["시각"].iloc[0],
                     "음식금액": g["음식금액"].iloc[0], "items": items,
                     "메인수": int(g.loc[g["메뉴분류"] == "메인", "수량"].sum())})  # f01.a5_menu 정의
    b = pd.DataFrame(rows)
    b["구분"] = np.where(b["수령"] == "포장", "앱 포장", "배달")
    return b


def baskets_receipt(r):
    if r.empty:
        return pd.DataFrame(columns=["영업일자", "전표번호", "월", "채널", "items", "음식금액", "메인수", "구분"])
    r = r.copy()
    r["수량"] = pd.to_numeric(r["수량"], errors="coerce").fillna(1).astype(int)
    r["월"] = r["영업일자"].dt.month

    def nm(x):
        if x["구분"] == "음료":
            return "음료"
        if x["구분"] == "주류":
            return "주류"
        n = str(x["상품명"])
        return "점심특선" if n.startswith("[점심특선]") else n

    rows = []
    for (d, no), g in r.groupby(["영업일자", "전표번호"]):
        items = []
        for _, x in g.iterrows():
            items += [nm(x)] * max(x["수량"], 1)
        food = int(g.loc[g["구분"] != "주류", "금액"].sum())
        rows.append({"영업일자": d, "전표번호": no, "월": g["월"].iloc[0], "채널": g["채널"].iloc[0], "items": items,
                     "음식금액": food, "메인수": int(g.loc[g["구분"] == "안주", "수량"].sum())})  # 전표요약 '안주수량'(점심특선 포함)과 같은 정의
    b = pd.DataFrame(rows)
    b["구분"] = np.where(b["채널"] == "매장", "홀", "직접 포장")
    return b


def pairs(B, ch, min_cnt=3):
    x = B[B["구분"] == ch]
    n = len(x)
    single = {}
    pair = {}
    for s in x["items"]:
        u = sorted(set(s))
        for i in u:
            single[i] = single.get(i, 0) + 1
        for a, b in combinations(u, 2):
            pair[(a, b)] = pair.get((a, b), 0) + 1
    rows = []
    for (a, b), c in pair.items():
        if c < min_cnt:
            continue
        rows.append({"채널": ch, "품목A": a, "품목B": b, "건수": c, "지지도(%)": round(c / n * 100, 1),
                     "신뢰도 A→B(%)": round(c / single[a] * 100, 1), "신뢰도 B→A(%)": round(c / single[b] * 100, 1),
                     "향상도": round((c / n) / ((single[a] / n) * (single[b] / n)), 2), "주문수": n})
    columns = ["채널", "품목A", "품목B", "건수", "지지도(%)", "신뢰도 A→B(%)", "신뢰도 B→A(%)", "향상도", "주문수"]
    df = pd.DataFrame(rows, columns=columns).sort_values(["건수", "향상도"], ascending=False)
    return df, single, n


def basket_patterns(B, ch, main_items=(), top=10):
    x = B[B["구분"] == ch]
    pat = x["items"].apply(lambda s: " + ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(pd.Series(s).value_counts().items(), key=lambda kv: (kv[0] not in main_items, kv[0]))))
    vc = pat.value_counts().head(top)
    return pd.DataFrame({"채널": ch, "장바구니": vc.index, "건수": vc.values, "비중(%)": (vc.values / len(x) * 100).round(1)})


def two_main_combos(B, ch, main_items=()):
    x = B[(B["구분"] == ch) & (B["메인수"] == 2)]
    pat = x["items"].apply(lambda s: " + ".join(sorted(i for i in s if i in main_items)))
    vc = pat.value_counts()
    return pd.DataFrame({"채널": ch, "메인2개_조합": vc.index, "건수": vc.values, "메인2개주문중(%)": (vc.values / len(x) * 100).round(1)})
