import types
import json
from cStringIO import StringIO

# TODO: make this an interface
class WebserviceImplementationBase(object):
    """
    Adapter class to connect the webservice application with the implementation.
    This class needs to be subclassed and the *_impl() methods need to be redefined.
    For an example see :py:class:`etoxwsapi.sampleimpl.ws_impl_v2.WS2`
    """
    def __init__(self):
        pass

    def info_impl(self):
        """
        Concrete implementations need to return a ws_info JSON object
        """
        raise NotImplementedError("must be implemented by subclass")
    def info(self):
        return self.info_impl()

    def dir_impl(self):
        """
        Needs to return an array of calculation_info JSON objects
        """
        raise NotImplementedError("must be implemented by subclass")
    def dir(self):
        retval = self.dir_impl()
        from django.conf import settings
        if settings.DEBUG:
            # also for WS with only one model we expect an list of calc_infos
            assert(isinstance(json.loads(retval), types.ListType))
        return retval

    def pmmdinfo_impl(self):
        """
        """
        info = dict()
        for t in ('PMMD name', 'PMMD status', 'Provider', 'Administrator'):
            info[t] = 'n/a'
        try:
            with open('/etc/etoxws-release', 'r') as rel_info:
                info = dict()
                for l in rel_info:
                    try:
                        t = l.split(':', 1)
                        info[t[0].strip()] = t[1].strip()
                    except:
                        pass
        except Exception, e:
            print e
        return json.dumps(info) 

    def pmmdinfo(self):
        return self.pmmdinfo_impl()

    def _nrecord(self, sdf_file):
        nrec = 0
        for line in StringIO(sdf_file):
            if line[0] == 'M' and line.startswith("M  END"):
                nrec += 1
        return nrec

    def calculate_impl(self, jobobserver, calc_info, sdf_file):
        """
        Implements the calculation. Use the jobobserver to report calculation progress,
        submit results and issue logging messages.
        """
        raise NotImplementedError("must be implemented by subclass")

    # calculate is now a celery task consuming calculate_impl
#	def calculate(self, job_id, calc_info, sdf_file, logger, lock):


