sam_build:
	poetry run sam build --cached

sam_package:
	poetry run sam package --config-file samconfig.toml --output-template-file deploy-template.yaml

sam_deploy:
	poetry run sam deploy --config-file samconfig.toml --template-file deploy-template.yaml

sam_auto_deploy:
	poetry run sam deploy --config-file samconfig.toml --template-file deploy-template.yaml --no-confirm-changeset

sam_dry_run:
	poetry run sam deploy --config-file samconfig.toml --template-file deploy-template.yaml --no-execute-changeset

sam_delete:
	poetry run sam delete --debug --region ap-northeast-1

update_requirements_txt:
	poetry export -f requirements.txt --output requirements.txt         --without-hashes
	poetry export -f requirements.txt --output layers/requirements.txt  --without-hashes
