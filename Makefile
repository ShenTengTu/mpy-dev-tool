MICROPYTHON_FIRMWARE?=esp32-idf3-20191220-v1.12.bin
PORT?=/dev/ttyUSB0

.PHONY: format install-firmware download-dep

format:
	@black .

install-firmware:
	@./bin/esp-install-firmware.sh $(MICROPYTHON_FIRMWARE) $(PORT)

download-dep:
	@./bin/github-api.sh download_repo_contents micropython micropython tools/pyboard.py dev_tool/pyboard.py
	@./bin/github-api.sh  download_from_gist 5e40217db8f7a218b28f365a13a14c00 cli.py dev_tool/cli.py

