import helper
import unittest
from datetime import datetime, timedelta
import pytz

# today = datetime.now(pytz.timezone('US/Pacific'))
# datetime stamps are in UTC in application

today = datetime.now()
today_day = today.day
yesterday = today.replace(day=(today_day-1))
tomorrow = today.replace(day=(today_day+1))
last_week = today - timedelta(days=8)

class DateTimeTestCases(unittest.TestCase):
	""" unit tests for DateTime helpers """

	def test_dates_same_1(self):
		self.assertEqual(helper.dates_same(yesterday, today, 'US/Pacific'), False)
	
	def test_dates_same_2(self):
		self.assertEqual(helper.dates_same(today, today, 'US/Pacific'), True)

	def dates_consecutive_1(self):
		self.assertEqual(helper.dates_consecutive(yesterday, today, 'US/Pacific'), True)

	def dates_consecutive_2(self):
		self.assertEqual(helper.dates_consecutive(yesterday, tomorrow, 'US/Pacific'), False)

	def dates_same_or_consecutive_1(self):
		self.assertEqual(helper.dates_same_or_consecutive(yesterday, today, 'US/Pacific'), True)

	def dates_same_or_consecutive_2(self):
		self.assertEqual(helper.dates_same_or_consecutive(today, today, 'US/Pacific'), True)

	def dates_same_or_consecutive_3(self):
		self.assertEqual(helper.dates_same_or_consecutive(last_week, today, 'US/Pacific'), False)

	def dates_week_apart_1(self):
		self.assertEqual(helper.dates_week_apart(last_week, today, 'US/Pacific'), True)

	def dates_week_apart_2(self):
		self.assertEqual(helper.dates_week_apart(yesterday, today, 'US/Pacific'), False)


class CountryTimeZoneCases(unittest.TestCase):
	""" unit tests for Country and Timezone helpers """

	def test_format_mobile(self):
		self.assertEqual(helper.format_mobile("8028253271", 'US'), "+1 802-825-3271")


if __name__ == '__main__':
	unittest.main()