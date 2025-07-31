
test:
	python -m pytest tests;

run:
	python app.py;

.SILENT: install
install:
	if [[ -z "$(pkg)" ]] || [[ -n "$$(cat requirements.txt | grep $(pkg))" ]]; then \
		pip install -r requirements.txt; \
	else \
		pip install "$(pkg)"; \
		if [ ! $? ]; then \
			version="$$(pip show $(pkg) | grep Version | cut -d ":" -f 2 | cut -c2- | head -n 1)"; \
			echo "$(pkg)==$${version}" >> requirements.txt; \
		fi \
	fi

.SILENT: uninstall
uninstall:
ifeq ($(pkg),)
	echo "Specify a package with pkg=<package>"; \
	exit 0;
else
	if [[ -n "$$(cat requirements.txt | grep $(pkg))" ]]; then \
		pip uninstall "$(pkg)" -y; \
		if [ ! $? ]; then \
			removal="$$(sed '/^$(pkg)==/d' ./requirements.txt)"; \
			if [[ -n "$$removal" ]]; then \
	echo "$$removal" > ./requirements.txt; \
			fi \
		fi \
	else \
		echo "The package '$(pkg)' is not installed."; \
	fi
endif

.SILENT: docker-compose-up
docker-compose-up:
ifeq ($(pkg),1)
	docker compose -f docker-compose.yml up -d;
else
	docker compose -f docker-compose.yml up -d --build;
endif

.SILENT: docker-compose-down;
docker-compose-down:
	docker compose -f docker-compose.yml down;
