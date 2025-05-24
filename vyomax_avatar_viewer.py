Microsoft Windows [Version 10.0.22631.5335]
(c) Microsoft Corporation. All rights reserved.

C:\Windows\System32>cd C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid

C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>py -3.12 --version
Python 3.12.5

C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>py -3.12 -m venv .venv_robot

C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>.venv_robot\Scripts\activate
'"C:\WINDOWS\System32\chcp.com"' is not recognized as an internal or external command,
operable program or batch file.

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>python -m pip install --upgrade pip
Requirement already satisfied: pip in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (24.2)
Collecting pip
  Using cached pip-25.1.1-py3-none-any.whl.metadata (3.6 kB)
Using cached pip-25.1.1-py3-none-any.whl (1.8 MB)
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 24.2
    Uninstalling pip-24.2:
      Successfully uninstalled pip-24.2
Successfully installed pip-25.1.1

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>pip install pygame speech_recognition pyttsx3 pywhatkit wikipedia pyjokes opencv-python face_recognition dlib transformers torch
Collecting pygame
  Downloading pygame-2.6.1-cp312-cp312-win_amd64.whl.metadata (13 kB)
ERROR: Could not find a version that satisfies the requirement speech_recognition (from versions: none)
ERROR: No matching distribution found for speech_recognition

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>pip install speech recognition
Collecting speech
  Downloading speech-0.5.2.tar.gz (18 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
ERROR: Could not find a version that satisfies the requirement recognition (from versions: none)
ERROR: No matching distribution found for recognition

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>pip install pygame SpeechRecognition pyttsx3 pywhatkit wikipedia pyjokes opencv-python face_recognition dlib transformers torch
Collecting pygame
  Using cached pygame-2.6.1-cp312-cp312-win_amd64.whl.metadata (13 kB)
Collecting SpeechRecognition
  Using cached speechrecognition-3.14.3-py3-none-any.whl.metadata (30 kB)
Collecting pyttsx3
  Using cached pyttsx3-2.98-py3-none-any.whl.metadata (3.8 kB)
Collecting pywhatkit
  Using cached pywhatkit-5.4-py3-none-any.whl.metadata (5.5 kB)
Collecting wikipedia
  Using cached wikipedia-1.4.0.tar.gz (27 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pyjokes
  Using cached pyjokes-0.8.3-py3-none-any.whl.metadata (3.4 kB)
Collecting opencv-python
  Using cached opencv_python-4.11.0.86-cp37-abi3-win_amd64.whl.metadata (20 kB)
Collecting face_recognition
  Using cached face_recognition-1.3.0-py2.py3-none-any.whl.metadata (21 kB)
Collecting dlib
  Using cached dlib-19.24.9.tar.gz (3.4 MB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting transformers
  Using cached transformers-4.52.3-py3-none-any.whl.metadata (40 kB)
Collecting torch
  Downloading torch-2.7.0-cp312-cp312-win_amd64.whl.metadata (29 kB)
Collecting typing-extensions (from SpeechRecognition)
  Using cached typing_extensions-4.13.2-py3-none-any.whl.metadata (3.0 kB)
Collecting comtypes (from pyttsx3)
  Using cached comtypes-1.4.11-py3-none-any.whl.metadata (7.2 kB)
Collecting pypiwin32 (from pyttsx3)
  Using cached pypiwin32-223-py3-none-any.whl.metadata (236 bytes)
Collecting pywin32 (from pyttsx3)
  Downloading pywin32-310-cp312-cp312-win_amd64.whl.metadata (9.4 kB)
Collecting Pillow (from pywhatkit)
  Downloading pillow-11.2.1-cp312-cp312-win_amd64.whl.metadata (9.1 kB)
Collecting pyautogui (from pywhatkit)
  Using cached PyAutoGUI-0.9.54.tar.gz (61 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting requests (from pywhatkit)
  Using cached requests-2.32.3-py3-none-any.whl.metadata (4.6 kB)
Collecting Flask (from pywhatkit)
  Using cached flask-3.1.1-py3-none-any.whl.metadata (3.0 kB)
Collecting beautifulsoup4 (from wikipedia)
  Using cached beautifulsoup4-4.13.4-py3-none-any.whl.metadata (3.8 kB)
Collecting charset-normalizer<4,>=2 (from requests->pywhatkit)
  Downloading charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl.metadata (36 kB)
Collecting idna<4,>=2.5 (from requests->pywhatkit)
  Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
Collecting urllib3<3,>=1.21.1 (from requests->pywhatkit)
  Using cached urllib3-2.4.0-py3-none-any.whl.metadata (6.5 kB)
Collecting certifi>=2017.4.17 (from requests->pywhatkit)
  Using cached certifi-2025.4.26-py3-none-any.whl.metadata (2.5 kB)
Collecting numpy>=1.21.2 (from opencv-python)
  Downloading numpy-2.2.6-cp312-cp312-win_amd64.whl.metadata (60 kB)
Collecting face-recognition-models>=0.3.0 (from face_recognition)
  Using cached face_recognition_models-0.3.0.tar.gz (100.1 MB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting Click>=6.0 (from face_recognition)
  Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
Collecting filelock (from transformers)
  Using cached filelock-3.18.0-py3-none-any.whl.metadata (2.9 kB)
Collecting huggingface-hub<1.0,>=0.30.0 (from transformers)
  Using cached huggingface_hub-0.32.0-py3-none-any.whl.metadata (14 kB)
Collecting packaging>=20.0 (from transformers)
  Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
Collecting pyyaml>=5.1 (from transformers)
  Downloading PyYAML-6.0.2-cp312-cp312-win_amd64.whl.metadata (2.1 kB)
Collecting regex!=2019.12.17 (from transformers)
  Downloading regex-2024.11.6-cp312-cp312-win_amd64.whl.metadata (41 kB)
Collecting tokenizers<0.22,>=0.21 (from transformers)
  Using cached tokenizers-0.21.1-cp39-abi3-win_amd64.whl.metadata (6.9 kB)
Collecting safetensors>=0.4.3 (from transformers)
  Using cached safetensors-0.5.3-cp38-abi3-win_amd64.whl.metadata (3.9 kB)
Collecting tqdm>=4.27 (from transformers)
  Using cached tqdm-4.67.1-py3-none-any.whl.metadata (57 kB)
Collecting fsspec>=2023.5.0 (from huggingface-hub<1.0,>=0.30.0->transformers)
  Using cached fsspec-2025.5.1-py3-none-any.whl.metadata (11 kB)
Collecting sympy>=1.13.3 (from torch)
  Using cached sympy-1.14.0-py3-none-any.whl.metadata (12 kB)
Collecting networkx (from torch)
  Using cached networkx-3.4.2-py3-none-any.whl.metadata (6.3 kB)
Collecting jinja2 (from torch)
  Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
Collecting setuptools (from torch)
  Using cached setuptools-80.8.0-py3-none-any.whl.metadata (6.6 kB)
Collecting colorama (from Click>=6.0->face_recognition)
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Collecting mpmath<1.4,>=1.1.0 (from sympy>=1.13.3->torch)
  Using cached mpmath-1.3.0-py3-none-any.whl.metadata (8.6 kB)
Collecting soupsieve>1.2 (from beautifulsoup4->wikipedia)
  Using cached soupsieve-2.7-py3-none-any.whl.metadata (4.6 kB)
Collecting blinker>=1.9.0 (from Flask->pywhatkit)
  Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
Collecting itsdangerous>=2.2.0 (from Flask->pywhatkit)
  Using cached itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
Collecting markupsafe>=2.1.1 (from Flask->pywhatkit)
  Downloading MarkupSafe-3.0.2-cp312-cp312-win_amd64.whl.metadata (4.1 kB)
Collecting werkzeug>=3.1.0 (from Flask->pywhatkit)
  Using cached werkzeug-3.1.3-py3-none-any.whl.metadata (3.7 kB)
Collecting pymsgbox (from pyautogui->pywhatkit)
  Using cached PyMsgBox-1.0.9.tar.gz (18 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pytweening>=1.0.4 (from pyautogui->pywhatkit)
  Using cached pytweening-1.2.0.tar.gz (171 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pyscreeze>=0.1.21 (from pyautogui->pywhatkit)
  Using cached pyscreeze-1.0.1.tar.gz (27 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pygetwindow>=0.0.5 (from pyautogui->pywhatkit)
  Using cached PyGetWindow-0.0.9.tar.gz (9.7 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting mouseinfo (from pyautogui->pywhatkit)
  Using cached MouseInfo-0.1.3.tar.gz (10 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pyrect (from pygetwindow>=0.0.5->pyautogui->pywhatkit)
  Using cached PyRect-0.2.0.tar.gz (17 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pyperclip (from mouseinfo->pyautogui->pywhatkit)
  Using cached pyperclip-1.9.0.tar.gz (20 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Downloading pygame-2.6.1-cp312-cp312-win_amd64.whl (10.6 MB)
   ---------------------------------------- 10.6/10.6 MB 4.3 MB/s eta 0:00:00
Using cached speechrecognition-3.14.3-py3-none-any.whl (32.9 MB)
Using cached pyttsx3-2.98-py3-none-any.whl (34 kB)
Using cached pywhatkit-5.4-py3-none-any.whl (15 kB)
Using cached requests-2.32.3-py3-none-any.whl (64 kB)
Downloading charset_normalizer-3.4.2-cp312-cp312-win_amd64.whl (105 kB)
Using cached idna-3.10-py3-none-any.whl (70 kB)
Using cached urllib3-2.4.0-py3-none-any.whl (128 kB)
Using cached pyjokes-0.8.3-py3-none-any.whl (47 kB)
Using cached opencv_python-4.11.0.86-cp37-abi3-win_amd64.whl (39.5 MB)
Using cached face_recognition-1.3.0-py2.py3-none-any.whl (15 kB)
Using cached transformers-4.52.3-py3-none-any.whl (10.5 MB)
Using cached huggingface_hub-0.32.0-py3-none-any.whl (509 kB)
Using cached tokenizers-0.21.1-cp39-abi3-win_amd64.whl (2.4 MB)
Downloading torch-2.7.0-cp312-cp312-win_amd64.whl (212.5 MB)
   ---------------------------------------- 212.5/212.5 MB 3.2 MB/s eta 0:00:00
Using cached certifi-2025.4.26-py3-none-any.whl (159 kB)
Using cached click-8.2.1-py3-none-any.whl (102 kB)
Using cached fsspec-2025.5.1-py3-none-any.whl (199 kB)
Downloading numpy-2.2.6-cp312-cp312-win_amd64.whl (12.6 MB)
   ---------------------------------------- 12.6/12.6 MB 3.8 MB/s eta 0:00:00
Using cached packaging-25.0-py3-none-any.whl (66 kB)
Downloading PyYAML-6.0.2-cp312-cp312-win_amd64.whl (156 kB)
Downloading regex-2024.11.6-cp312-cp312-win_amd64.whl (273 kB)
Using cached safetensors-0.5.3-cp38-abi3-win_amd64.whl (308 kB)
Using cached sympy-1.14.0-py3-none-any.whl (6.3 MB)
Using cached mpmath-1.3.0-py3-none-any.whl (536 kB)
Using cached tqdm-4.67.1-py3-none-any.whl (78 kB)
Using cached typing_extensions-4.13.2-py3-none-any.whl (45 kB)
Using cached beautifulsoup4-4.13.4-py3-none-any.whl (187 kB)
Using cached soupsieve-2.7-py3-none-any.whl (36 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Using cached comtypes-1.4.11-py3-none-any.whl (246 kB)
Using cached filelock-3.18.0-py3-none-any.whl (16 kB)
Using cached flask-3.1.1-py3-none-any.whl (103 kB)
Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
Using cached itsdangerous-2.2.0-py3-none-any.whl (16 kB)
Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
Downloading MarkupSafe-3.0.2-cp312-cp312-win_amd64.whl (15 kB)
Using cached werkzeug-3.1.3-py3-none-any.whl (224 kB)
Using cached networkx-3.4.2-py3-none-any.whl (1.7 MB)
Downloading pillow-11.2.1-cp312-cp312-win_amd64.whl (2.7 MB)
   ---------------------------------------- 2.7/2.7 MB 3.8 MB/s eta 0:00:00
Using cached pypiwin32-223-py3-none-any.whl (1.7 kB)
Downloading pywin32-310-cp312-cp312-win_amd64.whl (9.5 MB)
   ---------------------------------------- 9.5/9.5 MB 3.3 MB/s eta 0:00:00
Using cached setuptools-80.8.0-py3-none-any.whl (1.2 MB)
Building wheels for collected packages: wikipedia, dlib, face-recognition-models, pyautogui, pygetwindow, pyscreeze, pytweening, mouseinfo, pymsgbox, pyperclip, pyrect
  Building wheel for wikipedia (pyproject.toml) ... done
  Created wheel for wikipedia: filename=wikipedia-1.4.0-py3-none-any.whl size=11784 sha256=4b4060c7a516e90ad1c244348ec32693969da9e8603d6bdd75a702c2cbe17d03
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\63\47\7c\a9688349aa74d228ce0a9023229c6c0ac52ca2a40fe87679b8
  Building wheel for dlib (pyproject.toml) ... done
  Created wheel for dlib: filename=dlib-19.24.9-cp312-cp312-win_amd64.whl size=2927244 sha256=c8692677df7a995d34517e4aa4e6742149febb569b0b9cc8515dd8fef19cb595
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\3e\dd\f4\4d31a74848ef1c9cfd1857a5c43d1fa226d5ad0c7340dc34df
  Building wheel for face-recognition-models (pyproject.toml) ... done
  Created wheel for face-recognition-models: filename=face_recognition_models-0.3.0-py2.py3-none-any.whl size=100566257 sha256=1307ce54a5b869ae53cbed4c443b226f0c6cb1316208865716311aa69f54c64a
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\8f\47\c8\f44c5aebb7507f7c8a2c0bd23151d732d0f0bd6884ad4ac635
  Building wheel for pyautogui (pyproject.toml) ... done
  Created wheel for pyautogui: filename=pyautogui-0.9.54-py3-none-any.whl size=37705 sha256=0ffd338520d690836297b9e052ad237123cc4889e38eb37b7de5cb88fa27dd75
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\d9\d6\47\04075995b093ecc87c212c9a3dbd34e59456c6fe504d65c3e4
  Building wheel for pygetwindow (pyproject.toml) ... done
  Created wheel for pygetwindow: filename=pygetwindow-0.0.9-py3-none-any.whl size=11135 sha256=75ddb757a1847475a409c98804b01404acc63d81d34f863582ba970f0c2e27c4
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\b3\39\81\34dd7a2eca5f885f1f6e2796761970daf66a2d98ac1904f5f4
  Building wheel for pyscreeze (pyproject.toml) ... done
  Created wheel for pyscreeze: filename=pyscreeze-1.0.1-py3-none-any.whl size=14477 sha256=bdd39c0357e6cde6f4337a934e86cead36474ed8becb7bc8a91f0cc993e6b59e
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\cd\3a\c2\7f2839239a069aa3c9564f6777cbb29d733720ef673f104f0d
  Building wheel for pytweening (pyproject.toml) ... done
  Created wheel for pytweening: filename=pytweening-1.2.0-py3-none-any.whl size=8134 sha256=ce3c48a93b484ddc4ad2433c8a5efcbb807b17088dd975a1c2dd39674269f5dd
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\23\d5\13\4e9bdadbfe3c78e47c675e7410c0eed2fbb63c5ea6cf1b40e7
  Building wheel for mouseinfo (pyproject.toml) ... done
  Created wheel for mouseinfo: filename=mouseinfo-0.1.3-py3-none-any.whl size=10965 sha256=8d8d42ecca3a802b826f5b9f5870e3cfb01a31c62e49e9b976bf509eb8ea985d
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\b1\9b\f3\08650eb7f00af32f07789f3c6a101e0d7fc762b9891ae843bb
  Building wheel for pymsgbox (pyproject.toml) ... done
  Created wheel for pymsgbox: filename=pymsgbox-1.0.9-py3-none-any.whl size=7466 sha256=797092af45cbd34bfdf7378e64bf955d9ccce75d25d7f5a971adf113d977595b
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\55\e7\aa\239163543708d1e15c3d9a1b89dbfe3954b0929a6df2951b83
  Building wheel for pyperclip (pyproject.toml) ... done
  Created wheel for pyperclip: filename=pyperclip-1.9.0-py3-none-any.whl size=11114 sha256=e3bf6f5b44d06816047fe43ee71a9a759d0b89bc2f06fd29746befbc23f68404
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\e0\e8\fc\8ab8aa326e33bc066ccd5f3ca9646eab4299881af933f94f09
  Building wheel for pyrect (pyproject.toml) ... done
  Created wheel for pyrect: filename=pyrect-0.2.0-py2.py3-none-any.whl size=11306 sha256=a3a3a900d7021436897626831dde343e51bbc10c595a056798b5f23193b6a38f
  Stored in directory: c:\users\lavan\appdata\local\pip\cache\wheels\0b\1e\d7\0c74bd8f60b39c14d84e307398786002aa7ddc905927cc03c5
Successfully built wikipedia dlib face-recognition-models pyautogui pygetwindow pyscreeze pytweening mouseinfo pymsgbox pyperclip pyrect
Installing collected packages: pywin32, pytweening, pyscreeze, pyrect, pyperclip, pymsgbox, mpmath, face-recognition-models, dlib, urllib3, typing-extensions, sympy, soupsieve, setuptools, safetensors, regex, pyyaml, pypiwin32, pyjokes, pygetwindow, pygame, Pillow, packaging, numpy, networkx, mouseinfo, markupsafe, itsdangerous, idna, fsspec, filelock, comtypes, colorama, charset-normalizer, certifi, blinker, werkzeug, tqdm, SpeechRecognition, requests, pyttsx3, pyautogui, opencv-python, jinja2, Click, beautifulsoup4, wikipedia, torch, huggingface-hub, Flask, face_recognition, tokenizers, pywhatkit, transformers
Successfully installed Click-8.2.1 Flask-3.1.1 Pillow-11.2.1 SpeechRecognition-3.14.3 beautifulsoup4-4.13.4 blinker-1.9.0 certifi-2025.4.26 charset-normalizer-3.4.2 colorama-0.4.6 comtypes-1.4.11 dlib-19.24.9 face-recognition-models-0.3.0 face_recognition-1.3.0 filelock-3.18.0 fsspec-2025.5.1 huggingface-hub-0.32.0 idna-3.10 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.2 mouseinfo-0.1.3 mpmath-1.3.0 networkx-3.4.2 numpy-2.2.6 opencv-python-4.11.0.86 packaging-25.0 pyautogui-0.9.54 pygame-2.6.1 pygetwindow-0.0.9 pyjokes-0.8.3 pymsgbox-1.0.9 pyperclip-1.9.0 pypiwin32-223 pyrect-0.2.0 pyscreeze-1.0.1 pyttsx3-2.98 pytweening-1.2.0 pywhatkit-5.4 pywin32-310 pyyaml-6.0.2 regex-2024.11.6 requests-2.32.3 safetensors-0.5.3 setuptools-80.8.0 soupsieve-2.7 sympy-1.14.0 tokenizers-0.21.1 torch-2.7.0 tqdm-4.67.1 transformers-4.52.3 typing-extensions-4.13.2 urllib3-2.4.0 werkzeug-3.1.3 wikipedia-1.4.0

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>pip install pygame speech_recognition pyttsx3 pywhatkit wikipedia pyjokes opencv-python face_recognition dlib transformers torch
Requirement already satisfied: pygame in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (2.6.1)
ERROR: Could not find a version that satisfies the requirement speech_recognition (from versions: none)
ERROR: No matching distribution found for speech_recognition

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>pip install pygame SpeechRecognition pyttsx3 pywhatkit wikipedia pyjokes opencv-python face_recognition dlib transformers torch
Requirement already satisfied: pygame in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (2.6.1)
Requirement already satisfied: SpeechRecognition in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (3.14.3)
Requirement already satisfied: pyttsx3 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (2.98)
Requirement already satisfied: pywhatkit in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (5.4)
Requirement already satisfied: wikipedia in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (1.4.0)
Requirement already satisfied: pyjokes in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (0.8.3)
Requirement already satisfied: opencv-python in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (4.11.0.86)
Requirement already satisfied: face_recognition in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (1.3.0)
Requirement already satisfied: dlib in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (19.24.9)
Requirement already satisfied: transformers in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (4.52.3)
Requirement already satisfied: torch in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (2.7.0)
Requirement already satisfied: typing-extensions in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from SpeechRecognition) (4.13.2)
Requirement already satisfied: comtypes in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyttsx3) (1.4.11)
Requirement already satisfied: pypiwin32 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyttsx3) (223)
Requirement already satisfied: pywin32 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyttsx3) (310)
Requirement already satisfied: Pillow in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pywhatkit) (11.2.1)
Requirement already satisfied: pyautogui in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pywhatkit) (0.9.54)
Requirement already satisfied: requests in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pywhatkit) (2.32.3)
Requirement already satisfied: Flask in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pywhatkit) (3.1.1)
Requirement already satisfied: beautifulsoup4 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from wikipedia) (4.13.4)
Requirement already satisfied: charset-normalizer<4,>=2 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from requests->pywhatkit) (3.4.2)
Requirement already satisfied: idna<4,>=2.5 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from requests->pywhatkit) (3.10)
Requirement already satisfied: urllib3<3,>=1.21.1 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from requests->pywhatkit) (2.4.0)
Requirement already satisfied: certifi>=2017.4.17 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from requests->pywhatkit) (2025.4.26)
Requirement already satisfied: numpy>=1.21.2 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from opencv-python) (2.2.6)
Requirement already satisfied: face-recognition-models>=0.3.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from face_recognition) (0.3.0)
Requirement already satisfied: Click>=6.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from face_recognition) (8.2.1)
Requirement already satisfied: filelock in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (3.18.0)
Requirement already satisfied: huggingface-hub<1.0,>=0.30.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (0.32.0)
Requirement already satisfied: packaging>=20.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (25.0)
Requirement already satisfied: pyyaml>=5.1 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (6.0.2)
Requirement already satisfied: regex!=2019.12.17 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (2024.11.6)
Requirement already satisfied: tokenizers<0.22,>=0.21 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (0.21.1)
Requirement already satisfied: safetensors>=0.4.3 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (0.5.3)
Requirement already satisfied: tqdm>=4.27 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from transformers) (4.67.1)
Requirement already satisfied: fsspec>=2023.5.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from huggingface-hub<1.0,>=0.30.0->transformers) (2025.5.1)
Requirement already satisfied: sympy>=1.13.3 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from torch) (1.14.0)
Requirement already satisfied: networkx in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from torch) (3.4.2)
Requirement already satisfied: jinja2 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from torch) (3.1.6)
Requirement already satisfied: setuptools in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from torch) (80.8.0)
Requirement already satisfied: colorama in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from Click>=6.0->face_recognition) (0.4.6)
Requirement already satisfied: mpmath<1.4,>=1.1.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from sympy>=1.13.3->torch) (1.3.0)
Requirement already satisfied: soupsieve>1.2 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from beautifulsoup4->wikipedia) (2.7)
Requirement already satisfied: blinker>=1.9.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from Flask->pywhatkit) (1.9.0)
Requirement already satisfied: itsdangerous>=2.2.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from Flask->pywhatkit) (2.2.0)
Requirement already satisfied: markupsafe>=2.1.1 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from Flask->pywhatkit) (3.0.2)
Requirement already satisfied: werkzeug>=3.1.0 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from Flask->pywhatkit) (3.1.3)
Requirement already satisfied: pymsgbox in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyautogui->pywhatkit) (1.0.9)
Requirement already satisfied: pytweening>=1.0.4 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyautogui->pywhatkit) (1.2.0)
Requirement already satisfied: pyscreeze>=0.1.21 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyautogui->pywhatkit) (1.0.1)
Requirement already satisfied: pygetwindow>=0.0.5 in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyautogui->pywhatkit) (0.0.9)
Requirement already satisfied: mouseinfo in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pyautogui->pywhatkit) (0.1.3)
Requirement already satisfied: pyrect in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from pygetwindow>=0.0.5->pyautogui->pywhatkit) (0.2.0)
Requirement already satisfied: pyperclip in c:\users\lavan\onedrive\desktop\virtualhumanoid\.venv_robot\lib\site-packages (from mouseinfo->pyautogui->pywhatkit) (1.9.0)

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>python robot.py
pygame 2.6.1 (SDL 2.28.4, Python 3.12.5)
Hello from the pygame community. https://www.pygame.org/contribute.html
==================================================
WARNING: `transformers` library not found. Local AI model will not be available.
Please install it: pip install transformers torch
 (For GPU, install PyTorch with CUDA: e.g., pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 )
