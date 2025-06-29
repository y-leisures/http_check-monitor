# Project Overview

This repository provides a Lambda based monitoring application. It keeps track of the target website
status, stores monitoring information on S3 via SQLite and sends notifications to Slack.

The codebase is organized as follows:

- **`check_website/`** – Contains the Lambda source code.
  - `app.py` – Lambda handler that performs the checks and writes results to the database.
  - `notify_to_slack.py` – Utility for posting messages to Slack.
- **`layers/`** – Lambda Layer build files. `requirements.txt` defines packages shared by functions.
- **`template.yaml`** – AWS SAM template describing the Lambda function, roles and other resources.
- **`tests/`** – Pytest based unit tests. Run `pytest` to execute.
- **Configuration files** – `pyproject.toml`, `samconfig.toml`, Makefile and GitHub Actions workflows
  configure the development environment, CI and deployment.

## Key Points

1. **Python and Code Style** – The project uses Python 3.12 with dependencies managed by Poetry.
   Ruff formats code and performs static analysis while mypy handles type checking.
2. **AWS SAM Deployment** – `sam build` and `sam deploy` (available through the Makefile) build and
   deploy all AWS resources.
3. **Environment Variables** – Secrets such as the Slack webhook URL are passed via environment
   variables configured in `template.yaml`.
4. **Testing** – Unit tests are in the `tests/` directory and are executed with `pytest` as part
   of the CI workflow.

## Suggested Topics to Explore

- **AWS SAM / CloudFormation** – Understanding how resources are defined in `template.yaml` and
  deployed will clarify the application structure.
- **Lambda Layers** – `layers/requirements.txt` defines shared dependencies. Learn how layers keep
  Lambda functions lightweight and reusable.
- **CI/CD Workflow** – Review the GitHub Actions configuration to see how formatting checks, unit
  tests and deployments are automated.
- **AWS Integrations** – Become familiar with the AWS services used (SNS, S3, etc.) to simplify
  troubleshooting and feature additions.

This orientation should help new contributors grasp the project layout and common tasks quickly.
