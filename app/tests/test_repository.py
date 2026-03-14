import pytest
from unittest.mock import MagicMock
from app.modules.proposals.repository import ProposalRepository
from app.modules.proposals.models import Proposal
import uuid


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def repository(mock_db_session):
    return ProposalRepository(mock_db_session)


def test_get_proposal_by_id(repository, mock_db_session):
    proposal_id = uuid.uuid4()
    mock_proposal = Proposal(id=proposal_id)

    mock_db_session.query().filter().first.return_value = mock_proposal

    result = repository.get_by_id(proposal_id)

    assert result.id == proposal_id
    mock_db_session.query.assert_called()


def test_update_status_success(repository, mock_db_session):
    proposal_id = uuid.uuid4()
    mock_proposal = Proposal(id=proposal_id, status="pending")
    mock_db_session.query().filter().first.return_value = mock_proposal

    repository.update_status(proposal_id, "approved", "PROTO-123")

    assert mock_proposal.status == "approved"
    assert mock_proposal.external_protocol == "PROTO-123"
    mock_db_session.commit.assert_called_once()


def test_update_status_proposal_not_found(repository, mock_db_session):
    proposal_id = uuid.uuid4()
    mock_db_session.query().filter().first.return_value = None

    result = repository.update_status(proposal_id, "approved")

    assert result is None
    mock_db_session.commit.assert_not_called()


def test_create_proposal_with_tenant(repository, mock_db_session):
    from app.core.security import tenant_context

    user_id = uuid.uuid4()
    expected_tenant = uuid.uuid4()
    tenant_context.set(expected_tenant)

    proposal_data = {"amount": 5000, "installments": 24, "client_id": uuid.uuid4()}

    repository.create(proposal_data, user_id)

    args, _ = mock_db_session.add.call_args
    created_proposal = args[0]
    assert created_proposal.tenant_id == expected_tenant