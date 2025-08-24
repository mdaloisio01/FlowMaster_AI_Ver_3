# tests/__init__.py
# Ensure tests can import project modules by injecting boot paths first.

from boot.boot_path_initializer import inject_paths
inject_paths()
