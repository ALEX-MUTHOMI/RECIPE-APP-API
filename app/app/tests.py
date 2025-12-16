"""
Sample tests
"""
from django.test import SimpleTestCase

from app import calc  # <--- Only this import is needed

class CalcTests(SimpleTestCase):
    """Test the calc module"""

    def test_add_numbers(self):
        """Test that two numbers are added together"""
        res = calc.add(5, 6)
        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """Test that values are subtracted and returned"""
        # 1. Fixed spelling (subtract)
        res = calc.subtract(10, 8)
        
        # 2. Fixed assertion (Added 'res')
        self.assertEqual(res, 2)