from sqlalchemy import Column, String, Float, JSON, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
import uuid

Base = declarative_base()


class AuditLog(Base):
    """
    Immutable ledger for compliance. Every trade decision is recorded here
    to satisfy SEC/FINRA explainability requirements.
    """

    __tablename__ = "audit_log"

    decision_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String, index=True)
    agent_outputs = Column(JSON, nullable=False)
    portfolio_decision = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False)
    reasoning_summary = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class AuditManager:
    def __init__(self):
        db_uri = os.getenv(
            "POSTGRES_URI", "postgresql://postgres:postgres@localhost:5432/hedge_fund"
        )
        self.engine = create_engine(db_uri)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def log_decision(
        self,
        simulation_id: str,
        agent_outputs: dict,
        portfolio_decision: dict,
        confidence: float,
        reasoning: str,
    ):
        db = self.SessionLocal()
        try:
            log_entry = AuditLog(
                simulation_id=simulation_id,
                agent_outputs=agent_outputs,
                portfolio_decision=portfolio_decision,
                confidence_score=confidence,
                reasoning_summary=reasoning,
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()
