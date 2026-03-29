# 📊 Macro Index Tracker

Bloomberg-style macro dashboard. Fetches daily closing prices automatically via GitHub Actions and stores them in `data/prices.json`.

## 파일 구조

```
macro-tracker/
├── index.html                    ← 대시보드 웹페이지
├── data/
│   └── prices.json               ← 모든 가격 데이터 (자동 누적)
├── scripts/
│   ├── fetch_prices.py           ← 가격 fetch 스크립트
│   └── backfill.py               ← 과거 데이터 채우기
└── .github/
    └── workflows/
        └── fetch.yml             ← 매일 자동 실행
```

## 초기 설정 (처음 한 번만)

### 1단계 — 과거 데이터 백필 (로컬에서 실행)

```bash
# Python 3.12+ 필요
python scripts/backfill.py 2026-01-01    # 2026년 1월부터 오늘까지
```

완료 후 `data/prices.json`을 커밋:

```bash
git add data/prices.json
git commit -m "data: backfill 2026-01 to present"
git push
```

### 2단계 — GitHub Pages 활성화

1. GitHub repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / folder: `/ (root)`
4. Save → 1~2분 후 `https://[username].github.io/macro-tracker/` 접속 확인

### 3단계 — Actions 권한 확인

1. GitHub repo → **Settings** → **Actions** → **General**
2. **Workflow permissions** → **Read and write permissions** 선택
3. Save

이제 매일 오후 6시(KST)에 자동으로 가격을 fetch합니다.

## 수동 실행 / 특정 날짜 백필

GitHub repo → **Actions** → **Daily Price Fetch** → **Run workflow**

- `date` 필드: `2026-02-14` (비우면 오늘)
- `force`: 이미 있는 데이터 덮어쓰기

## Notion 임베드

```
/embed → https://[username].github.io/macro-tracker/
```

## 추적 지수 목록

| ID | 지수 | 마켓 |
|---|---|---|
| DJI | Dow Jones | DM |
| SPX | S&P 500 | DM |
| FTSE | FTSE 100 | DM |
| STOXX | Euro Stoxx 50 | DM |
| N225 | Nikkei 225 | DM |
| HSI | Hang Seng | DM |
| KS11 | KOSPI | EM |
| BVSP | Bovespa | EM |
| XU100 | BIST 100 | EM |
| NSEI | Nifty 50 | EM |
| SET | SET | EM |
| TWII | Taiwan Weighted | EM |
| TA35 | TA-35 | EM |
| GC | Gold Futures | CMD |
| CL | Crude Oil | CMD |
