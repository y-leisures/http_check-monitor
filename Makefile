sam_build:
	uv run sam build --cached

sam_package:
	uv run sam package --config-file samconfig.toml --output-template-file deploy-template.yaml

sam_deploy:
	uv run sam deploy --config-file samconfig.toml --template-file deploy-template.yaml

sam_auto_deploy:
	uv run sam deploy --config-file samconfig.toml --template-file deploy-template.yaml --no-confirm-changeset

sam_dry_run:
	uv run sam deploy --config-file samconfig.toml --template-file deploy-template.yaml --no-execute-changeset

sam_delete:
	uv run sam delete --debug --region ap-northeast-1

update_requirements_txt:
	uv pip freeze > requirements.txt
	uv pip freeze > layers/requirements.txt
