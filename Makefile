.PHONY: help up down logs seed bootstrap deploy destroy diff synth clean

# LocalStack accepts any credentials — these dummy values just need to exist.
CDK_ENV := AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=eu-west-2 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1

help:
	@echo "Platform Interview Substrate — available targets:"
	@echo "  make up         - start backend + localstack"
	@echo "  make down       - stop all services and remove volumes"
	@echo "  make logs       - tail logs from backend + localstack"
	@echo "  make seed       - migrate + re-seed fixtures"
	@echo "  make bootstrap  - CDK bootstrap against LocalStack (run once)"
	@echo "  make deploy     - CDK deploy all stacks to LocalStack"
	@echo "  make destroy    - CDK destroy all stacks in LocalStack"
	@echo "  make synth      - CDK synth (inspect the generated CloudFormation)"
	@echo "  make diff       - CDK diff against LocalStack"
	@echo "  make clean      - remove CDK artefacts"

up:
	docker compose up -d
	@echo "Waiting for LocalStack + backend..."
	@sleep 10
	@echo "Ready: backend at http://localhost:8000, localstack at http://localhost:4566"

down:
	docker compose down -v

logs:
	docker compose logs -f backend localstack

seed:
	docker compose exec backend python manage.py migrate --noinput
	docker compose exec backend python manage.py seed

bootstrap:
	cd infra && $(CDK_ENV) cdklocal bootstrap aws://000000000000/eu-west-2

deploy:
	cd infra && $(CDK_ENV) cdklocal deploy --all --require-approval never

destroy:
	cd infra && $(CDK_ENV) cdklocal destroy --all --force

synth:
	cd infra && $(CDK_ENV) cdklocal synth

diff:
	cd infra && $(CDK_ENV) cdklocal diff

clean:
	rm -rf infra/cdk.out infra/.cdk.staging
