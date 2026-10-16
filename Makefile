PY = .venv/bin/python3
VENV = .venv
CFG = config.txt
MAIN = a_maze_ing.py
OTP = output_maze.txt
MYPY_F = --explicit-package-bases --warn-return-any \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

all: run

install:
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	# install the mlx library
	$(PY) -m pip install mlx-2.2-py3-none-any.whl
	$(PY) -m pip install -r requirements.txt
	
run: install
	$(PY) $(MAIN) $(CFG)

build:
	$(PY) -m build  	
	cp dist/mazegen-*.whl .

lint:
	flake8
	mypy . $(MYPY_F)

debug:
	$(PY) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf .venv .mypy_cache .pytest_cache build dist *.egg-info $(OTP) mazegen-*.whl mazegen-*.tar.gz
	find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: install run build lint debug clean