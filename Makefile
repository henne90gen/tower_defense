all : install test lint_fast lint type_check coverage executable

install :
	pip install -r requirements.txt

executable :
	pyinstaller --onefile --specpath bin --distpath bin/dist --workpath bin/build -p tower_defense tower_defense/__main__.py
	# --add-data ../tower_defense/res:res

run :
	python -m tower_defense

test :
	python -m unittest discover tests -v

coverage :
	python -m coverage run --source=tower_defense -m unittest discover tests -v && python -m coverage report -m

lint :
	-python -m pylint tower_defense

lint_fast :
	python -m flake8 tower_defense --max-line-length=120

type_check :
	python -m mypy tower_defense --ignore-missing-imports
