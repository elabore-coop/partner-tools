# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

#@tagged('-standard', '-at_install', 'post_install', 'partner_profiles')
@tagged('-standard', 'post_install', 'partner_profiles')
class TestPartner(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestPartner, self).setUp(*args, **kwargs)
        # Individual partner creation
        values1 = {
            'name': 'partnerTest1',
            'is_company': False,
        }
        self.test_partner1 = self.env['res.partner'].create(values1)
        # Company partner creation
        values2 = {
            'name': 'partnerTest2',
            'is_company': True,
        }
        self.test_partner2 = self.env['res.partner'].create(values2)
        # Other contact creation
        values3 = {
            'name': 'partnerTest3',
            'is_company': False,
            'type': 'other',
        }
        self.test_partner3 = self.env['res.partner'].create(values3)

    def test_main_profile(self):
        """Check the main profile content"""
        # PARTNER 1
        # Test partner's type is 'contact'
        self.assertEqual(self.test_partner1.type, "contact")
        # # Test partner's profile is Main
        self.assertEqual(self.test_partner1.partner_profile.ref, "partner_profile_main")
        # # Test partner's profile booleans '
        # self.assertTrue(self.test_partner1.is_main_profile)
        # self.assertFalse(self.test_partner1.is_public_profile)
        # self.assertFalse(self.test_partner1.is_position_profile)

        # PARTNER 2
        # Test partner's type is 'contact'
        self.assertEqual(self.test_partner2.type, "contact")
        # # Test partner's profile is Main
        # self.assertEqual(self.test_partner2.partner_profile.ref, "partner_profile_main")
        # # Test partner's profile booleans '
        # self.assertTrue(self.test_partner2.is_main_profile)
        # self.assertFalse(self.test_partner2.is_public_profile)
        # self.assertFalse(self.test_partner2.is_position_profile)

        # PARTNER 3
        # Test partner's type is 'other'
        self.assertEqual(self.test_partner3.type, "other")
        # # Test partner's profile is None
        # self.assertEqual(self.test_partner3.partner_profile, None)
        # # Test partner's profile booleans '
        # self.assertFalse(self.test_partner3.is_main_profile)
        # self.assertFalse(self.test_partner3.is_public_profile)
        # self.assertFalse(self.test_partner3.is_position_profile)


    # def test_public_profile(self):
    #     """ Check the public profile creation"""
    #     # Test public profile is created
    #     self.assertEqual(True,True) 
    #     # Test public profile's name is equal to the main profile's name
    #     self.assertEqual(True,True) 