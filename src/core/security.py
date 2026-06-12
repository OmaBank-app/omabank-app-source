import logging

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from src.core.config import settings

logger = logging.getLogger(__name__)


class KeyVaultManager:
    def __init__(self):
        self.vault_url = settings.KEY_VAULT_URL
        self.credential = None
        self.client = None

        if self.vault_url:
            try:
                # DefaultAzureCredential handles the Zero-Trust identity chain
                # It tries Env Vars -> Workload Identity -> Managed Identity -> Azure CLI
                self.credential = DefaultAzureCredential()
                self.client = SecretClient(
                    vault_url=self.vault_url,
                    credential=self.credential,
                )  # noqa: E501
                logger.info(
                    f"Successfully authenticated to Azure Key Vault: {self.vault_url}"
                )
            except Exception as e:
                logger.error(f"Failed to initialize Key Vault Client: {str(e)}")

    def get_secret(self, secret_name: str) -> str:
        """Fetch a secret securely from the vault."""
        # Fallback for local testing without a vault
        if settings.ENVIRONMENT == "local" or not self.client:
            logger.warning(
                f"Vault bypassed for {secret_name}. Using local mocks if available."
            )
            return None

        try:
            secret = self.client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Error fetching secret '{secret_name}': {str(e)}")
            raise RuntimeError(
                f"Critical security failure: Could not load {secret_name}"
            ) from e


vault = KeyVaultManager()


def load_dynamic_secrets():
    """Injects vault secrets into the application state prior to startup."""
    if settings.KEY_VAULT_URL:
        logger.info("Fetching production secrets from Azure Key Vault...")
        settings.DATABASE_URL = vault.get_secret("omabank-db-connection-string")
        settings.JWT_SECRET_KEY = vault.get_secret("omabank-jwt-secret")
    else:
        # Expected behavior during docker-compose local runs
        logger.info("KEY_VAULT_URL not set. Relying on local environment variables.")
        import os

        settings.DATABASE_URL = os.getenv("DATABASE_URL")
        settings.JWT_SECRET_KEY = os.getenv(
            "JWT_SECRET_KEY", "local-dev-unsafe-secret-key"
        )
