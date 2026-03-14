import pytest
from unittest.mock import MagicMock, patch
from app.modules.proposals.service import ProposalService
from fastapi import HTTPException
import uuid


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    with patch('app.modules.proposals.service.ProposalRepository', return_value=mock_repo):
        from sqlalchemy.orm import Session
        service = ProposalService(MagicMock(spec=Session))
        service.repository = mock_repo
        return service


@patch('app.modules.proposals.service.send_to_queue')
def test_create_proposal_sends_sqs(mock_sqs, service, mock_repo):
    user_id = uuid.uuid4()
    proposal_data = MagicMock()
    proposal_data.model_dump.return_value = {"amount": 1000}

    mock_proposal = MagicMock(id=uuid.uuid4(), tenant_id=uuid.uuid4())
    mock_repo.create.return_value = mock_proposal

    service.create_proposal(proposal_data, user_id)

    mock_repo.create.assert_called_once()
    mock_sqs.assert_called_once()


def test_webhook_idempotency(service, mock_repo):
    proposal_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = MagicMock(status="approved")

    response = service.update_from_webhook(proposal_id, {"status": "rejected"})

    assert "processada anteriormente" in response["message"]

    mock_repo.update_status.assert_not_called()


def test_include_proposal_wrong_status(service, mock_repo):
    proposal_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = MagicMock(status="pending")

    with pytest.raises(HTTPException) as exc:
        service.include_proposal(proposal_id)

    assert exc.value.status_code == 400
    assert "Apenas propostas aprovadas" in exc.value.detail


def test_update_from_webhook_not_found(service, mock_repo):
    proposal_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        service.update_from_webhook(proposal_id, {"status": "approved"})

    assert exc.value.status_code == 404


@patch('app.modules.proposals.service.ExternalBankClient')
def test_include_proposal_success(mock_bank_class, service, mock_repo):
    proposal_id = uuid.uuid4()
    mock_proposal = MagicMock(status="approved", external_protocol="PROTO-123")
    mock_repo.get_by_id.return_value = mock_proposal

    mock_bank_instance = mock_bank_class.return_value
    mock_bank_instance.incluir.return_value = {"status": "included", "protocol": "FINAL-123"}

    response = service.include_proposal(proposal_id)

    assert response["status"] == "included"
    assert mock_proposal.status == "included"
    service.db.commit.assert_called()


@patch('app.modules.proposals.service.ExternalBankClient')
def test_include_proposal_bank_rejection(mock_bank_class, service, mock_repo):
    proposal_id = uuid.uuid4()
    mock_repo.get_by_id.return_value = MagicMock(status="approved")

    mock_bank_instance = mock_bank_class.return_value
    mock_bank_instance.incluir.return_value = {"error": "Score insuficiente para inclusão"}

    with pytest.raises(HTTPException) as exc:
        service.include_proposal(proposal_id)

    assert exc.value.status_code == 400
    assert "recusou a inclusão" in exc.value.detail


@patch('app.modules.proposals.service.send_to_queue')
def test_create_proposal_sqs_failure(mock_sqs, service, mock_repo):
    mock_sqs.side_effect = Exception("Conexão SQS perdida")

    user_id = uuid.uuid4()
    proposal_data = MagicMock()
    mock_proposal = MagicMock(id=uuid.uuid4())
    mock_repo.create.return_value = mock_proposal

    result = service.create_proposal(proposal_data, user_id)

    assert result == mock_proposal
    mock_repo.create.assert_called_once()