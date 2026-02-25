import pytest
import sys
import os
import json
import importlib
from uuid import uuid4, UUID

# --- CONFIGURATION DES CHEMINS ---
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
services_path = os.path.join(root_path, 'services')

def setup_service_context(service_name):
    """
    Nettoie radicalement l'environnement Python pour isoler le service testé.
    """
    # 1. On purge les modules 'domain', 'application', 'infrastructure' du cache
    prefixes_to_clean = ('domain', 'application', 'infrastructure')
    for mod_name in list(sys.modules.keys()):
        if any(mod_name.startswith(p) for p in prefixes_to_clean):
            del sys.modules[mod_name]

    # 2. Nettoyage de sys.path (on enlève les anciens services)
    for folder in os.listdir(services_path):
        full_p = os.path.join(services_path, folder)
        if full_p in sys.path:
            sys.path.remove(full_p)

    # 3. Ajout du service actuel (Underscore ou Tiret)
    current_path = os.path.join(services_path, service_name)
    if not os.path.exists(current_path):
        current_path = os.path.join(services_path, service_name.replace('_', '-'))
    
    sys.path.insert(0, current_path)
    importlib.invalidate_caches()

# ==============================================================================
# TESTS SERVICES INDIVIDUELS
# ==============================================================================

def test_product_service_logic(mocker):
    setup_service_context('product_service')
    from application.services import ProductApplicationService
    from application.dtos import ProductCreateDTO
    mock_uow, mock_pub = mocker.MagicMock(), mocker.MagicMock()
    mocker.patch('application.services.ProductRepository')
    service = ProductApplicationService(mock_uow, event_dispatcher=mock_pub)
    dto = ProductCreateDTO(name="PC", description="Fast", category="Tech")
    result = service.create_product(dto)
    assert result.name == "PC"

def test_customer_creation(mocker):
    setup_service_context('customer_service')
    from infrastructure.db.repositories import CustomerRepository
    from domain.models import Customer
    mock_session = mocker.MagicMock()
    repo = CustomerRepository(mock_session)
    new_cust = Customer(name="Jean", email="jean@test.com")
    repo.add(new_cust)
    assert mock_session.add.called

def test_pricing_repository_logic(mocker):
    setup_service_context('pricing_service')
    from infrastructure.db.repositories import PriceRepository
    mock_db_price = mocker.MagicMock()
    mock_db_price.value = 10.0
    repo = PriceRepository(mocker.MagicMock())
    mocker.patch.object(repo, '_get_db_obj', return_value=mock_db_price)
    repo.update_price(uuid4(), 15.0)
    assert mock_db_price.value == 15.0

def test_inventory_stock_reduction(mocker):
    setup_service_context('inventory_service')
    from infrastructure.db.repositories import InventoryRepository
    mock_stock = mocker.MagicMock()
    mock_stock.quantity = 100
    repo = InventoryRepository(mocker.MagicMock())
    mocker.patch.object(repo, '_get_db_obj', return_value=mock_stock)
    repo.update_quantity(uuid4(), UUID("00000000-0000-0000-0000-000000000001"), -10)
    assert mock_stock.quantity == 90

def test_order_creation_with_multiple_lines(mocker):
    setup_service_context('order_service')
    from domain.models import Order, OrderLine
    from infrastructure.db.repositories import OrderRepository
    mock_session = mocker.MagicMock()
    repo = OrderRepository(mock_session)
    order = Order(customer_id=uuid4(), total_amount=150.0, lines=[OrderLine(product_id=uuid4(), quantity=1)])
    repo.create_order(order)
    assert mock_session.add.call_count == 2

# ==============================================================================
# TEST GATEWAY SERVICE (AGRÉGATION)
# ==============================================================================

def test_gateway_aggregation_logic(mocker):
    setup_service_context('gateway_service')
    
    # Import dynamique
    try:
        from application.service.product import ProductGatewayService
        patch_target = 'application.service.product.ZmqClient'
    except ImportError:
        from application.services.product import ProductGatewayService
        patch_target = 'application.services.product.ZmqClient'
    
    # Mock des réponses ZMQ beaucoup plus permissif
    def mock_request_side_effect(payload):
        # Si c'est une requête "Product" (contient action ou id seul)
        if "action" in payload or ("id" in payload and "product_id" not in payload):
            return {"id": str(uuid4()), "name": "Produit Mock", "description": "Test"}
        # Si c'est une requête Pricing ou Inventory (contient product_id)
        if "product_id" in payload:
            return {"price": 99.99, "total_quantity": 42}
        return {}

    # On patche le client ZMQ
    mock_zmq_class = mocker.patch(patch_target)
    mock_zmq_instance = mock_zmq_class.return_value
    mock_zmq_instance.request.side_effect = mock_request_side_effect
    
    # Exécution du service
    gw_service = ProductGatewayService()
    result = gw_service.get_full_product(str(uuid4()))
    
    # Vérification des clés agrégées
    assert "name" in result, f"La clé 'name' manque dans la réponse: {result}"
    assert result["name"] == "Produit Mock"
    assert result["price"] == 99.99
    assert result["stock"] == 42