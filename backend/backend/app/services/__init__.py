from backend.app.services.model_gateway import get_model_gateway
from backend.app.services.providers.base import ProviderAdapter

# convenience export for other modules
get_gateway = get_model_gateway
ProviderBase = ProviderAdapter
