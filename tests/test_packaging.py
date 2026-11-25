"""Keep package metadata and installation inputs from drifting apart."""
import ast
from pathlib import Path
import tomllib
import unittest


class PackagingTests(unittest.TestCase):
    def test_metadata_has_one_owner_and_does_not_package_tests(self):
        root = Path(__file__).resolve().parents[1]
        data = tomllib.loads((root / 'pyproject.toml').read_text())
        self.assertFalse((root / 'setup.py').exists(), 'Duplicate setup metadata must be removed')
        self.assertEqual((root / 'requirements.txt').read_text().strip(), '.')
        self.assertIn('version', data['project']['dynamic'])
        self.assertEqual(data['tool']['setuptools']['packages']['find']['include'], ['producer_toolkit*'])
        version = ast.literal_eval(ast.parse((root / 'producer_toolkit' / '__init__.py').read_text()).body[1].value)
        self.assertTrue(version)
