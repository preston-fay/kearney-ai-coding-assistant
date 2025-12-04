"""
KACA Insight Engine

Extracts structured insights from data analysis and generates
presentation-ready content with evidence linkage.

Usage:
    from core.insight_engine import InsightEngine, Insight, Evidence

    engine = InsightEngine()
    insights = engine.extract_from_analysis(analysis_results, context)
    narrative = engine.generate_narrative(insights)
    slides = engine.to_slide_sequence(insights)
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Evidence:
    """Supporting evidence for an insight."""
    type: str  # "chart", "metric", "data_point", "comparison"
    reference: str  # Path to chart or metric identifier
    value: Any  # The actual value/data
    label: Optional[str] = None  # Human-readable label

    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'reference': self.reference,
            'value': self.value,
            'label': self.label,
        }


@dataclass
class Insight:
    """A structured insight with evidence and metadata."""
    id: str
    headline: str  # Action title format (e.g., "Northeast Drives 60% of Growth")
    supporting_text: str  # 2-3 sentence explanation
    evidence: List[Evidence] = field(default_factory=list)
    severity: str = "supporting"  # "key", "supporting", "context"
    category: str = "finding"  # "finding", "implication", "recommendation"
    suggested_slide_type: str = "content"  # "comparison", "trend", "summary", "risk", "recommendation"
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.8  # 0.0 to 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'headline': self.headline,
            'supporting_text': self.supporting_text,
            'evidence': [e.to_dict() for e in self.evidence],
            'severity': self.severity,
            'category': self.category,
            'suggested_slide_type': self.suggested_slide_type,
            'tags': self.tags,
            'confidence': self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Insight':
        evidence = [Evidence(**e) for e in data.get('evidence', [])]
        return cls(
            id=data['id'],
            headline=data['headline'],
            supporting_text=data['supporting_text'],
            evidence=evidence,
            severity=data.get('severity', 'supporting'),
            category=data.get('category', 'finding'),
            suggested_slide_type=data.get('suggested_slide_type', 'content'),
            tags=data.get('tags', []),
            confidence=data.get('confidence', 0.8),
        )


@dataclass
class InsightCatalog:
    """Collection of insights with narrative structure."""
    generated_at: str
    business_question: str
    insights: List[Insight]
    narrative_arc: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'generated_at': self.generated_at,
            'business_question': self.business_question,
            'insights': [i.to_dict() for i in self.insights],
            'narrative_arc': self.narrative_arc,
        }

    def save(self, path: str) -> None:
        """Save catalog to YAML file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)
        logger.info(f"Insight catalog saved to {path}")

    @classmethod
    def load(cls, path: str) -> 'InsightCatalog':
        """Load catalog from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        insights = [Insight.from_dict(i) for i in data.get('insights', [])]
        return cls(
            generated_at=data['generated_at'],
            business_question=data['business_question'],
            insights=insights,
            narrative_arc=data.get('narrative_arc', {}),
        )

    def get_key_insights(self) -> List[Insight]:
        """Get insights marked as key."""
        return [i for i in self.insights if i.severity == 'key']

    def get_by_category(self, category: str) -> List[Insight]:
        """Get insights by category."""
        return [i for i in self.insights if i.category == category]

    def get_recommendations(self) -> List[Insight]:
        """Get recommendation insights."""
        return self.get_by_category('recommendation')


class InsightEngine:
    """
    Engine for extracting and structuring insights from data analysis.

    The engine takes analysis results (metrics, comparisons, trends) and
    transforms them into structured insights suitable for presentations.
    """

    def __init__(self):
        self._insight_counter = 0

    def _generate_id(self) -> str:
        """Generate unique insight ID."""
        self._insight_counter += 1
        return f"insight_{self._insight_counter:03d}"

    def create_insight(
        self,
        headline: str,
        supporting_text: str,
        evidence: List[Evidence] = None,
        severity: str = "supporting",
        category: str = "finding",
        suggested_slide_type: str = "content",
        tags: List[str] = None,
        confidence: float = 0.8,
    ) -> Insight:
        """
        Create a new insight with generated ID.

        Args:
            headline: Action title (insight as a statement)
            supporting_text: 2-3 sentence explanation
            evidence: List of supporting evidence
            severity: "key", "supporting", or "context"
            category: "finding", "implication", or "recommendation"
            suggested_slide_type: Recommended slide layout
            tags: Classification tags
            confidence: Confidence score 0-1

        Returns:
            New Insight object
        """
        return Insight(
            id=self._generate_id(),
            headline=headline,
            supporting_text=supporting_text,
            evidence=evidence or [],
            severity=severity,
            category=category,
            suggested_slide_type=suggested_slide_type,
            tags=tags or [],
            confidence=confidence,
        )

    def extract_comparison_insight(
        self,
        metric_name: str,
        values: Dict[str, float],
        chart_path: Optional[str] = None,
    ) -> Insight:
        """
        Extract insight from a comparison of values.

        Args:
            metric_name: What's being compared (e.g., "Revenue")
            values: Dict of label -> value (e.g., {"North": 100, "South": 80})
            chart_path: Path to supporting chart if available

        Returns:
            Insight about the comparison
        """
        if not values:
            raise ValueError("Values dict cannot be empty")

        # Find leader and calculate shares
        total = sum(values.values())
        sorted_items = sorted(values.items(), key=lambda x: x[1], reverse=True)
        leader, leader_value = sorted_items[0]
        leader_share = (leader_value / total * 100) if total > 0 else 0

        # Generate headline
        headline = f"{leader} Leads {metric_name} at {leader_share:.0f}% Share"

        # Generate supporting text
        if len(sorted_items) > 1:
            runner_up, runner_up_value = sorted_items[1]
            gap = leader_value - runner_up_value
            supporting_text = (
                f"{leader} accounts for {leader_share:.0f}% of total {metric_name.lower()}, "
                f"leading {runner_up} by {gap:,.0f}. "
            )
            if len(sorted_items) > 2:
                others = ", ".join([item[0] for item in sorted_items[2:4]])
                supporting_text += f"Other significant contributors include {others}."
        else:
            supporting_text = f"{leader} represents 100% of {metric_name.lower()}."

        # Build evidence
        evidence = [
            Evidence(
                type="metric",
                reference=f"{leader}_{metric_name}",
                value=leader_value,
                label=f"{leader} {metric_name}"
            ),
            Evidence(
                type="metric",
                reference=f"{leader}_share",
                value=f"{leader_share:.0f}%",
                label=f"{leader} share of total"
            ),
        ]

        if chart_path:
            evidence.insert(0, Evidence(
                type="chart",
                reference=chart_path,
                value=None,
                label=f"{metric_name} comparison chart"
            ))

        return self.create_insight(
            headline=headline,
            supporting_text=supporting_text,
            evidence=evidence,
            severity="key" if leader_share > 40 else "supporting",
            category="finding",
            suggested_slide_type="comparison",
            tags=["comparison", metric_name.lower()],
        )

    def extract_trend_insight(
        self,
        metric_name: str,
        periods: List[str],
        values: List[float],
        chart_path: Optional[str] = None,
    ) -> Insight:
        """
        Extract insight from a trend over time.

        Args:
            metric_name: What's trending (e.g., "Revenue")
            periods: Time period labels (e.g., ["Q1", "Q2", "Q3"])
            values: Values for each period
            chart_path: Path to supporting chart if available

        Returns:
            Insight about the trend
        """
        if len(periods) != len(values) or len(values) < 2:
            raise ValueError("Need at least 2 periods with matching values")

        # Calculate trend
        start_value = values[0]
        end_value = values[-1]
        change = end_value - start_value
        change_pct = (change / start_value * 100) if start_value != 0 else 0

        # Determine trend direction
        if change_pct > 5:
            direction = "Grows"
            trend_word = "growth"
        elif change_pct < -5:
            direction = "Declines"
            trend_word = "decline"
        else:
            direction = "Remains Stable"
            trend_word = "stability"

        # Generate headline
        if abs(change_pct) > 5:
            headline = f"{metric_name} {direction} {abs(change_pct):.0f}% from {periods[0]} to {periods[-1]}"
        else:
            headline = f"{metric_name} {direction} Across {periods[0]}-{periods[-1]} Period"

        # Generate supporting text
        supporting_text = (
            f"{metric_name} moved from {start_value:,.0f} in {periods[0]} to "
            f"{end_value:,.0f} in {periods[-1]}, representing {trend_word} of {abs(change_pct):.1f}%. "
        )

        # Check for volatility
        if len(values) > 2:
            max_val = max(values)
            min_val = min(values)
            volatility = (max_val - min_val) / start_value * 100 if start_value != 0 else 0
            if volatility > 20:
                peak_period = periods[values.index(max_val)]
                supporting_text += f"Notable peak occurred in {peak_period}."

        # Build evidence
        evidence = [
            Evidence(
                type="metric",
                reference=f"{metric_name}_change",
                value=f"{change_pct:+.1f}%",
                label=f"{metric_name} change"
            ),
            Evidence(
                type="data_point",
                reference=f"{metric_name}_start",
                value=start_value,
                label=f"{periods[0]} value"
            ),
            Evidence(
                type="data_point",
                reference=f"{metric_name}_end",
                value=end_value,
                label=f"{periods[-1]} value"
            ),
        ]

        if chart_path:
            evidence.insert(0, Evidence(
                type="chart",
                reference=chart_path,
                value=None,
                label=f"{metric_name} trend chart"
            ))

        return self.create_insight(
            headline=headline,
            supporting_text=supporting_text,
            evidence=evidence,
            severity="key" if abs(change_pct) > 15 else "supporting",
            category="finding",
            suggested_slide_type="trend",
            tags=["trend", metric_name.lower()],
        )

    def extract_concentration_insight(
        self,
        dimension: str,
        top_item: str,
        top_share: float,
        total_items: int,
        chart_path: Optional[str] = None,
    ) -> Insight:
        """
        Extract insight about concentration risk.

        Args:
            dimension: What's concentrated (e.g., "Revenue by Product")
            top_item: The dominant item
            top_share: Share of top item (0-100)
            total_items: Total number of items
            chart_path: Path to supporting chart

        Returns:
            Insight about concentration
        """
        # Determine severity based on concentration level
        if top_share > 70:
            risk_level = "High"
            severity = "key"
        elif top_share > 50:
            risk_level = "Moderate"
            severity = "key"
        else:
            risk_level = "Low"
            severity = "supporting"

        headline = f"{top_item} Concentration Creates {risk_level} Dependency Risk"

        supporting_text = (
            f"{top_share:.0f}% of {dimension.lower()} depends on {top_item}, "
            f"while {total_items - 1} other options exist. "
        )

        if top_share > 50:
            supporting_text += "Diversification may reduce exposure to single-source risk."

        evidence = [
            Evidence(
                type="metric",
                reference=f"{top_item}_concentration",
                value=f"{top_share:.0f}%",
                label=f"{top_item} share"
            ),
            Evidence(
                type="metric",
                reference="item_count",
                value=total_items,
                label="Total options"
            ),
        ]

        if chart_path:
            evidence.insert(0, Evidence(
                type="chart",
                reference=chart_path,
                value=None,
                label="Concentration chart"
            ))

        return self.create_insight(
            headline=headline,
            supporting_text=supporting_text,
            evidence=evidence,
            severity=severity,
            category="implication",
            suggested_slide_type="risk",
            tags=["concentration", "risk", dimension.lower()],
        )

    def create_recommendation(
        self,
        action: str,
        rationale: str,
        expected_impact: str,
        supporting_insights: List[str] = None,
        priority: str = "medium",
    ) -> Insight:
        """
        Create a recommendation insight.

        Args:
            action: What should be done
            rationale: Why it should be done
            expected_impact: What the expected outcome is
            supporting_insights: IDs of insights that support this recommendation
            priority: "high", "medium", or "low"

        Returns:
            Recommendation insight
        """
        headline = action  # Recommendations use action as headline

        supporting_text = f"{rationale} {expected_impact}"

        evidence = []
        if supporting_insights:
            evidence.append(Evidence(
                type="insight_reference",
                reference=",".join(supporting_insights),
                value=None,
                label="Supporting findings"
            ))

        return self.create_insight(
            headline=headline,
            supporting_text=supporting_text,
            evidence=evidence,
            severity="key" if priority == "high" else "supporting",
            category="recommendation",
            suggested_slide_type="recommendation",
            tags=["recommendation", priority],
            confidence=0.7,  # Recommendations are inherently less certain
        )

    def build_catalog(
        self,
        insights: List[Insight],
        business_question: str,
    ) -> InsightCatalog:
        """
        Build an insight catalog with narrative structure.

        Args:
            insights: List of insights to include
            business_question: The question being answered

        Returns:
            InsightCatalog with narrative arc
        """
        # Organize by category
        findings = [i for i in insights if i.category == "finding"]
        implications = [i for i in insights if i.category == "implication"]
        recommendations = [i for i in insights if i.category == "recommendation"]

        # Sort within categories by severity
        severity_order = {"key": 0, "supporting": 1, "context": 2}
        findings.sort(key=lambda x: severity_order.get(x.severity, 1))
        implications.sort(key=lambda x: severity_order.get(x.severity, 1))
        recommendations.sort(key=lambda x: severity_order.get(x.severity, 1))

        # Build narrative arc
        narrative_arc = {
            "opening": f"Analysis addressing: {business_question}",
            "key_findings": [i.id for i in findings if i.severity == "key"],
            "supporting_findings": [i.id for i in findings if i.severity != "key"],
            "implications": [i.id for i in implications],
            "recommendations": [i.id for i in recommendations],
        }

        return InsightCatalog(
            generated_at=datetime.now().isoformat(),
            business_question=business_question,
            insights=insights,
            narrative_arc=narrative_arc,
        )

    def rank_insights(self, insights: List[Insight]) -> List[Insight]:
        """
        Rank insights by importance.

        Ranking considers:
        - Severity (key > supporting > context)
        - Category (finding > implication > recommendation)
        - Confidence score
        """
        def score(insight: Insight) -> float:
            severity_scores = {"key": 3, "supporting": 2, "context": 1}
            category_scores = {"finding": 1.2, "implication": 1.1, "recommendation": 1.0}

            base = severity_scores.get(insight.severity, 1)
            multiplier = category_scores.get(insight.category, 1.0)
            confidence = insight.confidence

            return base * multiplier * confidence

        return sorted(insights, key=score, reverse=True)

    def to_slide_sequence(self, catalog: InsightCatalog) -> List[Dict[str, Any]]:
        """
        Convert insight catalog to slide specifications.

        Returns list of slide specs suitable for KDSPresentation.
        """
        slides = []
        arc = catalog.narrative_arc

        # Opening slide with agenda
        slides.append({
            "type": "section",
            "title": "Key Findings",
            "section_number": 1,
        })

        # Key findings
        for insight_id in arc.get("key_findings", []):
            insight = next((i for i in catalog.insights if i.id == insight_id), None)
            if insight:
                slides.append(self._insight_to_slide_spec(insight))

        # Supporting findings (if any key ones exist, otherwise skip)
        supporting = arc.get("supporting_findings", [])
        if supporting and arc.get("key_findings"):
            slides.append({
                "type": "section",
                "title": "Additional Findings",
                "section_number": 2,
            })
            for insight_id in supporting[:3]:  # Limit to 3
                insight = next((i for i in catalog.insights if i.id == insight_id), None)
                if insight:
                    slides.append(self._insight_to_slide_spec(insight))

        # Implications
        implications = arc.get("implications", [])
        if implications:
            slides.append({
                "type": "section",
                "title": "Implications",
                "section_number": 3,
            })
            for insight_id in implications:
                insight = next((i for i in catalog.insights if i.id == insight_id), None)
                if insight:
                    slides.append(self._insight_to_slide_spec(insight))

        # Recommendations
        recommendations = arc.get("recommendations", [])
        if recommendations:
            slides.append({
                "type": "section",
                "title": "Recommendations",
                "section_number": 4,
            })
            for insight_id in recommendations:
                insight = next((i for i in catalog.insights if i.id == insight_id), None)
                if insight:
                    slides.append(self._insight_to_slide_spec(insight))

        return slides

    def _insight_to_slide_spec(self, insight: Insight) -> Dict[str, Any]:
        """Convert single insight to slide spec."""
        # Find chart evidence if any
        chart_evidence = next(
            (e for e in insight.evidence if e.type == "chart"),
            None
        )

        if chart_evidence:
            return {
                "type": "chart",
                "title": insight.headline,
                "chart_path": chart_evidence.reference,
                "caption": insight.supporting_text[:200],
                "notes": insight.supporting_text,
            }
        else:
            return {
                "type": "content",
                "title": insight.headline,
                "bullet_points": [insight.supporting_text],
                "notes": self._format_evidence_notes(insight.evidence),
            }

    def _format_evidence_notes(self, evidence: List[Evidence]) -> str:
        """Format evidence for slide notes."""
        if not evidence:
            return ""

        lines = ["Supporting Evidence:"]
        for e in evidence:
            if e.value is not None:
                lines.append(f"- {e.label or e.reference}: {e.value}")

        return "\n".join(lines)
