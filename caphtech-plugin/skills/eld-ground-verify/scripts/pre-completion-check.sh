#!/bin/bash
# ELD Pre-Completion Check Script
# PR作成前の完成前検証を自動実行

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Exit codes
EXIT_SUCCESS=0
EXIT_FAILURE=1

# Global variables
ERRORS=0
WARNINGS=0

# Helper functions
error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
    ((ERRORS++))
}

warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
    ((WARNINGS++))
}

success() {
    echo -e "${GREEN}✓ $1${NC}"
}

info() {
    echo "ℹ $1"
}

# ============================================================================
# Phase 1: Evidence Pack Completeness
# ============================================================================

check_evidence_pack() {
    echo "=== Phase 1: Evidence Pack Completeness ==="
    echo

    # Check 1: 因果マップの完全性
    info "Checking causal map..."

    if [ ! -f "evidence-pack/causal-map.md" ]; then
        error "Causal map not found: evidence-pack/causal-map.md"
    else
        # Check if causal map has required sections
        if ! grep -q "## 変更の因果関係" evidence-pack/causal-map.md; then
            error "Causal map missing section: 変更の因果関係"
        fi

        if ! grep -q "## 影響範囲グラフ" evidence-pack/causal-map.md; then
            error "Causal map missing section: 影響範囲グラフ"
        fi

        if ! grep -q "## データフロー" evidence-pack/causal-map.md; then
            warning "Causal map missing section: データフロー (optional)"
        fi

        if [ $ERRORS -eq 0 ]; then
            success "Causal map is complete"
        fi
    fi
    echo

    # Check 2: 証拠の完全性
    info "Checking evidence..."

    if [ ! -d "evidence-pack/evidence" ]; then
        error "Evidence directory not found: evidence-pack/evidence/"
    else
        # Check if test results exist
        if [ ! -f "evidence-pack/evidence/test-results.txt" ]; then
            warning "Test results not found: evidence-pack/evidence/test-results.txt"
        else
            # Check test pass rate
            TOTAL_TESTS=$(grep -c "test" evidence-pack/evidence/test-results.txt || echo 0)
            PASSED_TESTS=$(grep -c "✓" evidence-pack/evidence/test-results.txt || echo 0)

            if [ $TOTAL_TESTS -gt 0 ]; then
                PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
                if [ $PASS_RATE -lt 100 ]; then
                    error "Test pass rate is ${PASS_RATE}% (expected 100%)"
                else
                    success "All tests passed (${PASSED_TESTS}/${TOTAL_TESTS})"
                fi
            fi
        fi

        # Check if telemetry config exists
        if [ ! -f "evidence-pack/evidence/telemetry-config.yaml" ]; then
            warning "Telemetry config not found (optional for S2 Laws)"
        else
            success "Telemetry config found"
        fi
    fi
    echo

    # Check 3: 影響範囲グラフの完全性
    info "Checking impact graph..."

    if [ ! -f "evidence-pack/impact-graph.yaml" ]; then
        error "Impact graph not found: evidence-pack/impact-graph.yaml"
    else
        # Check if impact graph has required fields
        if ! grep -q "changed_files:" evidence-pack/impact-graph.yaml; then
            error "Impact graph missing field: changed_files"
        fi

        if ! grep -q "dependencies:" evidence-pack/impact-graph.yaml; then
            error "Impact graph missing field: dependencies"
        fi

        if ! grep -q "ripple_effect:" evidence-pack/impact-graph.yaml; then
            warning "Impact graph missing field: ripple_effect (optional)"
        fi

        if [ $ERRORS -eq 0 ]; then
            success "Impact graph is complete"
        fi
    fi
    echo
}

# ============================================================================
# Phase 2: Law/Term Orphan Detection
# ============================================================================

