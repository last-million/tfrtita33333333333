INFO:app.database:MySQL connection pool created successfully.
INFO:app.database:Successfully connected to MySQL database.
WARNING:app.services.ultravox_service:Ultravox API key not found in environment variables.
/root/tfrtita33333333333/venv/lib/python3.12/site-packages/pydub/utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
  warn("Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work", RuntimeWarning)
[2025-04-10 04:51:57 +0000] [3400] [ERROR] Exception in worker process
Traceback (most recent call last):
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 608, in spawn_worker
    worker.init_process()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/uvicorn/workers.py", line 66, in init_process
    super(UvicornWorker, self).init_process()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/workers/base.py", line 135, in init_process
    self.load_wsgi()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/workers/base.py", line 147, in load_wsgi
    self.wsgi = self.app.wsgi()
                ^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/base.py", line 66, in wsgi
    self.callable = self.load()
                    ^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
    return self.load_wsgiapp()
           ^^^^^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
    return util.import_app(self.app_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/util.py", line 370, in import_app
    mod = importlib.import_module(module)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/root/tfrtita33333333333/backend/app/main.py", line 15, in <module>
    from ultravox.client import Client as UltravoxClient # Renamed to avoid conflict
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'ultravox'
[2025-04-10 04:51:57 +0000] [3400] [INFO] Worker exiting (pid: 3400)
WARNING:app.services.ultravox_service:Ultravox API key not found in environment variables.
/root/tfrtita33333333333/venv/lib/python3.12/site-packages/pydub/utils.py:170: RuntimeWarning: Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work
  warn("Couldn't find ffmpeg or avconv - defaulting to ffmpeg, but may not work", RuntimeWarning)
[2025-04-10 04:51:57 +0000] [3399] [ERROR] Exception in worker process
Traceback (most recent call last):
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 608, in spawn_worker
    worker.init_process()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/uvicorn/workers.py", line 66, in init_process
    super(UvicornWorker, self).init_process()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/workers/base.py", line 135, in init_process
    self.load_wsgi()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/workers/base.py", line 147, in load_wsgi
    self.wsgi = self.app.wsgi()
                ^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/base.py", line 66, in wsgi
    self.callable = self.load()
                    ^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
    return self.load_wsgiapp()
           ^^^^^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
    return util.import_app(self.app_uri)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/util.py", line 370, in import_app
    mod = importlib.import_module(module)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/root/tfrtita33333333333/backend/app/main.py", line 15, in <module>
    from ultravox.client import Client as UltravoxClient # Renamed to avoid conflict
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'ultravox'
[2025-04-10 04:51:57 +0000] [3399] [INFO] Worker exiting (pid: 3399)
[2025-04-10 04:51:57 +0000] [3398] [ERROR] Worker (pid:3399) exited with code 3
[2025-04-10 04:51:57 +0000] [3398] [ERROR] Worker (pid:3400) was sent SIGTERM!
--- Logging error ---
Traceback (most recent call last):
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 208, in run
    self.sleep()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 359, in sleep
    ready = select.select([self.PIPE[0]], [], [], 1.0)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 241, in handle_chld
    self.reap_workers()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 529, in reap_workers
    raise HaltServer(reason, self.WORKER_BOOT_ERROR)
gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3.12/logging/__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
RuntimeError: reentrant call inside <_io.BufferedWriter name='<stderr>'>

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3.12/logging/__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 241, in handle_chld
    self.reap_workers()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 553, in reap_workers
    self.log.error(msg)
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/glogging.py", line 271, in error
    self.error_log.error(msg, *args, **kwargs)
  File "/usr/lib/python3.12/logging/__init__.py", line 1568, in error
    self._log(ERROR, msg, args, **kwargs)
  File "/usr/lib/python3.12/logging/__init__.py", line 1684, in _log
    self.handle(record)
  File "/usr/lib/python3.12/logging/__init__.py", line 1700, in handle
    self.callHandlers(record)
  File "/usr/lib/python3.12/logging/__init__.py", line 1762, in callHandlers
    hdlr.handle(record)
  File "/usr/lib/python3.12/logging/__init__.py", line 1028, in handle
    self.emit(record)
  File "/usr/lib/python3.12/logging/__init__.py", line 1168, in emit
    self.handleError(record)
  File "/usr/lib/python3.12/logging/__init__.py", line 1081, in handleError
    sys.stderr.write('--- Logging error ---\n')
RuntimeError: reentrant call inside <_io.BufferedWriter name='<stderr>'>
Call stack:
  File "/root/tfrtita33333333333/venv/bin/gunicorn", line 8, in <module>
    sys.exit(run())
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/wsgiapp.py", line 66, in run
    WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]", prog=prog).run()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/base.py", line 235, in run
    super().run()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/app/base.py", line 71, in run
    Arbiter(self).run()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 228, in run
    self.halt(reason=inst.reason, exit_status=inst.exit_status)
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 341, in halt
    self.stop()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 395, in stop
    time.sleep(0.1)
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 241, in handle_chld
    self.reap_workers()
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/arbiter.py", line 553, in reap_workers
    self.log.error(msg)
  File "/root/tfrtita33333333333/venv/lib/python3.12/site-packages/gunicorn/glogging.py", line 271, in error
    self.error_log.error(msg, *args, **kwargs)
