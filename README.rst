dj-api-auth
===========
**dj-api-auth** is a Django application, providing an AWS-alike API auth solution.


When I was seeking a simple solution rather than intricate OAuth, I was inspired by this article 
`Designing a Secure REST (Web) API without OAuth
<http://www.thebuzzmedia.com/designing-a-secure-rest-api-without-oauth-auth/>`_.
Thanks to the author and the comments.


Features
--------
1. API key, SEC key related forms
2. Each API key can be associated with a set of API
3. API can be associated with user,  your legacy code with ``request.user`` underneath can work smoothly with ``dj-api-auth``
4. Add auth by simply put a decorator on your view.
5. Provide utility functions that can help you register APIs as assignable. Both browser-oriented views(reusing) and dedicated API-oriented views can be marked as assignable.
6. A Django command to scan and update API information to database.


How it works
------------
1. Generate a pair of API key and SEC key, assign some APIs to it. 
2. Client put API key and current UNIX time as ``apikey`` and ``timestemp`` in requestURL
3. Client also generate a ``signature`` by calculate a SHA256 value on the whole URL(without ``signature``) by its known SEC key.
4. Server side will verify 
	- is ``timestamp`` from client in reasonable drifting compare to server time.
	- is ``apikey`` from client exists
	- is the API client trying to access allowed for the ``apikey``
	- compare the ``signature`` with the one calculated on server side by same algorithm

5. if any verification failed, return 403 error with brief message


Add to your project
--------------------
1. Add ``djapiauth`` to ``INSTALLED_APPS`` in ``sttings.py``

2. There are two optional settings 

- ``API_AUTH_ALLOWED_TIME_DRIFT``
	- **optional**, set the allowed time drift between server time and the ``timestamp`` parameter in coming URL.
	- **format** : integer, unit: second
	- **default** : 300, (5 minutes) 

- ``API_AUTH_ADMIN_USER_FILTER``
	- **optional**, when creating API keys, you can assign the API key to an user, this filter is used to filter the users showing in the API key creating form.
	- **format**: dictionary, the filter parameter will be passed to ``get_user_model().objects.filter()``. e.g. ``{'name_startswith': 'admin'}``
	- **default**: {}, means all users will show in the API key creating form.

Generate/Manage API and SEC key
-------------------------------
If you have ``admin`` enabled for your project, you can find these features in ``admin`` site. Otherwise, you can import forms from ``djapiauth.forms`` or write your own form based on models in ``djapiauth.models``

Add auth for views
----------------------------
- For legacy views, we can add the auth and registration together in URL dispatching file, usually the ``urls.py``, see **Register APIs** for detail.

- For API views, simply add ``@api_auth`` for the view after ``from djapiauth.auth import api_auth``

.. code-block:: python

	@api_auth
	def api_whoami(request):
		return JsonResponse({"user": "feifan", "boss": "lidan zhou"})



Register APIs
-------------
In order to manage APIs those can be assigned to an API key, we have to mark them first.
We may have two cases:

- For legacy views, we adds auth and register API in URL dispatching file at same time by utility function ``reg_n_protect_api``
- For views dedicate for API-style access, use utility function ``reg_api`` to finish the registration


.. code-block:: python

	# e.g.
	# 1, add auth for prevapp.views.myview, assign new url myapi/, of course, register the API
	# 2, since api_whoami have api_auth decorator in views.py, we only register here, 
	#    and assign url whoami/ for api.myapi.api_whoami

	import prevapp.views as app1views  # legacy views
	from djapiauth.utility import reg_n_protect_api, reg_api

	urlpatterns = patterns('api.myapi',
	                       reg_n_protect_api(r'^myapi/$', 'myview', views=app1views),  # 1
	                       reg_api(r'^whoami/$', 'api_whoami'),  # 2
	                       # ....
	                       )


Scan registered API
-------------------
we have a Django command ``reloadentrypoints`` to help you collect all registered API entry points to database.


Error messages
----------------------
- ``parameter missing``, any of ``apikey``, ``timestamp`` or ``signature`` missing in URL
- ``timestamp drifting xxx``, check your local time and server time. You can implement an API to return server time
- ``entry point not allowed for the API key``, check the assigned API for this API key in ``admin`` site or anywhere else you manage API keys
- ``signature error``, obviously, signature mismatch


DEMO
------
- Source code under ``example/djapp`` folder. 
- Test code is under ``example/test/``, we have ``python`` and ``javascript`` test code ready.

Server application provides 2 APIs

- ``/hello/`` : reused the code of index view, add an auth layer on it
- ``/goodbye/`` : a view you must access it by the signature stuff



DIY:

- Start the djapp
- there's already one pair of API+SEC keys: ``483a570a``, ``d7228d70cd7f456d9bfdc35ed8fee375``
- modify variable ``URL`` in ``test.py``, or ``URL`` in ``test.js``
- Generate API key and SEC key from localhost:8000/admin/xxx, modify variable ``API_KEY`` and ``SEC_KEY`` in ``test.py`` or ``test.js``
- Run ``python test.py`` or ``node test.js``
- login admin site with admin user: ``admin``/``123``, remove all APIs associated with ``483a570a``, try to run the test code again, you should see 403 errors ``__main__.APIException: (403, '{"error": "entry point not allowed for the API key"}')``
- modify the API key to an invalid one
- modify the SEC key to an invalid one
- modify your local time to one hour ago


Thanks
------


TODO
-----
- performance improvement for entry point matching in API permission check.
- easily solution to register API

