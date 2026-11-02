# 소상공인 매출·상권·리뷰 분석

**2026 AI·빅데이터 기반 소상공인 매출 증대 프로젝트 · 북적북적팀**

꿀꿀곱창의 매출·주문 구성·상권·리뷰를 분석해 운영과 홍보 개선안을 만든 프로젝트입니다. 이 저장소는 실제 프로젝트의 분석 함수 중 공개 가능한 부분을 분리하고, 합성 데이터로 실행할 수 있게 정리한 코드 사본입니다.

| 모듈 | 포함한 구현 |
| --- | --- |
| `sales.py` | 음식 매출 금액 정리, Poisson·Negative Binomial GLM, 계수·신뢰구간 요약 |
| `basket.py` | 주문·전표별 장바구니 구성, 품목 쌍의 지지도·신뢰도·향상도, 주문 패턴 집계 |
| `trade_area.py` | 도로 네트워크 거리와 접근 거리를 결합한 도보 거리 추정 |
| `reviews.py` | 로컬 HTML의 본문·제목·이미지 참조 구조 파싱 |

## 실행

Python 3.11 이상이 필요합니다.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/run_demo.py
```

예제는 가상 메뉴·주문·좌표·HTML을 코드에서 생성하고 `demo_output/summary.json`에 결과를 저장합니다. **입력과 결과는 모두 합성 예제이며, 실제 점포의 수치나 분석 결론을 재현하지 않습니다.** 모델 예제도 합성 자료로 새로 학습합니다.

## 공개 범위

실제 매출·정산·주문 자료, 고객·리뷰어 정보, 리뷰 원문과 사진, 로그인 상태가 담긴 응답, 발표·제출 보고서 및 실제 정산 추정 계수는 포함하지 않습니다. 수집·로그인 코드를 제외했으며, 리뷰 파서는 제공된 로컬 HTML만 처리합니다.

원본 전체와 실제 데이터는 **별도 비공개 저장소**에서 보관합니다. 원본 함수와 공개본의 변경 내용은 [PROVENANCE.md](PROVENANCE.md), 입력 형식과 해석상 제약은 [docs/INPUTS.md](docs/INPUTS.md)에 정리했습니다.