==================================================
Main App: Loki Voice Assistant with GUI starting...
Main App: Launching Robot Logic Thread...
Robot Thread: Initializing assistant logic...
Main App: Initializing and running Robot Face GUI...
Robot Warning: Local AI (transformers library) is not installed. General conversation is disabled.
Robot Log: Loading known faces from known_faces/...
Robot Log: Loaded face - Ajay
Robot Log: Loaded face - Amar
Robot Log: Loaded face - Checkin
Robot Log: Loaded face - Sai
Robot Log: Loaded face - Varun
Robot Log: Loaded 5 known faces.
Robot Log: Face recognition cam... (CV2 window, 'q' to skip)
🤖 Bot: Hello Sai, it's great to see your face!
Robot Log: Critical listening error (e.g., no microphone?): Could not find PyAudio; check installation
🤖 Bot: I'm having trouble with my microphone input right now.
Robot Log: Critical listening error (e.g., no microphone?): Could not find PyAudio; check installation
🤖 Bot: I'm having trouble with my microphone input right now.
Robot Log: Critical listening error (e.g., no microphone?): Could not find PyAudio; check installation
🤖 Bot: I'm having trouble with my microphone input right now.
Robot Log: Critical listening error (e.g., no microphone?): Could not find PyAudio; check installation
🤖 Bot: I'm having trouble with my microphone input right now.
Robot Log: Critical listening error (e.g., no microphone?): Could not find PyAudio; check installation
🤖 Bot: I'm having trouble with my microphone input right now.
Robot Log: Critical listening error (e.g., no microphone?): Could not find PyAudio; check installation
🤖 Bot: I'm having trouble with my microphone input right now.
Main App: GUI loop has finished or an error occurred.
Main App: Signaling robot logic thread to stop...
Main App: Waiting for robot logic thread to join...
Main App: Robot logic thread did not shut down cleanly (timed out).
Main App: Application shutdown complete.
Traceback (most recent call last):
  File "C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid\robot.py", line 529, in <module>
    gui_instance.run_gui_loop() # This is blocking; runs until GUI window is closed
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid\gui.py", line 528, in run_gui_loop
    self.clock.tick(FPS_GUI)
