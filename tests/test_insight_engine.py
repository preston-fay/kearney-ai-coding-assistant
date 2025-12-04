"""Tests for insight engine."""

import pytest
from pathlib import Path


class TestEvidence:
    """Tests for Evidence dataclass."""

    def test_evidence_creation(self):
        """Should create evidence with all fields."""
        from core.insight_engine import Evidence

        e = Evidence(
            type="metric",
            reference="revenue_total",
            value=1000000,
            label="Total Revenue"
        )

        assert e.type == "metric"
        assert e.value == 1000000

    def test_evidence_to_dict(self):
        """Should serialize to dict."""
        from core.insight_engine import Evidence

        e = Evidence(type="chart", reference="chart.png", value=None)
        d = e.to_dict()

        assert d['type'] == 'chart'
        assert d['reference'] == 'chart.png'


class TestInsight:
    """Tests for Insight dataclass."""

    def test_insight_creation(self):
        """Should create insight with defaults."""
        from core.insight_engine import Insight

        i = Insight(
            id="insight_001",
            headline="Test Headline",
            supporting_text="Test supporting text."
        )

        assert i.severity == "supporting"
        assert i.category == "finding"
        assert i.confidence == 0.8

    def test_insight_to_dict_and_back(self):
        """Should round-trip through dict."""
        from core.insight_engine import Insight, Evidence

        original = Insight(
            id="insight_001",
            headline="Test",
            supporting_text="Text",
            evidence=[Evidence(type="metric", reference="ref", value=100)],
            severity="key",
            tags=["test"],
        )

        d = original.to_dict()
        restored = Insight.from_dict(d)

        assert restored.id == original.id
        assert restored.headline == original.headline
        assert len(restored.evidence) == 1
        assert restored.severity == "key"


class TestInsightCatalog:
    """Tests for InsightCatalog."""

    def test_catalog_creation(self):
        """Should create catalog."""
        from core.insight_engine import InsightCatalog, Insight

        catalog = InsightCatalog(
            generated_at="2025-01-01",
            business_question="What drives growth?",
            insights=[
                Insight(id="i1", headline="H1", supporting_text="T1", severity="key"),
                Insight(id="i2", headline="H2", supporting_text="T2"),
            ]
        )

        assert len(catalog.insights) == 2
        assert catalog.business_question == "What drives growth?"

    def test_get_key_insights(self):
        """Should filter to key insights."""
        from core.insight_engine import InsightCatalog, Insight

        catalog = InsightCatalog(
            generated_at="2025-01-01",
            business_question="Test",
            insights=[
                Insight(id="i1", headline="H1", supporting_text="T1", severity="key"),
                Insight(id="i2", headline="H2", supporting_text="T2", severity="supporting"),
                Insight(id="i3", headline="H3", supporting_text="T3", severity="key"),
            ]
        )

        key = catalog.get_key_insights()
        assert len(key) == 2
        assert all(i.severity == "key" for i in key)

    def test_save_and_load(self, tmp_path):
        """Should save and load catalog."""
        from core.insight_engine import InsightCatalog, Insight

        catalog = InsightCatalog(
            generated_at="2025-01-01",
            business_question="Test question",
            insights=[
                Insight(id="i1", headline="H1", supporting_text="T1"),
            ]
        )

        path = tmp_path / "catalog.yaml"
        catalog.save(str(path))

        loaded = InsightCatalog.load(str(path))
        assert loaded.business_question == "Test question"
        assert len(loaded.insights) == 1

    def test_get_by_category(self):
        """Should filter by category."""
        from core.insight_engine import InsightCatalog, Insight

        catalog = InsightCatalog(
            generated_at="2025-01-01",
            business_question="Test",
            insights=[
                Insight(id="i1", headline="H1", supporting_text="T1", category="finding"),
                Insight(id="i2", headline="H2", supporting_text="T2", category="recommendation"),
                Insight(id="i3", headline="H3", supporting_text="T3", category="finding"),
            ]
        )

        findings = catalog.get_by_category("finding")
        assert len(findings) == 2

    def test_get_recommendations(self):
        """Should get recommendation insights."""
        from core.insight_engine import InsightCatalog, Insight

        catalog = InsightCatalog(
            generated_at="2025-01-01",
            business_question="Test",
            insights=[
                Insight(id="i1", headline="H1", supporting_text="T1", category="finding"),
                Insight(id="i2", headline="H2", supporting_text="T2", category="recommendation"),
            ]
        )

        recs = catalog.get_recommendations()
        assert len(recs) == 1
        assert recs[0].id == "i2"


