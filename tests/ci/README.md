# CI Tests 

This directory contains resources and scripts used for Continuous Integration testing.

## Structure

- `resources/`: Test files used in CI workflows
  - These files are either pre-committed or generated during the CI pipeline
- `scripts/`: Helper scripts used in CI workflows

## Notes

- The files in this directory are primarily used by GitHub Actions workflows
- For local testing, please use the tests in the `local/` directory
- The GitHub Actions workflow will generate additional test audio and video files as needed