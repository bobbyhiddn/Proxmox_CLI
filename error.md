Micah Longmire@DESKTOP-DJH7JMF MINGW64 ~/Code/Proxmox_CLI (main)
$ pxmx
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "C:\Users\Micah Longmire\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\Scripts\pxmx.exe\__main__.py", line 4, in <module>
  File "C:\Users\Micah Longmire\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\pxmx_cli\pxmx.py", line 8, in <module>
    from pxmx_cli.commands import commands_list, aliases
  File "C:\Users\Micah Longmire\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\LocalCache\local-packages\Python312\site-packages\pxmx_cli\commands\__init__.py", line 14, in <module>
    commands_list.append(vars(_module)[module_name])
                         ~~~~~~~~~~~~~^^^^^^^^^^^^^
KeyError: 'vm-info'
