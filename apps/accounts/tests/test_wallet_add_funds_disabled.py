from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import UserProfile, UserWallet


class WalletAddFundsDisabledTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="walletuser", email="wallet@test.com", password="pass"
        )
        UserProfile.objects.create(user=self.user, user_type="parent")
        self.wallet = UserWallet.objects.create(user=self.user, balance=Decimal("0.00"))

    def test_add_funds_endpoint_does_not_change_balance(self):
        self.client.force_login(self.user)
        before = UserWallet.objects.get(pk=self.wallet.pk).balance
        resp = self.client.post(
            reverse("accounts:wallet_add_funds"),
            data={"amount": "50.00", "description": "test"},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        after = UserWallet.objects.get(pk=self.wallet.pk).balance
        self.assertEqual(after, before)


