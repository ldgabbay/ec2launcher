PKG_NAME = $(shell grep -E '^name = ' pyproject.toml | sed -E 's/^name = "(.*)"/\1/')
PKG_VERSION := $(shell grep -E '^version = ' pyproject.toml | sed -E 's/^version = "(.*)"/\1/')

BUILD_DIR = build
DIST_DIR = dist

SOURCE_FILES := $(shell find src -type f -name \*.py | sed 's: :\\ :g')


.PHONY : dist clean pypi pypitest

dist : $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl

$(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl : $(SOURCE_FILES)
	python3 -m build --wheel .

clean :
	rm -rf $(BUILD_DIR) src/$(PKG_NAME).egg-info

distclean : clean
	rm -rf $(DIST_DIR)

pypi : dist
	twine upload -r pypi $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl

testpypi : dist
	twine upload -r testpypi $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl
