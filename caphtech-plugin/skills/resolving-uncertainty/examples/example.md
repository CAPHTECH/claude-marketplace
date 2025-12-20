# Example

## Decision
- Decision: MVPで「オフラインでも閲覧可能」を入れるか
- Deadline: 今週中
- Stakes: 実装コスト増 vs ユーザー価値
- Constraints: 1人/2日でMVP、iOSのみ

## Register
| ID | Category | Uncertainty | Hypothesis | I | E | U | Eff | P | Next observation |
|---:|---|---|---|---:|---:|---:|---:|---:|---|
| U-01 | Problem | ユーザーはオフライン閲覧を本当に必要としているか？ | 通勤で需要が高い | 4 | 2 | 4 | 2 | 16 | 5人インタビュー＋既存ログ確認 |
| U-02 | Tech | 2日で安全にキャッシュ実装できるか？ | 読み取り専用で限定すれば可能 | 5 | 2 | 5 | 3 | 20.8 | スパイク(2h)でPoC＋計測 |
| U-03 | Ops | キャッシュの破損/肥大化の運用が成立するか？ | サイズ上限と消去で回せる | 3 | 1 | 3 | 2 | 11.25 | 制約設計＋テスト観点洗い出し |

## Observation tasks (Top 2)
- T-01: 2時間スパイクでオフライン閲覧PoC（U-02）
- T-02: 5人の短インタビューで利用シーン確認（U-01）
