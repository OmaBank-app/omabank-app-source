import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.domains.ledger.schemas import TransferRequest, TransferResponse
from src.domains.ledger.service import LedgerService
from src.worker.tasks import process_transfer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ledger", tags=["Ledger Operations"])


@router.post(
    "/transfer", response_model=TransferResponse, status_code=status.HTTP_202_ACCEPTED
)
async def transfer_funds(request: TransferRequest, db: AsyncSession = Depends(get_db)):
    """
    Initiate a secure funds transfer between two accounts.
    Returns a 202 Accepted, offloading the ACID double-entry math to background workers.
    """
    # Initialize the service layer with the database session
    service = LedgerService(db)

    # Execute business logic
    txn = await service.initiate_transfer(request)

    # TODO in Block 4: Offload the heavy ACID double-entry math to the Celery Worker
    process_transfer.delay(txn.id)

    return TransferResponse(
        transaction_id=txn.id,
        status=txn.status,
        message="Transfer queued for secure processing.",
    )
