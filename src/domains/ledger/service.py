from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AccountNotFoundException, IdempotencyConflictException
from src.domains.ledger.repository import LedgerRepository
from src.domains.ledger.schemas import TransferRequest


class LedgerService:
    def __init__(self, db: AsyncSession):
        self.repo = LedgerRepository(db)

    async def initiate_transfer(self, request: TransferRequest):
        """
        Executes the business rules for initiating a transfer.
        Throws domain-specific exceptions if validation fails.
        """
        # 1. Idempotency Check: Prevent duplicate processing
        existing_txn = await self.repo.get_transaction_by_idempotency_key(
            request.idempotency_key
        )
        if existing_txn:
            raise IdempotencyConflictException()

        # 2. Account Validation: Ensure both parties exist
        from_acct = await self.repo.get_account(str(request.from_account_id))
        to_acct = await self.repo.get_account(str(request.to_account_id))

        if not from_acct or not to_acct:
            raise AccountNotFoundException()

        # 3. Create the PENDING transaction state
        new_txn = await self.repo.create_pending_transaction(
            key=request.idempotency_key,
            from_acct=str(request.from_account_id),
            to_acct=str(request.to_account_id),
            amount=request.amount,
        )

        return new_txn
