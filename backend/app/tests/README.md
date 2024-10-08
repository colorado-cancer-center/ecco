# ECCO Backend Tests

This folder contains tests for the ECCO backend. The tests are written using the
[pytest](https://docs.pytest.org/en/stable/) framework.

The tests are organized into the following subfolders:
- `metadata_integrity`: Tests that our metadata agrees with our sources (e.g.,
  CancerInFocus, State Cancer Profiles data releases as they come out)
- `helpers`: Tests for small helper functions in the backend
- `integration`: Tests that require actual stack services, e.g. a running,
  populated database
