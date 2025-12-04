"""Tests for action title generator."""

import pytest


class TestIsWeakTitle:
    """Tests for weak title detection."""

    def test_detects_overview_title(self):
        """Should detect 'overview' as weak."""
        from core.action_titles import is_weak_title

        assert is_weak_title("Revenue Overview")
        assert is_weak_title("Overview of Q3 Sales")

    def test_detects_analysis_title(self):
        """Should detect 'analysis' as weak."""
        from core.action_titles import is_weak_title

        assert is_weak_title("Regional Revenue Analysis")
        assert is_weak_title("Analysis of Customer Data")

    def test_detects_summary_title(self):
        """Should detect 'summary' as weak."""
        from core.action_titles import is_weak_title

        assert is_weak_title("Summary of Findings")
        assert is_weak_title("Q3 Summary")

    def test_detects_report_title(self):
        """Should detect 'report' as weak."""
        from core.action_titles import is_weak_title

        assert is_weak_title("Report on Sales Performance")
        assert is_weak_title("Data Report")

    def test_accepts_action_title(self):
        """Should accept action-oriented titles."""
        from core.action_titles import is_weak_title

        assert not is_weak_title("Northeast Drives 60% of Growth")
        assert not is_weak_title("Revenue Grows 25% Year-over-Year")
        assert not is_weak_title("Product A Outperforms Competition")

    def test_accepts_specific_title(self):
        """Should accept titles with specific numbers."""
        from core.action_titles import is_weak_title

        assert not is_weak_title("Northeast: 45% Market Share")
        assert not is_weak_title("$2.5M Revenue Gap")

    def test_accepts_title_with_captures(self):
        """Should accept title with 'captures'."""
        from core.action_titles import is_weak_title

        assert not is_weak_title("North Region Captures 50% Market Share")


class TestTransformToActionTitle:
    """Tests for title transformation."""

    def test_transform_with_metric_and_value(self):
        """Should create action title from metric and value."""
        from core.action_titles import transform_to_action_title

        result = transform_to_action_title(
            "Regional Analysis",
            key_metric="Revenue",
            key_value="Northeast 45%",
            trend="up"
        )

        assert "Northeast" in result
        assert "45%" in result
        assert "Revenue" in result

    def test_transform_with_trend_up(self):
        """Should use growth verb for upward trend."""
        from core.action_titles import transform_to_action_title

        result = transform_to_action_title(
            "Q3 Sales",
            key_metric="Sales",
            key_value="25%",
            trend="up"
        )

        assert "Grows" in result or "Drives" in result

    def test_transform_with_trend_down(self):
        """Should use decline verb for downward trend."""
        from core.action_titles import transform_to_action_title

        result = transform_to_action_title(
            "Cost Analysis",
            key_metric="Costs",
            key_value="15%",
            trend="down"
        )

        assert "Declines" in result or "Loses" in result

    def test_transform_removes_weak_words(self):
        """Should remove weak words when no data provided."""
        from core.action_titles import transform_to_action_title

        result = transform_to_action_title("Overview of Regional Sales")

        assert "Overview" not in result
        assert "Regional Sales" in result or "Regional" in result

    def test_transform_with_dollar_value(self):
        """Should handle dollar values."""
        from core.action_titles import transform_to_action_title

        result = transform_to_action_title(
            "Revenue Analysis",
            key_metric="Revenue",
            key_value="North $2.5M",
            trend="up"
        )

        assert "North" in result
        assert "$2.5M" in result

    def test_transform_neutral_trend(self):
        """Should use neutral verb when no trend."""
        from core.action_titles import transform_to_action_title

        result = transform_to_action_title(
            "Market Analysis",
            key_metric="Market",
            key_value="East 30%"
        )

        assert "Captures" in result or "Reaches" in result


class TestSuggestActionTitles:
    """Tests for title suggestions."""

    def test_suggests_from_values(self):
        """Should suggest titles based on values."""
        from core.action_titles import suggest_action_titles

        suggestions = suggest_action_titles(
            "regional revenue",
            {"North": 100, "South": 60, "East": 40}
        )

        assert len(suggestions) >= 3
        assert any("North" in s for s in suggestions)
        assert any("50%" in s for s in suggestions)  # 100/200 = 50%

    def test_provides_fallback(self):
        """Should provide generic suggestions when no data."""
        from core.action_titles import suggest_action_titles

        suggestions = suggest_action_titles("analysis", {})

        assert len(suggestions) > 0

    def test_suggests_comparison_title(self):
        """Should suggest comparison title when runner-up exists."""
        from core.action_titles import suggest_action_titles

        suggestions = suggest_action_titles(
            "sales comparison",
            {"A": 100, "B": 70, "C": 30}
        )

        # Should include an "Outperforms" suggestion
        assert any("Outperforms" in s for s in suggestions)

    def test_handles_non_numeric_values(self):
        """Should handle dict with non-numeric values."""
        from core.action_titles import suggest_action_titles

        suggestions = suggest_action_titles(
            "data",
            {"A": "high", "B": "low"}
        )

        # Should provide fallback suggestions
        assert len(suggestions) > 0


class TestValidateActionTitle:
    """Tests for title validation."""

    def test_validates_good_title(self):
        """Should validate good action title."""
        from core.action_titles import validate_action_title

        result = validate_action_title("Northeast Drives 60% of Revenue Growth")

        assert result['valid'] is True

    def test_rejects_weak_title(self):
        """Should reject weak title."""
        from core.action_titles import validate_action_title

        result = validate_action_title("Revenue Overview")

        assert result['valid'] is False
        assert 'action-oriented' in result['feedback'].lower() or 'descriptive' in result['feedback'].lower()

    def test_rejects_long_title(self):
        """Should reject overly long title."""
        from core.action_titles import validate_action_title

        long_title = "A" * 100
        result = validate_action_title(long_title)

        assert result['valid'] is False
        assert 'long' in result['feedback'].lower()

    def test_rejects_question_title(self):
        """Should reject question as title."""
        from core.action_titles import validate_action_title

        result = validate_action_title("What Drives Regional Growth?")

        assert result['valid'] is False
        assert 'question' in result['feedback'].lower()

    def test_rejects_short_title(self):
        """Should reject too short title."""
        from core.action_titles import validate_action_title

        result = validate_action_title("Sales")

        assert result['valid'] is False
        assert 'short' in result['feedback'].lower()

    def test_provides_suggestions_for_weak(self):
        """Should provide suggestions for weak titles."""
        from core.action_titles import validate_action_title

        result = validate_action_title("Data Overview")

        assert result['valid'] is False
        assert len(result['suggestions']) > 0

    def test_good_title_has_positive_feedback(self):
        """Should have positive feedback for good titles."""
        from core.action_titles import validate_action_title

        result = validate_action_title("Sales Grow 25% Year-over-Year")

        assert result['valid'] is True
        assert 'action-oriented' in result['feedback'].lower()
