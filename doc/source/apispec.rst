API Specification
=================

REST Interface
--------------

Webservice information
~~~~~~~~~~~~~~~~~~~~~~

============== ========= ========================================= =========================================== =================
URL            HTTP verb input data                                return data (mime-type: json schema)        HTTP status codes
============== ========= ========================================= =========================================== =================
/info          GET       \-                                        application/json: ws_info_
/dir           GET       \-                                        application/json: array of
                                                                   calculation_info_ objects
============== ========= ========================================= =========================================== =================

Job Management
~~~~~~~~~~~~~~
============== ========= ========================================= =========================================== =================
URL            HTTP verb input data                                return data (mime-type: json schema)        HTTP status codes
============== ========= ========================================= =========================================== =================
/jobs/         GET       \-                                        application/json: array of <job_id> of this 200
                                                                   webservice 200
/jobs/         POST      calculation_request                       application/json: array of job_status_      200, 400
                                                                   objects
/jobs/<job_id> GET       <job_id>: request info for job_id         application/json: job_status_ object        200, 404 
/jobs/<job_id> DELETE    <job_id>: job to be deleted               \-                                          200, 404, 500
============== ========= ========================================= =========================================== =================


Data Types
----------

.. include:: ../build/data_types.rst

