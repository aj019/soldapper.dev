from uagents import Model

class WalletCheckRequest(Model):
    wallet_address: str

class WalletCheckResponse(Model):
    summary: str
