from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.ledger.models import Account, Transaction


class LedgerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_transaction_by_idempotency_key(self, key: str):
        """Check if a transaction with this key already exists."""
        stmt = select(Transaction).where(Transaction.idempotency_key == key)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_account(self, account_id: str):
        """Fetch an account by its UUID."""
        return await self.db.get(Account, account_id)

    async def create_pending_transaction(
        self, key: str, from_acct: str, to_acct: str, amount: float
    ):
        """Write the initial PENDING transaction to the ledger."""
        new_txn = Transaction(
            idempotency_key=key,
            from_account_id=from_acct,
            to_account_id=to_acct,
            amount=amount,
            status="PENDING",
        )
        self.db.add(new_txn)
        await self.db.commit()
        await self.db.refresh(new_txn)
        return new_txn
