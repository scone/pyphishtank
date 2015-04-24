# Copyright (c) 2015 Samuel Cleveland
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Simple phishtank api.
"""

__docformat__ = 'restructuredtext'
__author__ = "Samuel Cleveland"
__version__ = '1.0.0'
__license__ = 'MIT License'

import datetime
import requests



class PhishTankError(Exception):
    """
    Exception for PhishTank errors.
    """
    pass
    
class PhishTankAPILimitExceeded(Exception):
    """
    Exception for exceeding the PhishTank API limit.
    """
    pass

class PhishTankAPILimitReached(Exception):
    """
    Exception when the PhishTank API limit is reached.
    """
    pass

class Result():
    """
    Result sent back from PhishTank.
    """

    # Slots for memory
    __slots__ = [
        'url', 'in_database', 'phish_id', 'phish_detail_page',
        'verified', 'verified_at', 'valid', 'submitted_at']

    def __init__(self, response):
        """
        Creates an instance of a response.

        :Parameters:
           - `response`: actual json response from the service
        """
        self.url = response.get('url', None)
        self.in_database = response.get('in_database', None)
        self.phish_id = response.get('phish_id', None)
        self.phish_detail_page = response.get('phish_detail_page', None)
        self.verified = response.get('verified', None)
        self.verified_at = response.get('verified_at', None)
        if self.verified_at:
            self.verified_at = self.__force_date(self.verified_at)
        self.valid = response.get('valid', None)
        self.submitted_at = response.get('submitted_at', None)
        if self.submitted_at:
            self.submitted_at = self.__force_date(self.submitted_at)

    def __force_date(self, date_str):
        """
        Forces a date string into a datetime object.

        :Parameters:
           - `date_str`: the date string in %Y-%m-%dT%H:%M:%S+00:00 format.
        """
        return datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S+00:00')

    def __unsafe(self):
        """
        Returns back True if known to be unsafe, False otherwise.
        """
        if self.valid:
            return True
        return False

    def __repr__(self):
        """
        Representation of thie object.
        """
        return "<Result: url=%s, unsafe=%s>" % (self.url, self.unsafe)

    def __eq__(self, other):
        """
        Checks to see if this instance is the same as another.

        :Parameters:
           - `other`: The other instance to look at.
        """
        for key in self.__slots__:
            try:
                if getattr(self, key) != getattr(other, key):
                    raise KeyError()
            except:
                return False
        return True

    def report(self):
        """
        **DEPRECATED**

        Old method which uses the internal data to return a report in
        string format. Use .result instead..
        """
        import warnings
        warnings.warn('report is deprecated. Please use result.')
        return self.result

    def __result(self):
        """
        Uses the internal data to return a report in string format.
        """
        formatted_string = ""
        for item in self.__slots__:
            if getattr(self, item):
                formatted_string += "%s: %s\n" % (item, getattr(self, item))
        formatted_string += "unsafe: %s" % self.unsafe
        return formatted_string

    # Aliases
    __str__ = __result
    unicode = __result

    # Properties
    unsafe = property(__unsafe)
    result = property(__result)


class PhishTank():
    """
    PhishTank abstraction class.
    """

    __apikey = ''
    _requests_available = 50
    _requests_made = 0

    def __init__(self, api_url='http://checkurl.phishtank.com/checkurl/', apikey=None):
        """
        Create an instance of the API caller.

        :Parameters:
           - `apikey`: optional apikey to use in calls
        """
        self.__apikey = apikey
        self._api_url = api_url
        
    def requests_left(self):
        """Check if API request limit has been reached."""
        if self._requests > 0:
            return True
        else:
            return False

    def check(self, url):
        """
        Check a URL.

        :Parameters:
           - `url`: url to check with PhishTank
        """
        post_data = {
            'url': url,
            'format': 'json',
            'app_key': self.__apikey,
        }
    
        response = requests.post(self._api_url, data=post_data)
        self._requests_made = response.headers.get('X-Request-Count', 0)
        self._requests_available = response.headers.get('X-Request-Limit', 50)
        
    
        if response.status_code == 509:
            request_interval = response.headers.get("X-Request-Limit-Interval", 300)
            raise PhishTankAPILimitExceeded(request_interval)
                
        data = response.json()

        if 'errortext' in data.keys():
            raise PhishTankError(data['errortext'])
        return Result(data['results'])
