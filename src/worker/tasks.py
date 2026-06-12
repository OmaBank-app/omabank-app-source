import asyncio
import logging

from sqlalchemy import select

from src.core.database import AsyncSessionLocal
from src.domains.ledger.models import Transaction
from src.worker.celery_app import celery_instance

logger = logging.getLogger(__name__)


async def async_process_transfer(transaction_id: str):
    """The actual async database logic to finalize a transfer."""
    async with AsyncSessionLocal() as db:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        txn = (await db.execute(stmt)).scalar_one_or_none()

        if not txn:
            logger.error(f"Transaction {transaction_id} not found in DB.")
            return False

        try:
            # Simulate heavy cryptographic signing or external banking API call
            await asyncio.sleep(2)

            # Finalize the transaction
            txn.status = "COMPLETED"
            await db.commit()
            logger.info(f"Successfully processed transfer: {transaction_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to process transfer {transaction_id}: {str(e)}")
            txn.status = "FAILED"
            await db.commit()
            return False


@celery_instance.task(name="process_transfer", bind=True, max_retries=3)
def process_transfer(self, transaction_id: str):
    """
    Celery wrapper to run the async database operation.
    Retries up to 3 times if the external network drops.
    """
    logger.info(f"Worker received transaction: {transaction_id}")
    try:
        # FIX: Create a new event loop specifically for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(async_process_transfer(transaction_id))

        # Clean up the loop when finished
        loop.close()

        return result
    except Exception as exc:
        logger.error(f"Task failed, retrying... {exc}")
        raise self.retry(exc=exc, countdown=5) from exc
