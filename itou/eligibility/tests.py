from django.test import TestCase

from itou.eligibility.models import AdministrativeCriteria, EligibilityDiagnosis
from itou.siaes.factories import SiaeWithMembershipFactory
from itou.users.factories import JobSeekerFactory
from itou.utils.perms.user import KIND_SIAE_STAFF, UserInfo


class EligibilityDiagnosisModelTest(TestCase):
    def test_create_diagnosis(self):

        job_seeker = JobSeekerFactory()
        siae = SiaeWithMembershipFactory()
        user = siae.members.first()
        user_info = UserInfo(
            user=user, kind=KIND_SIAE_STAFF, prescriber_organization=None, is_authorized_prescriber=False, siae=siae
        )

        eligibility = EligibilityDiagnosis.create_diagnosis(job_seeker, user_info)

        self.assertEqual(eligibility.job_seeker, job_seeker)
        self.assertEqual(eligibility.author, user)
        self.assertEqual(eligibility.author_kind, KIND_SIAE_STAFF)
        self.assertEqual(eligibility.author_siae, siae)
        self.assertEqual(eligibility.author_prescriber_organization, None)


class AdministrativeCriteriaModelTest(TestCase):
    def test_levels_queryset(self):

        level1_criterion = AdministrativeCriteria.objects.filter(level=AdministrativeCriteria.Level.LEVEL_1).first()
        level2_criterion = AdministrativeCriteria.objects.filter(level=AdministrativeCriteria.Level.LEVEL_2).first()

        qs = AdministrativeCriteria.objects.level1()
        self.assertIn(level1_criterion, qs)
        self.assertNotIn(level2_criterion, qs)

        qs = AdministrativeCriteria.objects.level2()
        self.assertIn(level2_criterion, qs)
        self.assertNotIn(level1_criterion, qs)
