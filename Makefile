all : install test lint_fast lint type_check coverage executable

install :
	pip install -r requirements.txt

executable :
	pyinstaller \
		--onefile \
		--specpath bin \
		--distpath bin/dist \
		--workpath bin/build \
		--add-data ../tower_defense/res:tower_defense/res \
		-p tower_defense \
		-n tower_defense \
		tower_defense/__main__.py

executable_run :
	./bin/dist/tower_defense

run :
	python -m tower_defense

test :
	python -m unittest discover tests -v

coverage :
	python -m coverage run --source=tower_defense -m unittest discover tests -v && python -m coverage report -m

lint :
	-python -m pylint tower_defense -j8
	-python -m pylint tests -j8

lint_fast :
	python -m flake8 tower_defense --max-line-length=120
	python -m flake8 tests --max-line-length=120

type_check :
	python -m mypy tower_defense --ignore-missing-imports
	python -m mypy tests --ignore-missing-imports

clean :
	rm -rf bin
