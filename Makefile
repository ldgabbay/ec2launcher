PKG_NAME := $(shell python3 ./setup.py --name)
PKG_VERSION := $(shell python3 ./setup.py --version)

BUILD_DIR = build
DIST_DIR = dist

SOURCE_FILES := $(shell find src -type f -name \*.py | sed 's: :\\ :g')


.PHONY : dist clean pypi pypitest

dist : $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl

$(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl : $(SOURCE_FILES)
	python3 ./setup.py bdist_wheel --dist-dir $(DIST_DIR) --bdist-dir $(BUILD_DIR)

clean :
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(PKG_NAME).egg-info
	find . -name __pycache__ -type d -print0 | xargs -0 rm -rf
	find . -name \*.pyc -type f -delete

pypi : dist
	twine upload -r pypi $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl

testpypi : dist
	twine upload -r testpypi $(DIST_DIR)/$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl
