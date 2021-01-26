from django.core import mail
from django.test import TestCase

from itou.job_applications.factories import JobApplicationFactory
from itou.job_applications.notifications import NewJobApplicationSiaeEmailNotification
from itou.siaes.factories import SiaeWith2MembershipsFactory


class NotificationsBaseClassTest(TestCase):
    # Use a child class to test parent class. Maybe refactor that later.

    def setUp(self):
        self.siae = SiaeWith2MembershipsFactory()
        self.job_application = JobApplicationFactory(to_siae=self.siae)
        self.notification = NewJobApplicationSiaeEmailNotification(job_application=self.job_application)

        # Make sure notifications are empty
        self.siaemembership_set = self.siae.siaemembership_set
        self.membership = self.siaemembership_set.first()
        self.assertFalse(self.membership.notifications)

    # Subscribe
    def test_subscribe(self):
        self.notification.subscribe(recipient=self.membership)

        # Dict is not empty
        self.assertTrue(self.membership.notifications)

        # Key exists
        key = self.notification.name
        self.assertTrue(self.membership.notifications.get(key))

        # Test method
        self.assertTrue(self.notification.is_subscribed(recipient=self.membership))

    # Unsubscribe
    def test_unsubscribe(self):
        self.notification.unsubscribe(recipient=self.membership)

        # Dict is not empty
        self.assertTrue(self.membership.notifications)

        # Key exists
        key = self.notification.name
        self.assertTrue(self.membership.notifications.get(key))

        # Test method
        self.assertFalse(self.notification.is_subscribed(recipient=self.membership))

    def test_subscribe_unset_recipients(self):
        """
        By default, notification preferences are not stored.
        We may want to retrieve unset members and subscribe them.
        """
        self.notification._subscribe_unset_recipients()

        for membership in self.siaemembership_set.all():
            self.assertTrue(self.notification.is_subscribed(recipient=membership))

    def test_recipients_email(self):
        recipients_emails = self.notification.recipients_emails
        self.assertEqual(
            self.siaemembership_set.filter(user__email__in=recipients_emails).count(), len(recipients_emails)
        )

    def test_get_recipients_default_send_to_all(self):
        # Unset recipients are present in get_recipients if SEND_TO_UNSET_RECIPIENTS = True
        recipients = self.notification.get_recipients()
        self.assertEqual(self.siaemembership_set.count(), len(recipients))

    def test_get_recipients_default_dont_send_to_all(self):
        # Unset recipients are not present in get_recipients if SEND_TO_UNSET_RECIPIENTS = False
        self.notification.SEND_TO_UNSET_RECIPIENTS = False
        recipients = self.notification.get_recipients()
        self.assertEqual(len(recipients), 0)

    def test_send(self):
        self.notification.send()

        receivers = [receiver for message in mail.outbox for receiver in message.to]
        self.assertEqual(self.notification.email.to, receivers)