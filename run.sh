if [ ! -d "env" ]; then
	python -m venv env
	source env/bin/activate
	pip install -r requirements.txt
	python main.py
else
  source env/bin/activate
  python main.py
fi
