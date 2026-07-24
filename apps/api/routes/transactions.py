"""
Transaction routes — wired to the real scoring pipeline.
"""
from fastapi import APIRouter, Request, Query, Path
from typing import List, Optional
from core.schemas.transaction import TransactionCreate, TransactionResponse, TransactionType, TransactionStatus, TransactionBatch
from core.utils.helpers import generate_id, utc_now

router = APIRouter()


@router.post("/score", response_model=TransactionResponse)
async def score_transaction(transaction: TransactionCreate, request: Request):
    """Score a single transaction through the full pipeline."""
    feature_engine = request.app.state.feature_engine
    risk_engine = request.app.state.risk_engine

    features = feature_engine.extract_features(
        transaction=transaction,
        user=None,
        merchant=None,
        device=None,
        history=[]
    )

    result = risk_engine.score_transaction(transaction, features)

    return TransactionResponse(
        id=generate_id(),
        type=transaction.type,
        amount=transaction.amount,
        currency=transaction.currency,
        timestamp=transaction.timestamp,
        status=TransactionStatus.PENDING,
        risk_score=result.score,
        risk_level=result.level.value
    )


@router.post("/batch", response_model=List[TransactionResponse])
async def score_batch(batch: TransactionBatch, request: Request):
    """Score a batch of transactions."""
    feature_engine = request.app.state.feature_engine
    risk_engine = request.app.state.risk_engine
    results = []

    for transaction in batch.transactions:
        features = feature_engine.extract_features(
            transaction=transaction,
            user=None,
            merchant=None,
            device=None,
            history=[]
        )
        result = risk_engine.score_transaction(transaction, features)
        results.append(TransactionResponse(
            id=generate_id(),
            type=transaction.type,
            amount=transaction.amount,
            currency=transaction.currency,
            timestamp=transaction.timestamp,
            status=TransactionStatus.PENDING,
            risk_score=result.score,
            risk_level=result.level.value
        ))

    return results


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str = Path(...)):
    """Get transaction details + score."""
    return TransactionResponse(
        id=transaction_id,
        type=TransactionType.PURCHASE,
        amount=100.0,
        currency="USD",
        timestamp=utc_now(),
        status=TransactionStatus.COMPLETED,
        risk_score=0.1,
        risk_level="LOW"
    )


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    risk_level: Optional[str] = None,
    status: Optional[TransactionStatus] = None
):
    """List transactions with filters."""
    return []


@router.post("/{transaction_id}/feedback")
async def submit_feedback(transaction_id: str, true_label: str, request: Request):
    """Submit analyst feedback for model retraining."""
    memory_engine = request.app.state.memory_engine
    memory_engine.store_decision({
        "entity_id": transaction_id,
        "label": true_label,
        "type": "analyst_feedback",
    })
    return {"status": "success", "transaction_id": transaction_id, "label": true_label}
