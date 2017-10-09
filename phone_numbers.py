from phone_iso3166.country import phone_country
import phonenumbers
import pycountry
import time
import datetime
import arrow
import pytz
from pytz import common_timezones
import timezones
from phonenumbers import timezone
import pendulum


# trying out phonenumbers

us_number = phonenumbers.parse('+18028253270', "US")
# phone number object w/format:
# PhoneNumber(country_code=1, national_number=8028253270, extension=None, italian_leading_zero=None, number_of_leading_zeros=None, country_code_source=0, preferred_domestic_carrier_code=None)

timezone.time_zones_for_number(US_number)
# returns ('America/New_york',)

phonenumbers.format_number(us_number, phonenumbers.PhoneNumberFormat.NATIONAL)
# returns (802) 825-3270

phonenumbers.format_number(us_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
# returns '+1 802-825-3270'

y = phonenumbers.parse("020 8366 1177", "GB")
# reutnrs: PhoneNumber(country_code=44, national_number=2083661177, extension=None, italian_leading_zero=None, number_of_leading_zeros=None, country_code_source=0, preferred_domestic_carrier_code=None)

# trying out pycountry

# 249 countries in pycountry.countries

for country in pycountry.countries:
    print country.alpha_2
    print country.name


# can format a drop down with display vales of name and values as alpha_2
# habot can then take anything the user puts into the field and create a phonenumbers object to accurately store information

