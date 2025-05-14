use substreams::errors::Error;
use substreams_solana::pb::sf::solana::r#type::v1::Block;

pub mod pb;
use pb::gas::WalletGasSpent;

#[substreams::handlers::map]
fn map_wallet_gas_fees(block: Block) -> Result<WalletGasSpent, Error> {
    let target_wallet = "J2NeRzadyut3753Anb61Y3meTBfrAMDx66ow2RDP3nea";
    let target_wallet_bytes = target_wallet.as_bytes();

    let mut total_fees = 0_u64;

    for txn in block.transactions {
        if let Some(txn_data) = txn.transaction {
            let account_keys = txn_data.message.as_ref().map(|m| &m.account_keys);
            if let Some(keys) = account_keys {
                if keys.iter().any(|key| key == target_wallet_bytes) {
                    if let Some(meta) = txn.meta {
                        total_fees += meta.fee as u64;
                    }
                }
            }
        }
    }

    Ok(WalletGasSpent { lamports: total_fees })
}
