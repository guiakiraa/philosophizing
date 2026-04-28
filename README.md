# 🧠 Philosophizing

> Agente autônomo que gera reflexões filosóficas diárias e envia por email — 
rodando 100% na nuvem, sem precisar de máquina ligada.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-black?style=flat&logo=openai)
![Firebase](https://img.shields.io/badge/Firestore-database-orange?style=flat&logo=firebase)
![GCP](https://img.shields.io/badge/GCP-Cloud%20Run-blue?style=flat&logo=googlecloud)
![Scheduler](https://img.shields.io/badge/Cloud%20Scheduler-daily-green?style=flat&logo=googlecloud)

---

## 📽️ Demo

![demo](assets/demo.png)

---

## ✨ O que faz

Todo dia em um horário fixo o agente:

1. Consulta o **Firestore** para ver todos os temas já enviados
2. Usa o **GPT-4o** para gerar uma reflexão completamente nova e nunca repetida
3. Formata e envia um **email HTML** com frase, contexto filosófico e pergunta para refletir
4. Salva o tema no **Firestore** para garantir que nunca se repita

---

## 📧 Exemplo de email recebido

```
💭 Reflexão do dia — 27/04/2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 FRASE DO DIA
"O amor não correspondido é o mais puro de todos,
pois nele não há expectativa de retorno."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 CONTEXTO
Filósofos como Platão já discutiam o amor não correspondido
no Banquete. Para ele, o amor é a busca pela metade perdida —
e quando essa busca não encontra resposta, revela o quanto
estamos dispostos a sentir sem garantias...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❓ PERGUNTA PARA REFLETIR
Você já deixou a timidez falar mais alto que o sentimento?
O que ficou dessa escolha?
```

---

## 🏗️ Arquitetura

```
Cloud Scheduler (todo dia às 08:00)
        │  OIDC token
        ▼
  Cloud Run (container privado)
        │
        ├── GPT-4o (gera reflexão com JSON Schema)
        │
        ├── Firestore (lê histórico + salva novo tema)
        │
        └── Gmail SMTP (envia o email formatado)

CI/CD (push → main)
        │
        ▼
  Cloud Build
        ├── docker build
        ├── push → Artifact Registry
        └── deploy → Cloud Run
```

---

## 🛠️ Tech Stack

| Camada | Tecnologia |
|---|---|
| LLM | OpenAI GPT-4o |
| Banco de dados | Google Firestore |
| Execução | GCP Cloud Run |
| Agendamento | GCP Cloud Scheduler |
| CI/CD | GCP Cloud Build |
| Registry | GCP Artifact Registry |
| Segredos | GCP Secret Manager |
| Email | Gmail SMTP |
| Linguagem | Python 3.11 |

---

## 📁 Estrutura do projeto

```
philosopher-agent/
│
├── src/
│   ├── agent/
│   │   ├── agent.py          # gera reflexão com GPT-4o
│   │   └── prompts.py        # system e user prompts
│   │
│   ├── database/
│   │   └── firestore.py      # lê e salva temas
│   │
│   ├── email/
│   │   └── sender.py         # envia email via Gmail SMTP
│   │
│   ├── scheduler/
│   │   └── main.py           # HTTP handler (@functions_framework.http)
│   │
│   └── logger.py             # logger centralizado
│
├── main.py                   # entry point exposto ao Cloud Run
├── Dockerfile
├── cloudbuild.yaml           # pipeline CI/CD
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup local

### 1. Clone o repositório
```bash
git clone https://github.com/guiakiraa/philosophizing.git
cd philosophizing
```

### 2. Crie o ambiente virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente
```bash
cp .env.example .env
```

Edite o `.env`:
```
OPENAI_API_KEY=sua_chave_openai
GMAIL_USER=seu_email@gmail.com
GMAIL_APP_PASSWORD=sua_app_password
TO_EMAIL=seu_email@gmail.com
GOOGLE_APPLICATION_CREDENTIALS=service-account.json
```

### 5. Configure o Firebase
- Crie um projeto no [GCP Console](https://console.cloud.google.com)
- Ative o Firestore em **Native Mode**
- Crie uma Service Account, adicione a role `Cloud Datastore User` e baixe o `service-account.json`
- Coloque o arquivo na raiz do projeto

### 6. Rode localmente
```bash
functions-framework --target=run --port=8080
# em outro terminal:
curl http://localhost:8080
```

---

## 🚀 Deploy no GCP (CI/CD)

O deploy é feito automaticamente via **Cloud Build** a cada push na branch `main`.

### Pré-requisitos (configuração única)

**1. Criar o repositório no Artifact Registry**
```bash
gcloud artifacts repositories create philosopher-agent \
  --repository-format=docker \
  --location=southamerica-east1
```

**2. Criar os secrets no Secret Manager**
```bash
echo -n "sua_chave" | gcloud secrets create OPENAI_API_KEY --data-file=-
echo -n "seu_email" | gcloud secrets create GMAIL_USER --data-file=-
echo -n "sua_app_password" | gcloud secrets create GMAIL_APP_PASSWORD --data-file=-
echo -n "destino@email.com" | gcloud secrets create TO_EMAIL --data-file=-
```

**3. Conceder permissões ao Cloud Run (Workload Identity)**

O Cloud Run usa a service account do projeto para acessar o Firestore — sem necessidade de `service-account.json` em produção.

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**4. Criar o trigger no Cloud Build**

Conecte o repositório no [Cloud Build Console](https://console.cloud.google.com/cloud-build/triggers) apontando para `cloudbuild.yaml`.

**5. Criar o job no Cloud Scheduler**
```bash
gcloud scheduler jobs create http philosopher-agent-daily \
  --location=southamerica-east1 \
  --schedule="0 8 * * *" \
  --uri="https://philosopher-agent-xxxx-uc.a.run.app" \
  --http-method=GET \
  --oidc-service-account-email=scheduler-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --time-zone="America/Sao_Paulo"
```

### Disparar manualmente
```bash
gcloud scheduler jobs run philosopher-agent-daily --location=southamerica-east1
```

---

## 💡 Temas abordados pelo agente

- Filosofia clássica e moderna
- Amor, paixão, timidez e relacionamentos
- Existencialismo e propósito de vida
- Dilemas morais e éticos
- Psicologia humana e comportamento
- Perguntas sem resposta definitiva
- Situações cotidianas com profundidade filosófica
