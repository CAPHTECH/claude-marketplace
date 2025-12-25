# Scorer Design Guide

LLM生成システムの品質を多面的に評価するスコアラー設計ガイド。

## スコアラーの基本原則

```
1. 単一責務: 各スコアラーは1つの品質側面のみを測定
2. 独立性: スコアラー間は独立して実行可能
3. 透明性: スコア計算の根拠が明確
4. 拡張性: 新しいスコアラーの追加が容易
```

---

## 標準スコアラー

### 1. Operation Accuracy（操作正確性）

**測定対象**: 期待される操作と実際の操作の一致度

```typescript
score = matchedOperations / totalExpectedOperations

// マッチング条件:
// - 操作種別 (type) が一致
// - ターゲットブロックID が一致
// - insert操作の場合、position も一致
```

**閾値**: 80%

**詳細情報**:
```typescript
{
  matchedOperations: number,
  totalExpectedOperations: number,
  unmatchedOperations: [
    {
      expected: Operation,
      reason: "type mismatch" | "target mismatch" | "position mismatch"
    }
  ]
}
```

---

### 2. Target Block Precision（ターゲット精度）

**測定対象**: 正しいターゲットブロックを特定できた割合

```typescript
score = correctTargets / totalTargets

// 正解条件:
// - targetBlockId が一致 OR
// - targetIndex が一致
```

**閾値**: 75%

**詳細情報**:
```typescript
{
  correctTargets: number,
  totalTargets: number,
  incorrectTargets: [
    {
      expected: { targetBlockId, targetIndex },
      actual: { targetBlockId, targetIndex }
    }
  ]
}
```

---

### 3. Content Quality（コンテンツ品質）

**測定対象**: 生成されたコンテンツが期待パターンにマッチする割合

```typescript
score = matchedPatterns / totalPatterns

// マッチング:
// - 正規表現パターンで検証
// - 大文字小文字非区別オプション
```

**閾値**: 60%

**詳細情報**:
```typescript
{
  matchedPatterns: number,
  totalPatterns: number,
  contentIssues: [
    "Page 'X': Pattern 'Y' not found in content: 'Z...'"
  ]
}
```

**パターン設計のベストプラクティス**:
```yaml
# ✓ Good: 複数選択肢
- "要約|まとめ|サマリー"

# ✓ Good: 部分一致
- ".*置換後.*"

# ✓ Good: 複数マッチの確認
- "Cart.*Cart.*Cart"

# ✗ Bad: 完全一致のみ
- "^完全に一致するテキスト$"
```

---

### 4. Operation Result（操作結果）

**測定対象**: 操作適用の成功率と最終結果の品質

```typescript
score = (applicationSuccessRate * 0.6) + (contentScore * 0.4)

// applicationSuccessRate: 操作が実際に適用可能か
// contentScore: 最終コンテンツの品質
```

**閾値**: 80%

---

### 5. Anti-Hallucination（幻覚防止）[カスタム]

**測定対象**: 入力に存在しない情報が追加されていないか

```typescript
score = (noNewContent && noDeletedBlocks && onlySpecifiedChanges) ? 1 : 0

// チェック項目:
// - 新規コンテンツの追加がない
// - 既存ブロックの削除がない
// - 指定された変更のみ行われている
```

**閾値**: 100%（幻覚は0でなければならない）

**実装例**:
```typescript
function scoreAntiHallucination(
  actual: BulkEditWorkflowOutput,
  expected: ExpectedBulkEditOutput,
  originalBlocks: Block[]
): number {
  // 1. 新規ブロックの追加チェック
  const actualBlockIds = new Set(extractAllBlockIds(actual));
  const originalBlockIds = new Set(extractAllBlockIds(originalBlocks));
  const newBlocks = [...actualBlockIds].filter(id => !originalBlockIds.has(id));

  if (newBlocks.length > 0) return 0;

  // 2. 予期しない削除のチェック
  const expectedDeleteIds = extractDeleteTargets(expected);
  for (const originalId of originalBlockIds) {
    if (!actualBlockIds.has(originalId) && !expectedDeleteIds.has(originalId)) {
      return 0;
    }
  }

  // 3. 内容の比較（期待された変更以外がないか）
  // ...

  return 1;
}
```

---

## スコアラー組み合わせパターン

### パターン1: 標準評価

```yaml
scorers:
  - type: operation-accuracy
    weight: 1.0
    threshold: 0.8
  - type: target-block-precision
    weight: 1.0
    threshold: 0.75
  - type: content-quality
    weight: 1.0
    threshold: 0.6
```

### パターン2: 厳密評価

```yaml
scorers:
  - type: operation-accuracy
    weight: 1.0
    threshold: 0.9
  - type: target-block-precision
    weight: 1.0
    threshold: 0.9
  - type: content-quality
    weight: 1.0
    threshold: 0.8
  - type: anti-hallucination
    weight: 2.0  # 重み付け増加
    threshold: 1.0
```

### パターン3: 操作重視

```yaml
scorers:
  - type: operation-accuracy
    weight: 2.0  # 重み付け増加
    threshold: 0.9
  - type: target-block-precision
    weight: 1.5
    threshold: 0.85
  - type: content-quality
    weight: 0.5  # 重み付け減少
    threshold: 0.5
```

---

## カスタムスコアラーの実装

```typescript
// インターフェース
interface Scorer<TActual, TExpected> {
  // スコア計算（0-1）
  score(actual: TActual, expected: TExpected): number;

  // 詳細情報（デバッグ用）
  getDetails(actual: TActual, expected: TExpected): ScorerDetails;
}

// 実装例: レスポンス時間スコアラー
class ResponseTimeScorer implements Scorer<WorkflowResult, ExpectedResult> {
  constructor(private maxAcceptableMs: number) {}

  score(actual: WorkflowResult, expected: ExpectedResult): number {
    const responseTimeMs = actual.durationMs;
    if (responseTimeMs <= this.maxAcceptableMs) {
      return 1;
    }
    // 段階的に減点
    return Math.max(0, 1 - (responseTimeMs - this.maxAcceptableMs) / this.maxAcceptableMs);
  }

  getDetails(actual: WorkflowResult, expected: ExpectedResult): ScorerDetails {
    return {
      responseTimeMs: actual.durationMs,
      maxAcceptableMs: this.maxAcceptableMs,
      passed: actual.durationMs <= this.maxAcceptableMs
    };
  }
}
```

---

## 合格判定ロジック

```typescript
// AND条件: すべてのスコアラーが閾値以上
function isPassed(scores: ScorerResult[]): boolean {
  return scores.every(s => s.score >= s.threshold);
}

// 重み付き平均
function weightedAverage(scores: ScorerResult[]): number {
  const totalWeight = scores.reduce((sum, s) => sum + s.weight, 0);
  const weightedSum = scores.reduce((sum, s) => sum + s.score * s.weight, 0);
  return weightedSum / totalWeight;
}
```

---

## デバッグ戦略

```yaml
# スコアが低い場合の分析フロー
diagnosis:
  operation_accuracy_low:
    - check: unmatchedOperations
    - analyze: 操作種別、ターゲット、位置のどれが不一致か

  target_precision_low:
    - check: incorrectTargets
    - analyze: LLMがターゲットを特定できていない理由

  content_quality_low:
    - check: contentIssues
    - analyze: パターンが厳しすぎないか、正規表現が有効か

  anti_hallucination_failed:
    - check: 入出力の差分
    - analyze: どのような内容が追加/削除されたか
```
