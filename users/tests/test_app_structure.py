"""
Test suite for validating Django app structure and configuration.

This module tests that all required apps are properly installed and
can be loaded by Django's app registry.
"""

import unittest
from django.test import TestCase
from django.apps import apps
from django.conf import settings


class AppStructureTestCase(TestCase):
    """Test case for validating Django app structure and installation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.required_apps = [
            'users',
            'academics',
            'students',
            'faculty',
            'attendance',
            'exams',
            'communication'
        ]
    
    def test_all_apps_in_installed_apps(self):
        """Test that all required apps are listed in INSTALLED_APPS."""
        installed_apps = settings.INSTALLED_APPS
        
        for app_name in self.required_apps:
            with self.subTest(app=app_name):
                self.assertIn(
                    app_name,
                    installed_apps,
                    f"App '{app_name}' is not in INSTALLED_APPS"
                )
    
    def test_all_apps_can_be_loaded(self):
        """Test that all required apps can be loaded by Django's app registry."""
        for app_name in self.required_apps:
            with self.subTest(app=app_name):
                try:
                    app_config = apps.get_app_config(app_name)
                    self.assertIsNotNone(
                        app_config,
                        f"App '{app_name}' could not be loaded from registry"
                    )
                    self.assertEqual(
                        app_config.name,
                        app_name,
                        f"App config name mismatch for '{app_name}'"
                    )
                except LookupError:
                    self.fail(f"App '{app_name}' not found in Django app registry")
    
    def test_app_configs_have_correct_attributes(self):
        """Test that app configurations have the required attributes."""
        for app_name in self.required_apps:
            with self.subTest(app=app_name):
                try:
                    app_config = apps.get_app_config(app_name)
                    
                    # Test that app has a name
                    self.assertTrue(
                        hasattr(app_config, 'name'),
                        f"App '{app_name}' config missing 'name' attribute"
                    )
                    
                    # Test that app has a label
                    self.assertTrue(
                        hasattr(app_config, 'label'),
                        f"App '{app_name}' config missing 'label' attribute"
                    )
                    
                    # Test that app has a path
                    self.assertTrue(
                        hasattr(app_config, 'path'),
                        f"App '{app_name}' config missing 'path' attribute"
                    )
                    
                except LookupError:
                    self.fail(f"App '{app_name}' not found in Django app registry")
    
    def test_no_duplicate_app_labels(self):
        """Test that there are no duplicate app labels in the registry."""
        app_labels = []
        
        for app_name in self.required_apps:
            try:
                app_config = apps.get_app_config(app_name)
                app_labels.append(app_config.label)
            except LookupError:
                self.fail(f"App '{app_name}' not found in Django app registry")
        
        # Check for duplicates
        unique_labels = set(app_labels)
        self.assertEqual(
            len(app_labels),
            len(unique_labels),
            f"Duplicate app labels found: {app_labels}"
        )
    
    def test_apps_are_ready(self):
        """Test that all apps are properly initialized and ready."""
        self.assertTrue(
            apps.ready,
            "Django apps registry is not ready"
        )
        
        for app_name in self.required_apps:
            with self.subTest(app=app_name):
                try:
                    app_config = apps.get_app_config(app_name)
                    # If we can get the app config without error, it's ready
                    self.assertIsNotNone(app_config)
                except LookupError:
                    self.fail(f"App '{app_name}' not ready or not found")


if __name__ == '__main__':
    unittest.main()