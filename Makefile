publish:
	poetry build && \
	twine upload --repository pptx2md dist/*
