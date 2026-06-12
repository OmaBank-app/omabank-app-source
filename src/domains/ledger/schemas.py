from uuid import UUID

from pydantic import BaseModel, Field, condecimal


class TransferRequest(BaseModel):
    # The client MUST provide a unique key to prevent double-charging
    idempotency_key: str = Field(
        ..., description="Unique key for idempotent processing"
    )

    from_account_id: UUID
    to_account_id: UUID

    # Strictly enforce that amounts are positive and have exactly 2 decimal places
    amount: condecimal(gt=0, max_digits=15, decimal_places=2)

    class Config:
        json_schema_extra = {
            "example": {
                "idempotency_key": "req-98765-abcd",  # gitleaks:allow
                "from_account_id": "123e4567-e89b-12d3-a456-426614174000",
                "to_account_id": "987fcdeb-51a2-43d7-9012-345678901234",
                "amount": "150.50",
            }
        }


class TransferResponse(BaseModel):
    transaction_id: str
    status: str
    message: str
