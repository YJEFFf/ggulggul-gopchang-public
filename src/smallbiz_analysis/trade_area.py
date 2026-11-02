"""미리 계산한 도로 점의 네트워크 거리에 직선 접근 거리를 더합니다."""

import numpy as np
from scipy.spatial import cKDTree


class WalkField:
    """위치 → 점포까지 도보 거리(m). 도로 네트워크 거리 + 도로에서의 직선 접근(최대 max_access_m)."""

    def __init__(self, rp, max_access_m):
        if rp.empty or max_access_m <= 0:
            raise ValueError("도로 점과 양수 접근 한도가 필요합니다.")
        if not np.isfinite(rp[["x", "y", "net_m"]].to_numpy()).all() or (rp["net_m"] < 0).any():
            raise ValueError("좌표·거리는 유한한 값이어야 하며 거리는 음수일 수 없습니다.")
        self.max_access_m = max_access_m
        self.rp = rp
        self.tree = cKDTree(rp[["x", "y"]].to_numpy())
        self.net = rp["net_m"].to_numpy()

    def __call__(self, x, y, k=12):
        x = np.atleast_1d(np.asarray(x, dtype=float))
        y = np.atleast_1d(np.asarray(y, dtype=float))
        if k < 1:
            raise ValueError("k는 1 이상이어야 합니다.")
        k = min(k, len(self.rp))
        dd, ii = self.tree.query(np.column_stack([x, y]), k=k, distance_upper_bound=self.max_access_m)
        if k == 1:
            dd, ii = dd[:, None], ii[:, None]
        valid = np.isfinite(dd)
        ii = np.where(valid, ii, 0)
        total = np.where(valid, self.net[ii] + dd, np.inf)
        return total.min(axis=1)
