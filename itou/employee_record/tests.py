import json
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase

from itou.employee_record.factories import EmployeeRecordFactory
from itou.employee_record.management.commands.transfer_employee_records import Command
from itou.employee_record.mocks.transfer_employee_records import (
    SFTPBadConnectionMock,
    SFTPConnectionMock,
    SFTPEvilConnectionMock,
    SFTPGoodConnectionMock,
)
from itou.employee_record.models import EmployeeRecord, EmployeeRecordBatch, validate_asp_batch_filename
from itou.job_applications.factories import (
    JobApplicationWithApprovalFactory,
    JobApplicationWithApprovalNotCancellableFactory,
    JobApplicationWithCompleteJobSeekerProfileFactory,
    JobApplicationWithJobSeekerProfileFactory,
    JobApplicationWithoutApprovalFactory,
)
from itou.job_applications.models import JobApplicationWorkflow
from itou.utils.mocks.address_format import mock_get_geocoding_data


class EmployeeRecordModelTest(TestCase):

    fixtures = ["test_INSEE_communes.json"]

    def setUp(self):
        self.employee_record = EmployeeRecordFactory()

    def test_creation_from_job_application(self):
        """
        Employee record objects are created from a job application giving them access to:
        - user / job seeker
        - job seeker profile
        - approval

        Creation is defensive, expect ValidationError if out of the lane
        """
        # Creation with invalid job application state
        with self.assertRaises(AssertionError):
            employee_record = EmployeeRecord.from_job_application(None)

        # Job application is not accepted
        with self.assertRaisesMessage(ValidationError, EmployeeRecord.ERROR_JOB_APPLICATION_MUST_BE_ACCEPTED):
            job_application = JobApplicationWithApprovalFactory(state=JobApplicationWorkflow.STATE_NEW)
            employee_record = EmployeeRecord.from_job_application(job_application)

        # Job application can be cancelled
        with self.assertRaisesMessage(ValidationError, EmployeeRecord.ERROR_JOB_APPLICATION_TOO_RECENT):
            job_application = JobApplicationWithApprovalFactory(state=JobApplicationWorkflow.STATE_ACCEPTED)
            employee_record = EmployeeRecord.from_job_application(job_application)

        # Job application has no approval
        with self.assertRaisesMessage(ValidationError, EmployeeRecord.ERROR_JOB_APPLICATION_WITHOUT_APPROVAL):
            job_application = JobApplicationWithoutApprovalFactory()
            employee_record = EmployeeRecord.from_job_application(job_application)

        # Job application is duplicated (already existing with same approval and SIAE)
        job_application = JobApplicationWithCompleteJobSeekerProfileFactory()

        # Must be ok
        EmployeeRecord.from_job_application(job_application).save()

        with self.assertRaisesMessage(ValidationError, EmployeeRecord.ERROR_EMPLOYEE_RECORD_IS_DUPLICATE):
            # Must not
            employee_record = EmployeeRecord.from_job_application(job_application)

        # Job seeker has no existing profile (must be filled before creation)
        with self.assertRaisesMessage(ValidationError, EmployeeRecord.ERROR_JOB_SEEKER_HAS_NO_PROFILE):
            job_application = JobApplicationWithApprovalNotCancellableFactory()
            employee_record = EmployeeRecord.from_job_application(job_application)

        # Job seeker has an incomplete profile
        with self.assertRaises(ValidationError):
            # Message checked in profile tests
            job_application = JobApplicationWithJobSeekerProfileFactory()
            employee_record = EmployeeRecord.from_job_application(job_application)

        # Standard / normal case
        job_application = JobApplicationWithCompleteJobSeekerProfileFactory()
        employee_record = EmployeeRecord.from_job_application(job_application)
        self.assertIsNotNone(employee_record)

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_prepare_successful(self, _mock):
        """
        Mainly format the job seeker address to Hexa format
        """
        job_application = JobApplicationWithCompleteJobSeekerProfileFactory()
        employee_record = EmployeeRecord.from_job_application(job_application)
        employee_record.update_as_ready()

        job_seeker = job_application.job_seeker
        self.assertIsNotNone(job_seeker.jobseeker_profile)

        # Surface check, this is not a job seeker profile test
        profile = job_seeker.jobseeker_profile
        self.assertIsNotNone(profile.hexa_commune)

    def test_prepare_failed_geoloc(self):
        """
        Test the failure of employee record preparation

        Mainly caused by:
        - geoloc issues (no API mock on this test)
        """
        # Complete profile, but geoloc API not reachable
        job_application = JobApplicationWithCompleteJobSeekerProfileFactory()

        with self.assertRaises(ValidationError):
            employee_record = EmployeeRecord.from_job_application(job_application)
            employee_record.update_as_ready()

    def test_batch_filename_validator(self):
        """
        Check format of ASP batch file name
        """
        with self.assertRaises(ValidationError):
            validate_asp_batch_filename(None)

        with self.assertRaises(ValidationError):
            validate_asp_batch_filename("xyz")

        with self.assertRaises(ValidationError):
            validate_asp_batch_filename("RiAE_20210410130000.json")

        validate_asp_batch_filename("RIAE_FS_20210410130000.json")

    def test_find_by_batch(self):
        """
        How to find employee records given their ASP batch file name and line number ?
        """
        filename = "RIAE_FS_20210410130000.json"
        employee_record = EmployeeRecordFactory(asp_batch_file=filename, asp_batch_line_number=2)

        self.assertEqual(EmployeeRecord.objects.find_by_batch("X", 3).count(), 0)
        self.assertEqual(EmployeeRecord.objects.find_by_batch(filename, 3).count(), 0)
        self.assertEqual(EmployeeRecord.objects.find_by_batch("X", 2).count(), 0)

        result = EmployeeRecord.objects.find_by_batch(filename, 2).first()

        self.assertEqual(result.id, employee_record.id)


