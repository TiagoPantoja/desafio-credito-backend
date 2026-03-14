import httpx

class ExternalBankClient:
    def __init__(self):
        self.base_url = "http://localhost:8001"

    def simular(self, data: dict):
        return self._post("/api/simular", data)

    def incluir(self, data: dict):
        return self._post("/api/incluir", data)

    def consultar(self, protocol: str):
        try:
            response = httpx.get(f"{self.base_url}/api/consultar/{protocol}", timeout=10.0)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def cancelar(self, protocol: str):
        try:
            response = httpx.post(f"{self.base_url}/api/cancelar/{protocol}", timeout=10.0)
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _post(self, path: str, data: dict):
        try:
            endpoint = f"{self.base_url}{path}"
            response = httpx.post(endpoint, json=data, timeout=10.0)
            print(f"DEBUG Banco ({path}): {response.status_code} - {response.text}")
            return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}