ROOT_DIR := $(shell pwd)

PKG_NAME := $(shell python3 ./setup.py --name)
PKG_VERSION := $(shell python3 ./setup.py --version)

BUILD_DIR = build
DIST_DIR = dist

SOURCE_FILES := $(shell find src -type f -name \*.py | sed 's: :\\ :g')
GENERATED_FILES = \
	$(PKG_NAME).egg-info \
	$(PKG_NAME)-$(PKG_VERSION).tar.gz \
	$(PKG_NAME)-$(PKG_VERSION)-py3-none-any.whl


.PHONY : dist clean pypi pypitest

dist : $(SOURCE_FILES)
	python3 ./setup.py sdist --dist-dir $(DIST_DIR) bdist_wheel --dist-dir $(DIST_DIR) --bdist-dir $(BUILD_DIR)

clean :
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(PKG_NAME).egg-info
	find . -name __pycache__ -type d -print0 | xargs -0 rm -rf
	find . -name \*.pyc -type f -delete

pypi : dist
	twine upload -r pypi $(DIST_DIR)/*

testpypi : dist
	twine upload -r testpypi $(DIST_DIR)/*
