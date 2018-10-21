env/done: env/bin/pip requirements.txt requirements-dev.txt
	env/bin/pip install -r requirements-dev.txt
	touch env/done

env/bin/pip:
	python3.6 -m venv env

requirements.txt: env/bin/pip-compile requirements.in
	env/bin/pip-compile --no-index requirements.in -o requirements.txt

requirements-dev.txt: env/bin/pip-compile requirements.in requirements-dev.in
	env/bin/pip-compile --no-index requirements.in requirements-dev.in -o requirements-dev.txt

env/bin/pip-compile: env/bin/pip
	env/bin/pip install pip-tools