class EmployeeRecordBatchTest(TestCase):
    """
    Misc tests on batch wrapper level
    """

    def test_format_feedback_filename(self):
        with self.assertRaises(ValidationError):
            EmployeeRecordBatch.feedback_filename("test.json")

        self.assertEquals(
            "RIAE_FS_20210410130000_FichierRetour.json",
            EmployeeRecordBatch.feedback_filename("RIAE_FS_20210410130000.json"),
        )

    def test_batch_filename_from_feedback(self):
        with self.assertRaises(ValidationError):
            EmployeeRecordBatch.batch_filename_from_feedback("test.json")

        self.assertEqual(
            "RIAE_FS_20210410130000.json",
            EmployeeRecordBatch.batch_filename_from_feedback("RIAE_FS_20210410130000_FichierRetour.json"),
        )


class EmployeeRecordLifeCycleTest(TestCase):
    """
    Note: employee records status is never changed manually
    """

    fixtures = ["test_INSEE_communes.json"]

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def setUp(self, mock):
        job_application = JobApplicationWithCompleteJobSeekerProfileFactory()
        employee_record = EmployeeRecord.from_job_application(job_application)
        self.employee_record = employee_record
        self.employee_record.update_as_ready()

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_state_ready(self, _mock):
        self.assertEqual(self.employee_record.status, EmployeeRecord.Status.READY)

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_state_sent(self, _mock):
        filename = "RIAE_FS_20210410130000.json"
        self.employee_record.update_as_sent(filename, 1)

        self.assertEqual(filename, self.employee_record.asp_batch_file)
        self.assertEqual(self.employee_record.status, EmployeeRecord.Status.SENT)

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_state_rejected(self, _mock):
        filename = "RIAE_FS_20210410130001.json"
        self.employee_record.update_as_sent(filename, 1)

        err_code, err_message = "12", "JSON Invalide"

        self.employee_record.update_as_rejected(err_code, err_message)
        self.assertEqual(self.employee_record.status, EmployeeRecord.Status.REJECTED)
        self.assertEqual(self.employee_record.asp_processing_code, err_code)
        self.assertEqual(self.employee_record.asp_processing_label, err_message)

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_state_accepted(self, _mock):
        filename = "RIAE_FS_20210410130001.json"
        self.employee_record.update_as_sent(filename, 1)

        process_code, process_message = "0000", "La ligne de la fiche salarié a été enregistrée avec succès."
        self.employee_record.update_as_accepted(process_code, process_message, "{}")

        self.assertEqual(self.employee_record.status, EmployeeRecord.Status.PROCESSED)
        self.assertEqual(self.employee_record.asp_processing_code, process_code)
        self.assertEqual(self.employee_record.asp_processing_label, process_message)


