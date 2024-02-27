import logging

_logger = logging.getLogger(__name__)

try:
    import phonenumbers

    def get_country_from_phone_number(number):
        try:
            number = phonenumbers.parse(number)
            return phonenumbers.region_code_for_number(number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False

except ImportError:

    def get_country_from_phone_number(number):
        global _phonenumbers_lib_warning
        if not _phonenumbers_lib_warning:
            _logger.info(
                "The `phonenumbers` Python module is not installed, contact numbers will not be "
                "verified. Please install the `phonenumbers` Python module."
            )
            _phonenumbers_lib_warning = True
        return number