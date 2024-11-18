publish:
	poetry build && \
	twine upload --repository pptx2md dist/*

format:
	pycln --config pyproject.toml
	isort pptx2md/*
	yapf -ir pptx2md/*.py
