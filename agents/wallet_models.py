from uagents import Model

class WalletCheckRequest(Model):
    wallet_address: str

class WalletCheckResponse(Model):
    summary: str


class SubstreamRequest(Model):
    start_block: int
    stop_block: int
    module: str
    package_url: str

class SubstreamResponse(Model):
    output: str