if [ ! -d "env" ]; then
	python -m venv env
	source env/bin/activate
	pip install -r requirements.txt
else
  source env/bin/activate
fi

python main.py