KeyboardInterrupt
^C
(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>cpython -m pip show transformers
'cpython' is not recognized as an internal or external command,
operable program or batch file.

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>python -m pip show transformers
Name: transformers
Version: 4.52.3
Summary: State-of-the-art Machine Learning for JAX, PyTorch and TensorFlow
Home-page: https://github.com/huggingface/transformers
Author: The Hugging Face team (past and future) with the help of all our contributors (https://github.com/huggingface/transformers/graphs/contributors)
Author-email: transformers@huggingface.co
License: Apache 2.0 License
Location: C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid\.venv_robot\Lib\site-packages
Requires: filelock, huggingface-hub, numpy, packaging, pyyaml, regex, requests, safetensors, tokenizers, tqdm
Required-by:

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>python -m pip show torch
Name: torch
Version: 2.7.0
Summary: Tensors and Dynamic neural networks in Python with strong GPU acceleration
Home-page: https://pytorch.org/
Author: PyTorch Team
Author-email: packages@pytorch.org
License: BSD-3-Clause
Location: C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid\.venv_robot\Lib\site-packages
Requires: filelock, fsspec, jinja2, networkx, setuptools, sympy, typing-extensions
Required-by:

(.venv_robot) C:\Users\lavan\OneDrive\Desktop\VirtualHumanoid>python
Python 3.12.5 (tags/v3.12.5:ff3bc82, Aug  6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> import transformers
>>>
>>> print(transformers.__version__)
4.52.3
>>> import transformers
>>>
