# 원본 코드와 공개본의 관계

- 원본: `YJEFFf/ggulggul-gopchang` — 별도 비공개 보관
- 기준 커밋: `bc78d2bfd332544c174ee819c3d4c08eda9852ef`
- 원본 팀: 북적북적팀
- 이 저장소는 원본 전체를 복제한 것이 아니라, 아래 함수의 구현을 추출하고 입력 의존성을 정리한 공개용 사본입니다. 새 커밋 작성자가 팀 코드 전체의 단독 저자라는 의미는 아닙니다.

| 공개 모듈 | 원본 파일·함수 |
| --- | --- |
| `sales.py` | `분석/요일비교/src/compare_sunday_tuesday.py`의 `food_sales`; `최종제출_북적북적팀/분석코드/W1_매출/w1_분석.py`의 `glm`, `coef_row` |
| `basket.py` | `최종제출_북적북적팀/분석코드/W3_배달세트/w3_분석.py`의 `norm_app`, `baskets_app`, `baskets_receipt`, `pairs`, `basket_patterns`, `two_main_combos` |
| `trade_area.py` | `분석/상권분석/src/s01_walk_network.py`의 `WalkField` |
| `reviews.py` | `분석/리뷰수집/src/r04_build.py`의 텍스트 정리 함수, `parse_naver`, `has_block_ancestor`, `parse_generic` |

공개본에서는 배달료 가정, 주 메뉴 목록, 도로 점과 접근 거리 한도를 호출자가 전달합니다. 실제 자료 경로·날짜별 보정·점포별 추정 계수·후기별 메모·실제 상권 좌표는 옮기지 않았습니다. 장바구니와 HTML의 빈 입력, 한 개 도로 점을 처리하도록 경계 조건을 보완했습니다.

패키지 구성, 합성 예제와 단위 테스트는 공개용 정리 과정에서 추가했습니다. 원본 Git 이력과 원본 데이터·결과물은 포함하지 않습니다.
