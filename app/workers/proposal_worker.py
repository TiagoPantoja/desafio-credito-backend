import json
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.sqs import get_sqs_client
from app.core.config import settings
from app.core.external_bank import ExternalBankClient
from app.modules.proposals.models import Proposal
from app.modules.clients.models import Client
from app.modules.users.models import User
from app.modules.tenants.models import Tenant


def process_messages():
    sqs = get_sqs_client()
    bank_client = ExternalBankClient()
    queue_url = settings.SQS_QUEUE_URL

    print("Worker iniciado. Aguardando mensagens")

    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )

        messages = response.get('Messages', [])
        for msg in messages:
            body = json.loads(msg['Body'])
            proposal_id = body['proposal_id']

            print(f"Processando proposta: {proposal_id}")

            db: Session = SessionLocal()
            try:
                proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
                if proposal:
                    client = db.query(Client).filter(Client.id == proposal.client_id).first()

                    payload = {
                        "cpf": client.cpf,
                        "amount": float(proposal.amount),
                        "installments": proposal.installments,
                        "webhook_url": f"http://host.docker.internal:8000/api/webhooks/bank-callback?proposal_id={proposal.id}"
                    }

                    print(f"Enviando proposta para banco: {payload}")
                    result = bank_client.simular(payload)

                    if "protocol" in result:
                        proposal.status = "processing"
                        proposal.external_protocol = result["protocol"]
                        print(f"Sucesso: Proposta {proposal_id} enviada. Protocolo: {proposal.external_protocol}")
                    else:
                        proposal.status = "error"
                        print(f"Erro: Banco recusou o envio da proposta {proposal_id}")

                    proposal.bank_response = result
                    db.commit()

                    sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=msg['ReceiptHandle']
                    )

            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                db.rollback()
            finally:
                db.close()


if __name__ == "__main__":
    process_messages()