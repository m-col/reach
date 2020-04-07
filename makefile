help:
	@echo 'make:                 Display this message'
	@echo 'make clean:           Remove the compiled files (*.pyc, *.pyo)'
	@echo 'make pylint:          Test using pylint'
	@echo 'make flake8:          Test using flake8'
	@echo 'make black:           Run black formatter'
	@echo 'make todo:            Look for TODO and XXX markers in the source code'

clean:
	find reach -regex .\*\.py[co]\$$ -delete
	find reach -depth -name __pycache__ -type d -exec rm -r -- {} \;

TEST_PATHS = \
	reach

pylint:
	@echo "Running pylint..."
	pylint --rcfile=setup.cfg $(TEST_PATHS)

flake8:
	@echo "Running flake8..."
	flake8 $(TEST_PATHS)

black:
	@echo "Running black..."
	black $(TEST_PATHS)

todo:
	-@grep --color -Ion '\(TODO\|XXX\).*' -r reach

.PHONY: clean default help test pylint flake8 todo