class TestInsightEngine:
    """Tests for InsightEngine."""

    def test_create_insight(self):
        """Should create insight with generated ID."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        i1 = engine.create_insight("Headline 1", "Text 1")
        i2 = engine.create_insight("Headline 2", "Text 2")

        assert i1.id == "insight_001"
        assert i2.id == "insight_002"

    def test_extract_comparison_insight(self):
        """Should extract comparison insight."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_comparison_insight(
            metric_name="Revenue",
            values={"North": 100, "South": 60, "East": 40}
        )

        assert "North" in insight.headline
        assert "50%" in insight.headline  # 100/200 = 50%
        assert insight.suggested_slide_type == "comparison"
        assert len(insight.evidence) >= 2

    def test_extract_comparison_with_chart(self):
        """Should include chart in evidence."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_comparison_insight(
            metric_name="Sales",
            values={"A": 80, "B": 20},
            chart_path="charts/sales.png"
        )

        chart_evidence = [e for e in insight.evidence if e.type == "chart"]
        assert len(chart_evidence) == 1
        assert chart_evidence[0].reference == "charts/sales.png"

    def test_extract_trend_insight_growth(self):
        """Should detect growth trend."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_trend_insight(
            metric_name="Revenue",
            periods=["Q1", "Q2", "Q3", "Q4"],
            values=[100, 110, 125, 140]
        )

        assert "Grows" in insight.headline
        assert "40%" in insight.headline  # 40% growth
        assert insight.suggested_slide_type == "trend"

    def test_extract_trend_insight_decline(self):
        """Should detect decline trend."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_trend_insight(
            metric_name="Costs",
            periods=["Jan", "Feb", "Mar"],
            values=[100, 85, 70]
        )

        assert "Declines" in insight.headline

    def test_extract_trend_insight_stable(self):
        """Should detect stable trend."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_trend_insight(
            metric_name="Margin",
            periods=["Q1", "Q2"],
            values=[100, 102]
        )

        assert "Stable" in insight.headline

    def test_extract_concentration_insight_high(self):
        """Should flag high concentration."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_concentration_insight(
            dimension="Revenue by Product",
            top_item="Product A",
            top_share=75,
            total_items=10
        )

        assert "High" in insight.headline
        assert insight.severity == "key"
        assert insight.category == "implication"

    def test_extract_concentration_insight_moderate(self):
        """Should flag moderate concentration."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_concentration_insight(
            dimension="Revenue by Product",
            top_item="Product A",
            top_share=55,
            total_items=10
        )

        assert "Moderate" in insight.headline
        assert insight.severity == "key"

    def test_extract_concentration_insight_low(self):
        """Should flag low concentration."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_concentration_insight(
            dimension="Revenue by Product",
            top_item="Product A",
            top_share=35,
            total_items=10
        )

        assert "Low" in insight.headline
        assert insight.severity == "supporting"

    def test_create_recommendation(self):
        """Should create recommendation insight."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.create_recommendation(
            action="Diversify Product Portfolio",
            rationale="Current concentration creates risk.",
            expected_impact="Reduces dependency on single product by 30%.",
            supporting_insights=["insight_001"],
            priority="high"
        )

        assert insight.category == "recommendation"
        assert insight.headline == "Diversify Product Portfolio"
        assert insight.severity == "key"

    def test_create_recommendation_medium_priority(self):
        """Should create medium priority recommendation."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.create_recommendation(
            action="Review pricing strategy",
            rationale="Margins are declining.",
            expected_impact="May improve margins by 5%.",
            priority="medium"
        )

        assert insight.severity == "supporting"

    def test_build_catalog(self):
        """Should build catalog with narrative arc."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insights = [
            engine.create_insight("Finding 1", "Text", category="finding", severity="key"),
            engine.create_insight("Finding 2", "Text", category="finding"),
            engine.create_insight("Implication", "Text", category="implication"),
            engine.create_insight("Recommendation", "Text", category="recommendation"),
        ]

        catalog = engine.build_catalog(insights, "What drives growth?")

        assert len(catalog.narrative_arc["key_findings"]) == 1
        assert len(catalog.narrative_arc["supporting_findings"]) == 1
        assert len(catalog.narrative_arc["implications"]) == 1
        assert len(catalog.narrative_arc["recommendations"]) == 1

    def test_rank_insights(self):
        """Should rank insights by importance."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insights = [
            engine.create_insight("Low", "Text", severity="context"),
            engine.create_insight("High", "Text", severity="key"),
            engine.create_insight("Medium", "Text", severity="supporting"),
        ]

        ranked = engine.rank_insights(insights)

        assert ranked[0].headline == "High"
        assert ranked[2].headline == "Low"

    def test_to_slide_sequence(self):
        """Should convert catalog to slides."""
        from core.insight_engine import InsightEngine, Evidence

        engine = InsightEngine()

        insights = [
            engine.create_insight(
                "Chart Insight",
                "With chart evidence",
                evidence=[Evidence(type="chart", reference="chart.png", value=None)],
                severity="key",
                category="finding"
            ),
            engine.create_insight(
                "Text Insight",
                "Without chart",
                severity="key",
                category="finding"
            ),
        ]

        catalog = engine.build_catalog(insights, "Test question")
        slides = engine.to_slide_sequence(catalog)

        # Should have section + 2 content slides
        assert len(slides) >= 3

        # Check for chart slide
        chart_slides = [s for s in slides if s.get("type") == "chart"]
        assert len(chart_slides) == 1

    def test_to_slide_sequence_with_recommendations(self):
        """Should include recommendation section in slides."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insights = [
            engine.create_insight("Key Finding", "Text", severity="key", category="finding"),
            engine.create_recommendation("Do This", "Because.", "Expected result.", priority="high"),
        ]

        catalog = engine.build_catalog(insights, "Test")
        slides = engine.to_slide_sequence(catalog)

        # Check for recommendations section
        section_titles = [s.get("title") for s in slides if s.get("type") == "section"]
        assert "Recommendations" in section_titles