Message: 'Worker (pid:3400) was sent SIGTERM!'
Arguments: ()
^C[2025-04-10 04:52:27 +0000] [3398] [ERROR] Shutting down: Master
[2025-04-10 04:52:27 +0000] [3398] [ERROR] Reason: Worker failed to boot.
(venv) root@aicalles:~/tfrtita33333333333/backend# cd ~/tfrtita33333333333/backend
(venv) root@aicalles:~/tfrtita33333333333/backend# source ../venv/bin/activate
(venv) root@aicalles:~/tfrtita33333333333/backend# pip install -r requirements.txt
Requirement already satisfied: fastapi==0.100.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 2)) (0.100.0)
Requirement already satisfied: uvicorn==0.23.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 3)) (0.23.1)
Requirement already satisfied: gunicorn in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 4)) (23.0.0)
Requirement already satisfied: python-multipart==0.0.6 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 5)) (0.0.6)
Requirement already satisfied: google-auth-oauthlib==1.0.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 8)) (1.0.0)
Requirement already satisfied: google-auth-httplib2==0.1.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 9)) (0.1.0)
Requirement already satisfied: google-api-python-client==2.95.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 10)) (2.95.0)
Requirement already satisfied: supabase==1.0.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 13)) (1.0.3)
Requirement already satisfied: sentence-transformers==2.2.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 16)) (2.2.2)
Requirement already satisfied: python-magic==0.4.27 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 17)) (0.4.27)
Requirement already satisfied: PyPDF2==3.0.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 18)) (3.0.1)
Requirement already satisfied: python-docx==0.8.11 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 19)) (0.8.11)
Requirement already satisfied: openpyxl==3.1.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 20)) (3.1.2)
Requirement already satisfied: pandas==2.0.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 21)) (2.0.2)
Requirement already satisfied: twilio in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 25)) (9.5.2)
Requirement already satisfied: pydantic-settings in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 28)) (2.8.1)
Requirement already satisfied: mysql-connector-python in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 31)) (9.2.0)
Requirement already satisfied: ultravox-client in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 34)) (0.0.6)
Requirement already satisfied: pydub in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from -r requirements.txt (line 35)) (0.25.1)
Requirement already satisfied: pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,<3.0.0,>=1.7.4 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from fastapi==0.100.0->-r requirements.txt (line 2)) (2.11.3)
Requirement already satisfied: starlette<0.28.0,>=0.27.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from fastapi==0.100.0->-r requirements.txt (line 2)) (0.27.0)
Requirement already satisfied: typing-extensions>=4.5.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from fastapi==0.100.0->-r requirements.txt (line 2)) (4.13.1)
Requirement already satisfied: click>=7.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from uvicorn==0.23.1->-r requirements.txt (line 3)) (8.1.8)
Requirement already satisfied: h11>=0.8 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from uvicorn==0.23.1->-r requirements.txt (line 3)) (0.14.0)
Requirement already satisfied: google-auth>=2.15.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (2.38.0)
Requirement already satisfied: requests-oauthlib>=0.7.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (2.0.0)
Requirement already satisfied: httplib2>=0.15.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth-httplib2==0.1.0->-r requirements.txt (line 9)) (0.22.0)
Requirement already satisfied: six in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth-httplib2==0.1.0->-r requirements.txt (line 9)) (1.17.0)
Requirement already satisfied: google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-api-python-client==2.95.0->-r requirements.txt (line 10)) (2.24.2)
Requirement already satisfied: uritemplate<5,>=3.0.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-api-python-client==2.95.0->-r requirements.txt (line 10)) (4.1.1)
Requirement already satisfied: gotrue<2.0.0,>=1.0.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (1.3.1)
Requirement already satisfied: httpx<0.24.0,>=0.23.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (0.23.3)
Requirement already satisfied: postgrest<0.11.0,>=0.10.6 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (0.10.7)
Requirement already satisfied: python-semantic-release==7.33.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (7.33.2)
Requirement already satisfied: realtime<2.0.0,>=1.0.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (1.0.6)
Requirement already satisfied: storage3<0.6.0,>=0.5.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (0.5.3)
Requirement already satisfied: supafunc<0.3.0,>=0.2.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from supabase==1.0.3->-r requirements.txt (line 13)) (0.2.2)
Requirement already satisfied: transformers<5.0.0,>=4.6.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (4.51.1)
Requirement already satisfied: tqdm in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (4.67.1)
Requirement already satisfied: torch>=1.6.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (2.6.0)
Requirement already satisfied: torchvision in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (0.21.0)
Requirement already satisfied: numpy in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (2.2.4)
Requirement already satisfied: scikit-learn in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (1.6.1)
Requirement already satisfied: scipy in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (1.15.2)
Requirement already satisfied: nltk in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.9.1)
Requirement already satisfied: sentencepiece in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (0.2.0)
Requirement already satisfied: huggingface-hub>=0.4.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sentence-transformers==2.2.2->-r requirements.txt (line 16)) (0.30.2)
Requirement already satisfied: lxml>=2.3.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-docx==0.8.11->-r requirements.txt (line 19)) (5.3.2)
Requirement already satisfied: et-xmlfile in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from openpyxl==3.1.2->-r requirements.txt (line 20)) (2.0.0)
Requirement already satisfied: python-dateutil>=2.8.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pandas==2.0.2->-r requirements.txt (line 21)) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pandas==2.0.2->-r requirements.txt (line 21)) (2025.2)
Requirement already satisfied: tzdata>=2022.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pandas==2.0.2->-r requirements.txt (line 21)) (2025.2)
Requirement already satisfied: click-log<1,>=0.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.4.0)
Requirement already satisfied: gitpython<4,>=3.0.8 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.1.44)
Requirement already satisfied: invoke<2,>=1.4.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (1.7.3)
Requirement already satisfied: semver<3,>=2.10 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (2.13.0)
Requirement already satisfied: twine<4,>=3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.8.0)
Requirement already satisfied: requests<3,>=2.25 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (2.32.3)
Requirement already satisfied: wheel in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.45.1)
Requirement already satisfied: python-gitlab<4,>=2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.15.0)
Requirement already satisfied: tomlkit~=0.10 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.13.2)
Requirement already satisfied: dotty-dict<2,>=1.3.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (1.3.1)
Requirement already satisfied: packaging in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (24.2)
Requirement already satisfied: PyJWT<3.0.0,>=2.0.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twilio->-r requirements.txt (line 25)) (2.10.1)
Requirement already satisfied: aiohttp>=3.8.4 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twilio->-r requirements.txt (line 25)) (3.11.16)
Requirement already satisfied: aiohttp-retry>=2.8.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twilio->-r requirements.txt (line 25)) (2.9.1)
Requirement already satisfied: python-dotenv>=0.21.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pydantic-settings->-r requirements.txt (line 28)) (1.1.0)
Requirement already satisfied: livekit==0.8 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from ultravox-client->-r requirements.txt (line 34)) (0.8.0)
Requirement already satisfied: pyee<12.0.0,>=11.0.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from ultravox-client->-r requirements.txt (line 34)) (11.1.1)
Requirement already satisfied: sounddevice<0.6.0,>=0.5.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from ultravox-client->-r requirements.txt (line 34)) (0.5.1)
Requirement already satisfied: websockets<13.0,>=12.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from ultravox-client->-r requirements.txt (line 34)) (12.0)
Requirement already satisfied: protobuf>=4 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from livekit==0.8->ultravox-client->-r requirements.txt (line 34)) (6.30.2)
Requirement already satisfied: types-protobuf>=4 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from livekit==0.8->ultravox-client->-r requirements.txt (line 34)) (5.29.1.20250403)
Requirement already satisfied: aiohappyeyeballs>=2.3.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (2.6.1)
Requirement already satisfied: aiosignal>=1.1.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (1.3.2)
Requirement already satisfied: attrs>=17.3.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (25.3.0)
Requirement already satisfied: frozenlist>=1.1.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (1.5.0)
Requirement already satisfied: multidict<7.0,>=4.5 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (6.4.2)
Requirement already satisfied: propcache>=0.2.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (0.3.1)
Requirement already satisfied: yarl<2.0,>=1.17.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from aiohttp>=3.8.4->twilio->-r requirements.txt (line 25)) (1.19.0)
Requirement already satisfied: googleapis-common-protos<2.0.0,>=1.56.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client==2.95.0->-r requirements.txt (line 10)) (1.69.2)
Requirement already satisfied: proto-plus<2.0.0,>=1.22.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client==2.95.0->-r requirements.txt (line 10)) (1.26.1)
Requirement already satisfied: cachetools<6.0,>=2.0.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth>=2.15.0->google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (5.5.2)
Requirement already satisfied: pyasn1-modules>=0.2.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth>=2.15.0->google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (0.4.2)
Requirement already satisfied: rsa<5,>=3.1.4 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from google-auth>=2.15.0->google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (4.9)
Requirement already satisfied: pyparsing!=3.0.0,!=3.0.1,!=3.0.2,!=3.0.3,<4,>=2.4.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from httplib2>=0.15.0->google-auth-httplib2==0.1.0->-r requirements.txt (line 9)) (3.2.3)
Requirement already satisfied: certifi in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from httpx<0.24.0,>=0.23.0->supabase==1.0.3->-r requirements.txt (line 13)) (2025.1.31)
Requirement already satisfied: httpcore<0.17.0,>=0.15.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from httpx<0.24.0,>=0.23.0->supabase==1.0.3->-r requirements.txt (line 13)) (0.16.3)
Requirement already satisfied: rfc3986<2,>=1.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from rfc3986[idna2008]<2,>=1.3->httpx<0.24.0,>=0.23.0->supabase==1.0.3->-r requirements.txt (line 13)) (1.5.0)
Requirement already satisfied: sniffio in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from httpx<0.24.0,>=0.23.0->supabase==1.0.3->-r requirements.txt (line 13)) (1.3.1)
Requirement already satisfied: filelock in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from huggingface-hub>=0.4.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.18.0)
Requirement already satisfied: fsspec>=2023.5.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from huggingface-hub>=0.4.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (2025.3.2)
Requirement already satisfied: pyyaml>=5.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from huggingface-hub>=0.4.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (6.0.2)
Requirement already satisfied: deprecation<3.0.0,>=2.1.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from postgrest<0.11.0,>=0.10.6->supabase==1.0.3->-r requirements.txt (line 13)) (2.1.0)
Requirement already satisfied: strenum<0.5.0,>=0.4.9 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from postgrest<0.11.0,>=0.10.6->supabase==1.0.3->-r requirements.txt (line 13)) (0.4.15)
Requirement already satisfied: annotated-types>=0.6.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,<3.0.0,>=1.7.4->fastapi==0.100.0->-r requirements.txt (line 2)) (0.7.0)
Requirement already satisfied: pydantic-core==2.33.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,<3.0.0,>=1.7.4->fastapi==0.100.0->-r requirements.txt (line 2)) (2.33.1)
Requirement already satisfied: typing-inspection>=0.4.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pydantic!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,<3.0.0,>=1.7.4->fastapi==0.100.0->-r requirements.txt (line 2)) (0.4.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from requests<3,>=2.25->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.4.1)
Requirement already satisfied: idna<4,>=2.5 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from requests<3,>=2.25->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from requests<3,>=2.25->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (2.3.0)
Requirement already satisfied: oauthlib>=3.0.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from requests-oauthlib>=0.7.0->google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (3.2.2)
Requirement already satisfied: CFFI>=1.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sounddevice<0.6.0,>=0.5.0->ultravox-client->-r requirements.txt (line 34)) (1.17.1)
Requirement already satisfied: anyio<5,>=3.4.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from starlette<0.28.0,>=0.27.0->fastapi==0.100.0->-r requirements.txt (line 2)) (4.9.0)
Requirement already satisfied: networkx in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.4.2)
Requirement already satisfied: jinja2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.1.6)
Requirement already satisfied: nvidia-cuda-nvrtc-cu12==12.4.127 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.4.127)
Requirement already satisfied: nvidia-cuda-runtime-cu12==12.4.127 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.4.127)
Requirement already satisfied: nvidia-cuda-cupti-cu12==12.4.127 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.4.127)
Requirement already satisfied: nvidia-cudnn-cu12==9.1.0.70 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (9.1.0.70)
Requirement already satisfied: nvidia-cublas-cu12==12.4.5.8 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.4.5.8)
Requirement already satisfied: nvidia-cufft-cu12==11.2.1.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (11.2.1.3)
Requirement already satisfied: nvidia-curand-cu12==10.3.5.147 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (10.3.5.147)
Requirement already satisfied: nvidia-cusolver-cu12==11.6.1.9 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (11.6.1.9)
Requirement already satisfied: nvidia-cusparse-cu12==12.3.1.170 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.3.1.170)
Requirement already satisfied: nvidia-cusparselt-cu12==0.6.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (0.6.2)
Requirement already satisfied: nvidia-nccl-cu12==2.21.5 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (2.21.5)
Requirement already satisfied: nvidia-nvtx-cu12==12.4.127 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.4.127)
Requirement already satisfied: nvidia-nvjitlink-cu12==12.4.127 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (12.4.127)
Requirement already satisfied: triton==3.2.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.2.0)
Requirement already satisfied: setuptools in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (78.1.0)
Requirement already satisfied: sympy==1.13.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (1.13.1)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from sympy==1.13.1->torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (1.3.0)
Requirement already satisfied: regex!=2019.12.17 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from transformers<5.0.0,>=4.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (2024.11.6)
Requirement already satisfied: tokenizers<0.22,>=0.21 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from transformers<5.0.0,>=4.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (0.21.1)
Requirement already satisfied: safetensors>=0.4.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from transformers<5.0.0,>=4.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (0.5.3)
Requirement already satisfied: joblib in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from nltk->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (1.4.2)
Requirement already satisfied: threadpoolctl>=3.1.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from scikit-learn->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.6.0)
Requirement already satisfied: pillow!=8.3.*,>=5.3.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from torchvision->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (11.1.0)
Requirement already satisfied: pycparser in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from CFFI>=1.0->sounddevice<0.6.0,>=0.5.0->ultravox-client->-r requirements.txt (line 34)) (2.22)
Requirement already satisfied: gitdb<5,>=4.0.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from gitpython<4,>=3.0.8->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (4.0.12)
Requirement already satisfied: pyasn1<0.7.0,>=0.6.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from pyasn1-modules>=0.2.1->google-auth>=2.15.0->google-auth-oauthlib==1.0.0->-r requirements.txt (line 8)) (0.6.1)
Requirement already satisfied: requests-toolbelt>=0.10.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from python-gitlab<4,>=2->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (1.0.0)
Requirement already satisfied: pkginfo>=1.8.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (1.12.1.2)
Requirement already satisfied: readme-renderer>=21.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (44.0)
Requirement already satisfied: importlib-metadata>=3.6 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (8.6.1)
Requirement already satisfied: keyring>=15.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (25.6.0)
Requirement already satisfied: colorama>=0.4.3 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.4.6)
Requirement already satisfied: MarkupSafe>=2.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from jinja2->torch>=1.6.0->sentence-transformers==2.2.2->-r requirements.txt (line 16)) (3.0.2)
Requirement already satisfied: smmap<6,>=3.0.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from gitdb<5,>=4.0.1->gitpython<4,>=3.0.8->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (5.0.2)
Requirement already satisfied: zipp>=3.20 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from importlib-metadata>=3.6->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.21.0)
Requirement already satisfied: SecretStorage>=3.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.3.3)
Requirement already satisfied: jeepney>=0.4.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.9.0)
Requirement already satisfied: jaraco.classes in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (3.4.0)
Requirement already satisfied: jaraco.functools in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (4.1.0)
Requirement already satisfied: jaraco.context in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (6.0.1)
Requirement already satisfied: nh3>=0.2.14 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from readme-renderer>=21.0->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.2.21)
Requirement already satisfied: docutils>=0.21.2 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from readme-renderer>=21.0->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (0.21.2)
Requirement already satisfied: Pygments>=2.5.1 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from readme-renderer>=21.0->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (2.19.1)
Requirement already satisfied: cryptography>=2.0 in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from SecretStorage>=3.2->keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (44.0.2)
Requirement already satisfied: more-itertools in /root/tfrtita33333333333/venv/lib/python3.12/site-packages (from jaraco.classes->keyring>=15.1->twine<4,>=3->python-semantic-release==7.33.2->supabase==1.0.3->-r requirements.txt (line 13)) (10.6.0)
(venv) root@aicalles:~/tfrtita33333333333/backend# deactivate
root@aicalles:~/tfrtita33333333333/backend# sudo systemctl restart tfrtita333.service
root@aicalles:~/tfrtita33333333333/backend# systemctl status tfrtita333.service
× tfrtita333.service - Tfrtita333 App Backend
     Loaded: loaded (/etc/systemd/system/tfrtita333.service; enabled; preset: enabled)
     Active: failed (Result: exit-code) since Thu 2025-04-10 04:56:10 UTC; 3s ago
   Duration: 1ms
    Process: 3462 ExecStart=/root/tfrtita33333333333/venv/bin/gunicorn -k uvicorn.workers.UvicornWorker -w 3 --bind 127.0.0.1:8080 app.main:app (code=exited, status=217/USER)
   Main PID: 3462 (code=exited, status=217/USER)
        CPU: 796us

Apr 10 04:56:10 aicalles systemd[1]: tfrtita333.service: Scheduled restart job, restart counter is at 5.
Apr 10 04:56:10 aicalles systemd[1]: tfrtita333.service: Start request repeated too quickly.
Apr 10 04:56:10 aicalles systemd[1]: tfrtita333.service: Failed with result 'exit-code'.
Apr 10 04:56:10 aicalles systemd[1]: Failed to start tfrtita333.service - Tfrtita333 App Backend.
root@aicalles:~/tfrtita33333333333/backend#
