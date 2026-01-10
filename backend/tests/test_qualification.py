"""Tests for qualification verification logic."""
import pytest

from src.app.api.v1.experts import verify_qualification_rules
from src.app.models.expert import DegreeType, OrgType, QualificationStatus


class TestQualificationVerification:
    """Test qualification verification rules."""

    def test_phd_with_related_field_and_sufficient_career(self):
        """Test PhD with related field and 3+ years career - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=DegreeType.PHD,
            degree_field="컴퓨터공학",
            career_years=3,
            position="연구원",
            org_type=OrgType.RESEARCH,
            certifications=None,
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["degree_field_career"].passed is True
        assert checks["overall"].passed is True

    def test_phd_with_related_field_but_insufficient_career(self):
        """Test PhD with related field but less than 3 years career."""
        status, checks = verify_qualification_rules(
            degree_type=DegreeType.PHD,
            degree_field="인공지능",
            career_years=2,  # Less than required 3 years
            position=None,
            org_type=None,
            certifications=None,
        )

        assert status == QualificationStatus.DISQUALIFIED
        assert checks["degree_field_career"].passed is False
        assert "2년 < 요구 3년" in checks["degree_field_career"].reason

    def test_master_with_related_field_and_sufficient_career(self):
        """Test Master with related field and 5+ years career - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=DegreeType.MASTER,
            degree_field="데이터사이언스",
            career_years=5,
            position=None,
            org_type=None,
            certifications=None,
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["degree_field_career"].passed is True

    def test_bachelor_with_related_field_and_sufficient_career(self):
        """Test Bachelor with related field and 7+ years career - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=DegreeType.BACHELOR,
            degree_field="소프트웨어",
            career_years=7,
            position=None,
            org_type=None,
            certifications=None,
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["degree_field_career"].passed is True

    def test_high_level_position_without_degree(self):
        """Test high-level position (부장) without degree - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=None,
            degree_field=None,
            career_years=None,
            position="부장",
            org_type=OrgType.COMPANY,
            certifications=None,
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["position_certification"].passed is True
        assert "직급/직위 요건 충족" in checks["position_certification"].reason

    def test_university_faculty(self):
        """Test university professor - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=DegreeType.PHD,
            degree_field="전기전자공학",
            career_years=10,
            position="부교수",
            org_type=OrgType.UNIVERSITY,
            certifications=None,
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["position_certification"].passed is True

    def test_special_certification_engineer(self):
        """Test special certification (특급기술자) - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=None,
            degree_field=None,
            career_years=None,
            position=None,
            org_type=None,
            certifications=[{"name": "엔지니어링산업진흥법 특급기술자"}],
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["position_certification"].passed is True
        assert "특급" in checks["position_certification"].reason

    def test_unrelated_field_even_with_career(self):
        """Test unrelated field even with sufficient career - should be DISQUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=DegreeType.MASTER,
            degree_field="문학",  # Unrelated field
            career_years=10,
            position=None,
            org_type=None,
            certifications=None,
        )

        assert status == QualificationStatus.DISQUALIFIED
        assert checks["degree_field_career"].passed is False

    def test_no_degree_no_position_no_certification(self):
        """Test no qualification criteria met - should be DISQUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=None,
            degree_field=None,
            career_years=None,
            position="사원",  # Low level position
            org_type=OrgType.COMPANY,
            certifications=[{"name": "정처기"}],  # Regular certification
        )

        assert status == QualificationStatus.DISQUALIFIED
        assert checks["overall"].passed is False
        assert "자격요건 미충족" in checks["overall"].reason

    def test_gisa_certification(self):
        """Test 기술사 (Professional Engineer) certification - should be QUALIFIED."""
        status, checks = verify_qualification_rules(
            degree_type=None,
            degree_field=None,
            career_years=None,
            position=None,
            org_type=None,
            certifications=[{"name": "정보통신기술사"}],
        )

        assert status == QualificationStatus.QUALIFIED
        assert checks["position_certification"].passed is True
        assert "기술사" in checks["position_certification"].reason