class EmployeeRecordManagementCommandTest(TestCase):
    """
    Employee record management command, testing:
    - mocked sftp connection
    - basic upload / download modes
    - ...
    """

    fixtures = ["test_INSEE_communes.json", "test_asp_INSEE_countries.json"]

    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def setUp(self, _mock):
        job_application = JobApplicationWithCompleteJobSeekerProfileFactory()
        employee_record = EmployeeRecord.from_job_application(job_application)
        employee_record.update_as_ready()

        self.employee_record = employee_record
        self.job_application = job_application

    @mock.patch("pysftp.Connection", SFTPConnectionMock)
    def test_smoke_download(self):
        command = Command()
        command.handle(download=True)

    @mock.patch("pysftp.Connection", SFTPConnectionMock)
    def test_smoke_upload(self):
        command = Command()
        command.handle(upload=True)

    @mock.patch("pysftp.Connection", SFTPConnectionMock)
    def test_smoke_download_and_upload(self):
        command = Command()
        command.handle()

    @mock.patch("pysftp.Connection", SFTPGoodConnectionMock)
    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_dryrun_upload(self, _mock):
        employee_record = self.employee_record

        # Upload with dry run
        command = Command()
        command.handle(upload=True, dryrun=True)

        # Then download "for real", should work but leave
        # employee record untouched
        command.handle(upload=False, download=True)

        self.assertEqual(employee_record.status, EmployeeRecord.Status.READY)

    @mock.patch("pysftp.Connection", SFTPGoodConnectionMock)
    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_dryrun_download(self, _mock):
        employee_record = self.employee_record

        # Upload "for real"
        command = Command()
        command.handle(upload=True)

        # Then download dry run, should work but leave
        # employee record untouched
        command.handle(upload=False, download=True, dryrun=True)

        self.assertEqual(employee_record.status, EmployeeRecord.Status.READY)

    @mock.patch("pysftp.Connection", SFTPBadConnectionMock)
    def test_upload_failure(self):
        employee_record = self.employee_record
        command = Command()
        with self.assertRaises(Exception):
            command.handle(upload=True)

        self.assertEqual(employee_record.status, EmployeeRecord.Status.READY)

    @mock.patch("pysftp.Connection", SFTPBadConnectionMock)
    def test_download_failure(self):
        employee_record = self.employee_record
        command = Command()
        with self.assertRaises(Exception):
            command.handle(download=True)

        self.assertEqual(employee_record.status, EmployeeRecord.Status.READY)

    @mock.patch("pysftp.Connection", SFTPGoodConnectionMock)
    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_upload_and_download_success(self, _mock):
        """
        - Create an employee record
        - Send it to ASP
        - Get feedback
        - Update employee record
        """
        employee_record = self.employee_record

        command = Command()
        command.handle(upload=True, download=False)
        employee_record.refresh_from_db()

        self.assertEqual(employee_record.status, EmployeeRecord.Status.SENT)
        self.assertEqual(employee_record.batch_line_number, 1)
        self.assertIsNotNone(employee_record.asp_batch_file)

        command.handle(upload=False, download=True)
        employee_record.refresh_from_db()

        self.assertEqual(employee_record.status, EmployeeRecord.Status.PROCESSED)
        self.assertEqual(employee_record.asp_processing_code, "0000")

    @mock.patch("pysftp.Connection", SFTPGoodConnectionMock)
    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_employee_record_archive(self, _mock):
        """
        Check that "proof" of validated employee record is OK
        """
        employee_record = self.employee_record

        command = Command()
        command.handle()
        employee_record.refresh_from_db()

        self.assertIsNotNone(employee_record.archived_json)

        employee_record_json = json.loads(employee_record.archived_json)

        self.assertEqual("0000", employee_record_json.get("codeTraitement"))
        self.assertIsNotNone(employee_record_json.get("libelleTraitement"))

    @mock.patch("pysftp.Connection", SFTPEvilConnectionMock)
    @mock.patch(
        "itou.utils.address.format.get_geocoding_data",
        side_effect=mock_get_geocoding_data,
    )
    def test_random_connection_failure(self, _mock):
        employee_record = self.employee_record

        # Randowm upload failure
        for _ in range(10):
            command = Command()
            with self.assertRaises(Exception):
                command.handle(upload=True, download=False)

        # Employee record must be in the same status
        employee_record.refresh_from_db()
        self.assertEqual(employee_record.status, EmployeeRecord.Status.READY)

        for _ in range(10):
            command = Command()
            with self.assertRaises(Exception):
                command.handle(upload=False, download=True)

        employee_record.refresh_from_db()
        self.assertEqual(employee_record.status, EmployeeRecord.Status.READY)
