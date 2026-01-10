"""Matching Service for intelligent expert-demand matching."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.expert import Expert, QualificationStatus
from src.app.models.company import Demand, DemandStatus
from src.app.models.matching import Matching, MatchingStatus
from src.app.models.expert_score import ExpertScore


@dataclass
class MatchScore:
    """Match score breakdown between an expert and a demand."""

    total_score: float  # 0-100
    specialty_score: float  # 40% weight - required vs expert specialties
    qualification_score: float  # 15% weight - QUALIFIED bonus
    career_score: float  # 15% weight - years relative to demand
    evaluation_score: float  # 20% weight - average grading score
    availability_score: float  # 10% weight - active matchings count
    details: dict[str, Any]  # Detailed breakdown


@dataclass
class MatchCandidate:
    """A candidate expert for a demand match."""

    expert_id: UUID
    expert_name: str
    score: MatchScore
    recommendation_reasons: list[str]


class MatchingService:
    """Service for calculating match scores and finding best expert-demand matches.

    The matching algorithm considers:
    1. Specialty match (40%): How well expert specialties match demand requirements
    2. Qualification status (15%): QUALIFIED experts get bonus points
    3. Career experience (15%): Years of experience relative to demand needs
    4. Evaluation score (20%): Expert's average evaluation performance
    5. Availability (10%): Fewer active matchings = more available
    """

    # Scoring weights
    WEIGHT_SPECIALTY = 0.40
    WEIGHT_QUALIFICATION = 0.15
    WEIGHT_CAREER = 0.15
    WEIGHT_EVALUATION = 0.20
    WEIGHT_AVAILABILITY = 0.10

    @classmethod
    async def calculate_match_score(
        cls,
        db: AsyncSession,
        expert: Expert,
        demand: Demand,
    ) -> MatchScore:
        """Calculate match score between an expert and a demand.

        Args:
            db: Database session
            expert: Expert to evaluate
            demand: Demand to match against

        Returns:
            MatchScore with total and component scores
        """
        details: dict[str, Any] = {}

        # 1. Specialty Match (40%)
        specialty_score = cls._calculate_specialty_score(expert, demand, details)

        # 2. Qualification Status (15%)
        qualification_score = cls._calculate_qualification_score(expert, details)

        # 3. Career Experience (15%)
        career_score = cls._calculate_career_score(expert, demand, details)

        # 4. Evaluation Score (20%)
        evaluation_score = await cls._calculate_evaluation_score(db, expert, details)

        # 5. Availability (10%)
        availability_score = await cls._calculate_availability_score(db, expert, details)

        # Calculate weighted total
        total_score = (
            specialty_score * cls.WEIGHT_SPECIALTY
            + qualification_score * cls.WEIGHT_QUALIFICATION
            + career_score * cls.WEIGHT_CAREER
            + evaluation_score * cls.WEIGHT_EVALUATION
            + availability_score * cls.WEIGHT_AVAILABILITY
        )

        return MatchScore(
            total_score=round(total_score, 2),
            specialty_score=round(specialty_score, 2),
            qualification_score=round(qualification_score, 2),
            career_score=round(career_score, 2),
            evaluation_score=round(evaluation_score, 2),
            availability_score=round(availability_score, 2),
            details=details,
        )

    @classmethod
    def _calculate_specialty_score(
        cls,
        expert: Expert,
        demand: Demand,
        details: dict[str, Any],
    ) -> float:
        """Calculate specialty match score.

        Returns 100 if all required specialties match, proportionally less otherwise.
        """
        expert_specs = set(expert.specialties or [])
        required_specs = set(demand.requirements.get("specialties", []) if demand.requirements else [])

        if not required_specs:
            # No specific requirements, base score on expert having specialties
            score = 80.0 if expert_specs else 50.0
        else:
            # Calculate match percentage
            matched = expert_specs & required_specs
            score = (len(matched) / len(required_specs)) * 100 if required_specs else 50.0

        details["specialty"] = {
            "expert_specialties": list(expert_specs),
            "required_specialties": list(required_specs),
            "matched": list(expert_specs & required_specs) if required_specs else [],
            "score": score,
        }

        return score

    @classmethod
    def _calculate_qualification_score(
        cls,
        expert: Expert,
        details: dict[str, Any],
    ) -> float:
        """Calculate qualification status score.

        QUALIFIED: 100, PENDING: 60, DISQUALIFIED: 0
        """
        if expert.qualification_status == QualificationStatus.QUALIFIED:
            score = 100.0
        elif expert.qualification_status == QualificationStatus.PENDING:
            score = 60.0
        else:
            score = 0.0

        details["qualification"] = {
            "status": expert.qualification_status.value if hasattr(expert.qualification_status, 'value') else str(expert.qualification_status),
            "score": score,
        }

        return score

    @classmethod
    def _calculate_career_score(
        cls,
        expert: Expert,
        demand: Demand,
        details: dict[str, Any],
    ) -> float:
        """Calculate career experience score.

        Based on years of experience relative to demand requirements.
        """
        expert_years = expert.career_years or 0
        required_years = demand.requirements.get("min_career_years", 0) if demand.requirements else 0

        if required_years == 0:
            # No requirement, give points based on experience
            score = min(50 + (expert_years * 5), 100)
        elif expert_years >= required_years:
            # Meets or exceeds requirement
            bonus = min((expert_years - required_years) * 5, 20)
            score = 80 + bonus
        else:
            # Below requirement, proportional score
            score = (expert_years / required_years) * 70

        details["career"] = {
            "expert_years": expert_years,
            "required_years": required_years,
            "meets_requirement": expert_years >= required_years,
            "score": score,
        }

        return score

    @classmethod
    async def _calculate_evaluation_score(
        cls,
        db: AsyncSession,
        expert: Expert,
        details: dict[str, Any],
    ) -> float:
        """Calculate evaluation performance score.

        Based on expert's average evaluation percentage.
        """
        # Get expert score
        result = await db.execute(
            select(ExpertScore).where(ExpertScore.expert_id == expert.id)
        )
        expert_score = result.scalar_one_or_none()

        if expert_score and expert_score.average_percentage > 0:
            score = expert_score.average_percentage
        else:
            # No evaluation yet, neutral score
            score = 50.0

        details["evaluation"] = {
            "average_percentage": expert_score.average_percentage if expert_score else None,
            "graded_count": expert_score.graded_count if expert_score else 0,
            "total_count": expert_score.total_count if expert_score else 0,
            "score": score,
        }

        return score

    @classmethod
    async def _calculate_availability_score(
        cls,
        db: AsyncSession,
        expert: Expert,
        details: dict[str, Any],
    ) -> float:
        """Calculate availability score based on active matchings.

        Fewer active matchings = higher availability = higher score.
        """
        # Count active matchings
        active_count = (
            await db.execute(
                select(func.count())
                .select_from(Matching)
                .where(
                    Matching.expert_id == expert.id,
                    Matching.is_active == True,
                    Matching.status.in_([
                        MatchingStatus.PROPOSED,
                        MatchingStatus.ACCEPTED,
                        MatchingStatus.IN_PROGRESS,
                    ]),
                )
            )
        ).scalar() or 0

        # Score inversely proportional to active matchings
        # 0 matchings = 100, 1 = 80, 2 = 60, 3+ = 40
        if active_count == 0:
            score = 100.0
        elif active_count == 1:
            score = 80.0
        elif active_count == 2:
            score = 60.0
        else:
            score = max(40.0, 100 - (active_count * 20))

        details["availability"] = {
            "active_matchings": active_count,
            "score": score,
        }

        return score

    @classmethod
    async def find_best_matches(
        cls,
        db: AsyncSession,
        demand_id: UUID,
        top_n: int = 10,
        min_score: float = 50.0,
    ) -> list[MatchCandidate]:
        """Find the best expert matches for a demand.

        Args:
            db: Database session
            demand_id: Demand UUID to find matches for
            top_n: Maximum number of candidates to return
            min_score: Minimum score threshold

        Returns:
            List of MatchCandidates sorted by score descending
        """
        from src.app.models.user import User

        # Get demand
        demand_result = await db.execute(select(Demand).where(Demand.id == demand_id))
        demand = demand_result.scalar_one_or_none()

        if not demand:
            raise ValueError(f"Demand {demand_id} not found")

        # Get all qualified/pending experts
        experts_result = await db.execute(
            select(Expert, User)
            .join(User, Expert.user_id == User.id)
            .where(
                Expert.is_active == True,
                Expert.qualification_status.in_([
                    QualificationStatus.QUALIFIED,
                    QualificationStatus.PENDING,
                ]),
            )
        )

        candidates: list[MatchCandidate] = []

        for expert, user in experts_result:
            # Calculate score
            score = await cls.calculate_match_score(db, expert, demand)

            if score.total_score >= min_score:
                # Generate recommendation reasons
                reasons = cls._generate_recommendation_reasons(score)

                candidates.append(
                    MatchCandidate(
                        expert_id=expert.id,
                        expert_name=user.name,
                        score=score,
                        recommendation_reasons=reasons,
                    )
                )

        # Sort by total score descending
        candidates.sort(key=lambda c: c.score.total_score, reverse=True)

        return candidates[:top_n]

    @classmethod
    def _generate_recommendation_reasons(cls, score: MatchScore) -> list[str]:
        """Generate human-readable recommendation reasons based on score breakdown."""
        reasons = []

        # Specialty match
        if score.specialty_score >= 80:
            reasons.append("전문분야가 요구사항과 잘 일치합니다")
        elif score.specialty_score >= 60:
            reasons.append("전문분야가 부분적으로 일치합니다")

        # Qualification
        if score.qualification_score >= 100:
            reasons.append("인증된 전문가입니다")

        # Career
        if score.career_score >= 90:
            reasons.append("풍부한 경력을 보유하고 있습니다")
        elif score.career_score >= 70:
            reasons.append("필요 경력을 충족합니다")

        # Evaluation
        if score.evaluation_score >= 80:
            reasons.append("평가 점수가 우수합니다")

        # Availability
        if score.availability_score >= 80:
            reasons.append("현재 가용성이 높습니다")

        return reasons

    @classmethod
    async def check_compatibility(
        cls,
        db: AsyncSession,
        expert_id: UUID,
        demand_id: UUID,
    ) -> dict[str, Any]:
        """Check compatibility between a specific expert and demand.

        Args:
            db: Database session
            expert_id: Expert UUID
            demand_id: Demand UUID

        Returns:
            Compatibility analysis with score and recommendations
        """
        # Get expert
        expert_result = await db.execute(select(Expert).where(Expert.id == expert_id))
        expert = expert_result.scalar_one_or_none()

        if not expert:
            raise ValueError(f"Expert {expert_id} not found")

        # Get demand
        demand_result = await db.execute(select(Demand).where(Demand.id == demand_id))
        demand = demand_result.scalar_one_or_none()

        if not demand:
            raise ValueError(f"Demand {demand_id} not found")

        # Calculate score
        score = await cls.calculate_match_score(db, expert, demand)
        reasons = cls._generate_recommendation_reasons(score)

        # Determine recommendation
        if score.total_score >= 80:
            recommendation = "HIGHLY_RECOMMENDED"
            recommendation_text = "강력 추천"
        elif score.total_score >= 60:
            recommendation = "RECOMMENDED"
            recommendation_text = "추천"
        elif score.total_score >= 40:
            recommendation = "POSSIBLE"
            recommendation_text = "가능"
        else:
            recommendation = "NOT_RECOMMENDED"
            recommendation_text = "비추천"

        return {
            "expert_id": str(expert_id),
            "demand_id": str(demand_id),
            "total_score": score.total_score,
            "score_breakdown": {
                "specialty": score.specialty_score,
                "qualification": score.qualification_score,
                "career": score.career_score,
                "evaluation": score.evaluation_score,
                "availability": score.availability_score,
            },
            "recommendation": recommendation,
            "recommendation_text": recommendation_text,
            "reasons": reasons,
            "details": score.details,
        }

    @classmethod
    async def get_matching_analytics(
        cls,
        db: AsyncSession,
    ) -> dict[str, Any]:
        """Get matching analytics and statistics.

        Returns:
            Analytics data including success rates, trends, and distributions
        """
        # Total matchings by status
        status_counts = {}
        for status in MatchingStatus:
            count = (
                await db.execute(
                    select(func.count())
                    .select_from(Matching)
                    .where(Matching.status == status, Matching.is_active == True)
                )
            ).scalar() or 0
            status_counts[status.value] = count

        # Success rate (completed / (completed + rejected + cancelled))
        completed = status_counts.get("COMPLETED", 0)
        rejected = status_counts.get("REJECTED", 0)
        cancelled = status_counts.get("CANCELLED", 0)
        resolved = completed + rejected + cancelled
        success_rate = (completed / resolved * 100) if resolved > 0 else 0.0

        # Average match score
        avg_score_result = await db.execute(
            select(func.avg(Matching.match_score)).where(
                Matching.match_score.isnot(None),
                Matching.is_active == True,
            )
        )
        avg_match_score = avg_score_result.scalar() or 0.0

        # Top matched experts
        top_experts_result = await db.execute(
            select(Matching.expert_id, func.count().label("match_count"))
            .where(Matching.is_active == True)
            .group_by(Matching.expert_id)
            .order_by(func.count().desc())
            .limit(5)
        )
        top_experts = [
            {"expert_id": str(row[0]), "match_count": row[1]}
            for row in top_experts_result
        ]

        return {
            "status_distribution": status_counts,
            "success_rate": round(success_rate, 1),
            "average_match_score": round(float(avg_match_score), 1),
            "total_active_matchings": sum(
                status_counts.get(s, 0)
                for s in ["PROPOSED", "ACCEPTED", "IN_PROGRESS"]
            ),
            "total_completed": completed,
            "top_matched_experts": top_experts,
        }
