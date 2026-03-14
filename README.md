# API de Gerenciamento de Crédito

API desenvolvida para processar propostas de empréstimo. O sistema utiliza arquitetura baseada em eventos para garantir escalabilidade e integridade dos dados.

---

## Tecnologias

* **Linguagem:** Python 3.12
* **Framework:** FastAPI
* **Banco de Dados:** PostgreSQL
* **Mensageria:** AWS SQS via LocalStack
* **Infra:** Docker

---

## Arquitetura

O fluxo de dados segue um modelo assíncrono:
1. **API:** Recebe a proposta, valida os dados e a envia para uma fila SQS.
2. **Worker:** Consome as mensagens da fila e realiza a integração com o Banco Externo.
3. **Webhook:** O Banco Externo processa a análise e notifica a API através de um callback.
4. **Efetivação:** O endpoint de inclusão finaliza o contrato após a aprovação.

---

## Como Rodar

### 1. Subir a Infra

A infra está dockerizada, facilitando o setup.

### 1. Preparando o ambiente:

Crie o arquivo `.env` na raiz do projeto seguindo o `.env.example`:
```bash
cp .env.example .env
```

### 2. Subir os containers:
```bash
docker compose up --build -d
```

### 3. Executar testes unitários:
```bash
pytest app/tests/ -v
```

### 4. Passo-a-passo de como testar os endpoints:

Acesse a documentação Swagger em: `https://localhost:8000/docs`.

1. **Criar Cliente**
   * **Endpoint:** `POST /api/clients/`
   * **Body:**
     ```json
     {
       "name": "Tiago Pantoja",
       "cpf": "12345678901",
       "email": "tiago@exemplo.com",
       "birth_date": "1990-01-01",
       "phone": "91988887766"
     }
     ```
Copie o `id` retornado no JSON de resposta.

2. **Criar Proposta**
   * **Endpoint:** `POST /api/proposals/`
   * **Body:** Substitua o `client_id` pelo ID copiado acima
     ```json
     {
       "client_id": "COLE_O_ID_AQUI",
       "amount": 2500.00,
       "installments": 12
     }
     ```

3. **Acompanhamento**
   * **Endpoint:** `GET /api/proposals/{id}`
   * Verifique a transição automática do campo `status`:  
     `pending` -> `processing` -> `approved`.

4. **Finalizar Inclusão**
   * **Endpoint:** `POST /api/proposals/{id}/include`
   * **Ação:** Após a proposta constar como `approved`, execute este endpoint para efetivá-la no banco externo. 
   * **Resultado:** O status final deve ser `included`.

---

## Implementações

Checklist dos requisitos solicitados e a implementação de cada categoria.

### Requisitos Obrigatórios
* [x] **Código fonte:** Hospedado em repositório Git.
* [x] **README.md:** Explicações sobre o projeto e instruções.
* [x] **Migrations:** Alembic para controle de versão do banco.
* [x] **Seed de dados:** Script para popular `tenants` e `usuários`.
* [x] **Endpoints:** Todos os recursos da API operacionais.
* [x] **Fluxo Assíncrono:** Integração via fila com AWS SQS com LocalStack.
* [x] **Webhook:** Recebimento e processamento de callbacks do banco externo.
* [x] **Multi-tenancy:** Isolamento de dados entre diferentes tenants.
* [x] **Autenticação:** Proteção de rotas com JWT
* [x] **Testes Unitários:** 11 testes cobrindo `Service` e `Repository`.

### Diferenciais (Implementados)
* [x] **Dockerfile:** Arquivo otimizado para a API.
* [ ] **Rate Limiting:** Nginx para controle de tráfego.
* [x] **Idempotência:** Tratamento no Webhook para evitar reprocessamento.
* [x] **Tratamento de Erros:** Resiliência criando propostas caso o SQS esteja indisponível.
* [x] **Validação de CPF:** Pydantic para garantir integridade dos dados.
* [x] **Documentação Swagger:** Endpoints documentados e testáveis.

---
