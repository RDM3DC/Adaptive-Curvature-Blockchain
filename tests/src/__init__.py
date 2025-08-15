"""Proxy package to expose the project's `src` modules for tests."""
import os
__path__ = [os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))]