check_orphan() {
    echo "=== Phase 2: Law/Term Orphan Detection ==="
    echo

    # Check if link-map exists
    if [ ! -f "link-map.yaml" ]; then
        error "Link map not found: link-map.yaml"
        echo
        return
    fi

    # Check Law orphans
    info "Checking Law orphans..."

    if [ -d "law-catalog" ]; then
        LAW_ORPHANS=0

        for law_file in law-catalog/*.yaml; do
            if [ -f "$law_file" ]; then
                LAW_ID=$(basename "$law_file" .yaml)

                if ! grep -q "law: $LAW_ID" link-map.yaml; then
                    warning "Orphan Law detected: $LAW_ID"
                    ((LAW_ORPHANS++))
                fi
            fi
        done

        if [ $LAW_ORPHANS -eq 0 ]; then
            success "No Law orphans detected"
        else
            warning "Found $LAW_ORPHANS orphan Law(s)"
        fi
    else
        warning "Law catalog directory not found"
    fi
    echo

    # Check Term orphans
    info "Checking Term orphans..."

    if [ -d "term-catalog" ]; then
        TERM_ORPHANS=0

        for term_file in term-catalog/*.yaml; do
            if [ -f "$term_file" ]; then
                TERM_ID=$(basename "$term_file" .yaml)

                if ! grep -q "term: $TERM_ID" link-map.yaml; then
                    warning "Orphan Term detected: $TERM_ID"
                    ((TERM_ORPHANS++))
                fi
            fi
        done

        if [ $TERM_ORPHANS -eq 0 ]; then
            success "No Term orphans detected"
        else
            warning "Found $TERM_ORPHANS orphan Term(s)"
        fi
    else
        warning "Term catalog directory not found"
    fi
    echo
}

# ============================================================================
# Phase 3: Evidence Ladder Achievement
# ============================================================================

check_evidence_ladder() {
    echo "=== Phase 3: Evidence Ladder Achievement ==="
    echo

    # Check if grounding-map exists
    if [ ! -f "grounding-map.yaml" ]; then
        error "Grounding map not found: grounding-map.yaml"
        echo
        return
    fi

    info "Checking S0 Laws..."

    # Extract S0 Laws from grounding-map
    S0_LAWS=$(grep -A1 "severity: S0" grounding-map.yaml | grep "law:" | sed 's/.*law: //' || echo "")

    if [ -n "$S0_LAWS" ]; then
        S0_INCOMPLETE=0

        while IFS= read -r law; do
            # Check if Law has L1, L2, L4
            LEVELS=$(grep -A10 "law: $law" grounding-map.yaml | grep "level:" | sed 's/.*level: //')

            HAS_L1=false
            HAS_L2=false
            HAS_L4=false

            while IFS= read -r level; do
                case $level in
                    L1) HAS_L1=true ;;
                    L2) HAS_L2=true ;;
                    L4) HAS_L4=true ;;
                esac
            done <<< "$LEVELS"

            if [ "$HAS_L1" = false ] || [ "$HAS_L2" = false ] || [ "$HAS_L4" = false ]; then
                error "S0 Law $law missing Evidence: L1=$HAS_L1, L2=$HAS_L2, L4=$HAS_L4"
                ((S0_INCOMPLETE++))
            else
                success "S0 Law $law: L1/L2/L4 complete"
            fi
        done <<< "$S0_LAWS"

        if [ $S0_INCOMPLETE -eq 0 ]; then
            success "All S0 Laws have complete Evidence"
        fi
    else
        info "No S0 Laws found"
    fi
    echo

    info "Checking S1 Laws..."

    # Extract S1 Laws from grounding-map
    S1_LAWS=$(grep -A1 "severity: S1" grounding-map.yaml | grep "law:" | sed 's/.*law: //' || echo "")

    if [ -n "$S1_LAWS" ]; then
        S1_INCOMPLETE=0

        while IFS= read -r law; do
            # Check if Law has L1
            LEVELS=$(grep -A10 "law: $law" grounding-map.yaml | grep "level:" | sed 's/.*level: //')

            HAS_L1=false

            while IFS= read -r level; do
                if [ "$level" = "L1" ]; then
                    HAS_L1=true
                fi
            done <<< "$LEVELS"

            if [ "$HAS_L1" = false ]; then
                error "S1 Law $law missing Evidence L1"
                ((S1_INCOMPLETE++))
            else
                success "S1 Law $law: L1 complete"
            fi
        done <<< "$S1_LAWS"

        if [ $S1_INCOMPLETE -eq 0 ]; then
            success "All S1 Laws have L1 Evidence"
        fi
    else
        info "No S1 Laws found"
    fi
    echo
}

# ============================================================================
# Phase 4: Stop Conditions Check
# ============================================================================

check_stop_conditions() {
    echo "=== Phase 4: Stop Conditions Check ==="
    echo

    # Check if issue-contract exists
    if [ ! -f "issue-contract.yaml" ]; then
        warning "Issue contract not found: issue-contract.yaml"
        echo
        return
    fi

    # Check test failure count
    info "Checking test failure history..."

    if [ -f ".test-failure-count" ]; then
        FAILURE_COUNT=$(cat .test-failure-count)

        if [ $FAILURE_COUNT -ge 3 ]; then
            error "Test failure count is $FAILURE_COUNT (threshold: 3)"
        else
            success "Test failure count is $FAILURE_COUNT (OK)"
        fi
    else
        info "No test failure history found (assuming 0)"
    fi
    echo

    # Check unobservable changes
    info "Checking for unobservable changes..."

    UNOBSERVABLE=0

    # Get list of changed files
    if [ -f "evidence-pack/changed-files.txt" ]; then
        while IFS= read -r file; do
            # Check if file has corresponding test
            if [ ! -f "tests/${file%.ts}.test.ts" ] && [ ! -f "tests/${file%.js}.test.js" ]; then
                warning "No test found for: $file"
                ((UNOBSERVABLE++))
            fi
        done < evidence-pack/changed-files.txt

        if [ $UNOBSERVABLE -eq 0 ]; then
            success "All changes have corresponding tests"
        else
            error "Found $UNOBSERVABLE unobservable change(s)"
        fi
    else
        warning "Changed files list not found"
    fi
    echo

    # Check rollback capability
    info "Checking rollback capability..."

    if [ -f "evidence-pack/irreversible-changes.txt" ]; then
        IRREVERSIBLE_COUNT=$(wc -l < evidence-pack/irreversible-changes.txt)

        if [ $IRREVERSIBLE_COUNT -gt 0 ]; then
            error "Found $IRREVERSIBLE_COUNT irreversible change(s)"
        else
            success "All changes are reversible"
        fi
    else
        success "No irreversible changes detected"
    fi
    echo
}

# ============================================================================
# Phase 5: Completion Decision
# ============================================================================

completion_decision() {
    echo "=== Phase 5: Completion Decision ==="
    echo

    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓ PR READY${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        success "All completion criteria are met"

        if [ $WARNINGS -gt 0 ]; then
            warning "Found $WARNINGS warning(s) - review recommended"
        fi

        echo
        echo "You can now create a PR."
        return $EXIT_SUCCESS
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}✗ PR NOT READY${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo
        error "Found $ERRORS error(s) that must be fixed"

        if [ $WARNINGS -gt 0 ]; then
            warning "Also found $WARNINGS warning(s)"
        fi

        echo
        echo "Please fix the errors above before creating a PR."
        return $EXIT_FAILURE
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    echo
    echo "╔═══════════════════════════════════════════╗"
    echo "║  ELD Pre-Completion Verification         ║"
    echo "╚═══════════════════════════════════════════╝"
    echo

    check_evidence_pack
    check_orphan
    check_evidence_ladder
    check_stop_conditions
    completion_decision

    return $?
}

# Run main
main
exit $?
