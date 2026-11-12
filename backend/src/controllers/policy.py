from src.services import policy as service
def list_items():return service.list_policies()
def create(data):return service.create(data)
