import urllib, re, time, simplejson as json

import defaults

class FanFeedrException(Exception):
    """
    Generic exception for the FanFeedr API
    """
    pass

class FanFeedrNotFoundException(Exception):
    """
    Resource wasn't found, raise exception
    """
    pass

class FanFeedrCallException(Exception):
    """
    Exception generated by an error being thrown in the actual
    request to the API server (not in the SDK)
    """

    def __init__(self, data):
        error = re.match(r".*<h1>(\d{3})(.+)</h1>.*", data)
        if error:
            self.code = int(error.group(1))
            self.msg = error.group(2).strip()
        else:
            self.code = None
            self.msg = data

    def __str__(self):
        return "FanFeedrCallException with response from server: %s" % self.msg

    def __repr__(self):
        return "FanFeedrCallException with response from server: %s" % self.msg

class FanFeedrAPI(object):
    """
    Wrapper for the FanFeedr REST API v1.
    Documentation available at http://developer.fanfeedr.com/
    """

    def __init__(self, fanfeedr_key, tier=defaults.TIER,
                 base_url=defaults.FANFEEDR_BASE):
        """
        Initialize setup for requests made to the
        Fanfeedr API

        tier is one of basic|bronze|silver|gold depending on
        your key
        """
        self.FANFEEDR_BASE = base_url + tier
        self.FANFEEDR_KEY = fanfeedr_key

    def _make_request(self, path, request_number=1):
        """
        Makes a request the FanFeedrAPI, massages the data back into
        a proper Python dict.

        Example url:
        http://
        """
        url = "http://%s/api/%s?api_key=%s" % (self.FANFEEDR_BASE, path, self.FANFEEDR_KEY)
        f = urllib.urlopen(url)
        if f.getcode() == 404:
            raise FanFeedrNotFoundException()
        data = f.read()
        try:
            return json.loads(data)
        except:
            #Error handling, retry if there's a query per second overage
            exception = FanFeedrCallException(data)
            if exception.code == 403 and "Qps" in exception.msg:
                #Over queries per second, try again in .1 seconds
                if request_number < 3:
                    time.sleep(.1)
                    return self._make_request(path, request_number=request_number+1)
                else:
                    raise exception
            else:
                raise exception


    def get_resource(self, rtype, uid):
        """
        Loads the resource of type rtype with uid
        Ex:
         ffapi.get_resource('teams', 'this-is-a-uuid')
        """

        return self._make_request("%s/%s" % (rtype, uid))

    def get_collection(self, rtype, ptype=None, puid=None):
        """
        Gets base collection for resource rtype, with
        optional parent resource of type ptype with uid puid
        Ex:
         ffapi.get_resource('teams', 'divisions', 'this-is-the-division-uuid')
        """

        if ptype and not puid:
            raise FanFeedrException("Parent resource specified, "
                                    "but no UUID was included")
        if puid and not ptype:
            raise FanFeedrException("Parent uuid was specified, "
                                    "but no UUID was included")
        path = rtype
        if ptype and puid:
            path = "%s/%s/%s" % (ptype, puid, rtype)
        return self._make_request(path)

    def get_collection_method(self, method, rtype, ptype=None, puid=None):
        """
        Call to a method for a collection resource (like /content/blog)
        Ex:
         ffapi.get_collection_method('blog', 'content', 'teams', 'this-is-a-team-uuid')
        """

        if ptype and not puid:
            raise FanFeedrException("Parent resource specified, "
                                    "but no UUID was included")
        if puid and not ptype:
            raise FanFeedrException("Parent uuid was specified, "
                                    "but no UUID was included")
        path = "%s/%s" % (rtype, method)
        if ptype and puid:
            path = "%s/%s/%s" % (ptype, puid, path)
        return self._make_request(path)

    def get_resource_method(self, method, rtype, uid):
        """
        Call to a method for an individual resource
        Ex:
         ffapi.get_collection_method('related', 'content', 'article-uid')
        """

        path = "%s/%s/%s" % (rtype, uid, method)
        return self._make_request(path)
