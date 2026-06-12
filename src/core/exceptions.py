from fastapi import HTTPException, status


class FintechException(HTTPException):
    """Base class for all business-logic related HTTP exceptions."""

    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class InsufficientFundsException(FintechException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient funds to complete transaction.",
        )


class IdempotencyConflictException(FintechException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="A transaction with this idempotency key is already processing.",
        )


class AccountNotFoundException(FintechException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested account does not exist.",
        )