class TestInsightEngineEdgeCases:
    """Edge case tests for InsightEngine."""

    def test_comparison_empty_values_raises(self):
        """Should raise on empty values."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        with pytest.raises(ValueError):
            engine.extract_comparison_insight("Revenue", {})

    def test_trend_mismatched_lengths_raises(self):
        """Should raise on mismatched periods/values."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        with pytest.raises(ValueError):
            engine.extract_trend_insight("Revenue", ["Q1", "Q2"], [100])

    def test_trend_single_period_raises(self):
        """Should raise on single period."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        with pytest.raises(ValueError):
            engine.extract_trend_insight("Revenue", ["Q1"], [100])

    def test_comparison_single_value(self):
        """Should handle single value comparison."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        insight = engine.extract_comparison_insight(
            metric_name="Revenue",
            values={"Only": 100}
        )

        assert "100%" in insight.headline
        assert "100%" in insight.supporting_text

    def test_trend_with_volatility(self):
        """Should detect volatility in trend."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        # High volatility: 100 -> 150 -> 80 -> 130
        insight = engine.extract_trend_insight(
            metric_name="Sales",
            periods=["Q1", "Q2", "Q3", "Q4"],
            values=[100, 150, 80, 130]
        )

        assert "peak" in insight.supporting_text.lower()

    def test_comparison_key_severity_threshold(self):
        """Should mark as key when leader share > 40%."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        # 45% share = key
        insight = engine.extract_comparison_insight(
            "Revenue",
            {"A": 45, "B": 30, "C": 25}
        )
        assert insight.severity == "key"

        # Reset counter
        engine._insight_counter = 0

        # 35% share = supporting
        insight = engine.extract_comparison_insight(
            "Revenue",
            {"A": 35, "B": 35, "C": 30}
        )
        assert insight.severity == "supporting"

    def test_trend_key_severity_threshold(self):
        """Should mark as key when change > 15%."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()

        # 20% change = key
        insight = engine.extract_trend_insight(
            "Revenue",
            ["Q1", "Q2"],
            [100, 120]
        )
        assert insight.severity == "key"

        # Reset counter
        engine._insight_counter = 0

        # 10% change = supporting
        insight = engine.extract_trend_insight(
            "Revenue",
            ["Q1", "Q2"],
            [100, 110]
        )
        assert insight.severity == "supporting"


class TestEvidenceFormatting:
    """Tests for evidence formatting."""

    def test_format_evidence_notes_empty(self):
        """Should handle empty evidence."""
        from core.insight_engine import InsightEngine

        engine = InsightEngine()
        result = engine._format_evidence_notes([])
        assert result == ""

    def test_format_evidence_notes_with_values(self):
        """Should format evidence with values."""
        from core.insight_engine import InsightEngine, Evidence

        engine = InsightEngine()
        evidence = [
            Evidence(type="metric", reference="rev", value=1000, label="Revenue"),
            Evidence(type="chart", reference="chart.png", value=None, label="Chart"),
        ]

        result = engine._format_evidence_notes(evidence)
        assert "Revenue: 1000" in result
        assert "Chart" not in result  # None values excluded

    def test_insight_to_slide_with_chart(self):
        """Should create chart slide spec."""
        from core.insight_engine import InsightEngine, Insight, Evidence

        engine = InsightEngine()
        insight = Insight(
            id="i1",
            headline="Test Headline",
            supporting_text="Test supporting text that is quite long.",
            evidence=[Evidence(type="chart", reference="charts/test.png", value=None)]
        )

        spec = engine._insight_to_slide_spec(insight)

        assert spec["type"] == "chart"
        assert spec["title"] == "Test Headline"
        assert spec["chart_path"] == "charts/test.png"

    def test_insight_to_slide_without_chart(self):
        """Should create content slide spec."""
        from core.insight_engine import InsightEngine, Insight, Evidence

        engine = InsightEngine()
        insight = Insight(
            id="i1",
            headline="Test Headline",
            supporting_text="Test supporting text.",
            evidence=[Evidence(type="metric", reference="rev", value=1000)]
        )

        spec = engine._insight_to_slide_spec(insight)

        assert spec["type"] == "content"
        assert spec["title"] == "Test Headline"
        assert len(spec["bullet_points"]) == 1
