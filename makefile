help:
	@echo 'make:                 Display this message'
	@echo 'make clean:           Remove the compiled files (*.pyc, *.pyo)'
	@echo 'make test:            Test everything and display git status'
	@echo 'make pylint:          Test using pylint'
	@echo 'make flake8:          Test using flake8'
	@echo 'make pytest:          Test using py.test'
	@echo 'make todo:            Look for TODO and XXX markers in the source code'

clean:
	find reach -regex .\*\.py[co]\$$ -delete
	find reach -depth -name __pycache__ -type d -exec rm -r -- {} \;

TEST_PATHS = \
	$(shell find ./reach -name '*.py') \
	$(shell find ./tests -name '*.py') \
	./setup.py

pylint:
	@echo "Running pylint..."
	pylint $(TEST_PATHS)

flake8:
	@echo "Running flake8..."
	flake8

pytest:
	@echo "Running py.test tests..."
	py.test tests

todo:
	-@grep --color -Ion '\(TODO\|XXX\).*' -r reach

gitstatus:
	@git status

test: pylint flake8 pytest todo gitstatus
	@echo "Finished testing: All tests passed!"

.PHONY: clean default help test pylint flake8 pytest todo gitstatus
