# pyaba 

Uma plataforma open source para gerenciar inscrições em tutoriais que acontecem em eventos, feita para ajudar comunidades a organizar, divulgar e facilitar a participação em atividades técnicas e educacionais.

A estrutura do repositório foi pensada para ser simples de usar: frontend e backend estão juntos, facilitando a instalação, deploy e manutenção, seja para eventos pequenos ou grandes. Assim, qualquer pessoa ou comunidade pode subir rapidamente uma instância e começar a usar!

Tem uma versão rodando aqui no [tutoriais.rapadura.org](https://tutoriais.rapadura.org/) 😁

---

## Funcionalidades

- Cadastro e gerenciamento de eventos e tutoriais
- Inscrição online com confirmação por e-mail
- Controle de vagas, horários e instrutores
- Emissão automática de certificados em PDF para inscritos
- Painel administrativo (Django Admin)
- API RESTful para integrações e automações
- Frontend moderno com Quasar/Vue.js
- Templates de e-mail prontos para confirmação de inscrição

---

## Estrutura do Projeto

```
tutoriais/
├── backend/   # Django + DRF (API, models, admin, templates de e-mail)
├── frontend/  # Quasar (Vue.js) SPA
├── media/     # Uploads de imagens (eventos, instrutores)
├── static/    # Arquivos estáticos coletados do frontend e backend
├── templates/ # Templates globais (ex: index.html)
├── Dockerfile # Build fullstack (backend + frontend)
├── pyproject.toml, uv.lock # Dependências Python
└── README.md  # Este arquivo
```

---

## Como rodar localmente

### Pré-requisitos

- [uv](https://github.com/astral-sh/uv) para instalar o Python 3.11 e dependências do backend;
- [nvm](https://github.com/nvm-sh/nvm) para instalar o Node, [Quasar](https://quasar.dev/start/quasar-cli/) e outras dependêcnias do frontend;
- Docker (opcional, para rodar tudo em um só container);

### 1. Instale as dependências

**Backend:**
```bash
uv python install 3.11  # se você ainda não tem essa versão
cd tutoriais # no diretório do projeto
uv sync # isso vai criar o ambiente virtual e instalar as dependências
```

**Frontend:**
```bash
nvm install 20 # instalar node

# Existem várias formas de instalar o quasar, mostrarei com npm
npm i -g @quasar/cli

cd frontend
npm install
```

### 2. Variáveis de ambiente

Faça uma cópia do arquivo `.env.example` e preencha as variáveis de ambiente.

```bash
cp .env.example .env
```

O arquivo possui essa estrutura:

```
# Habilita o modo de depuração do Django. Use “True” em desenvolvimento e “False” em produção.
DEBUG=

# Chave secreta do Django, usada para criptografia de sessões e tokens. Mantenha em segredo!
SECRET_KEY=

# Lista de hosts permitidos a acessar a aplicação, separados por vírgula (ex: “meusite.com,localhost”).
ALLOWED_HOSTS=

# Endereço do servidor SMTP para envio de e‑mails (ex: “smtp.gmail.com”).
EMAIL_HOST=

# Usuário/login para autenticação no servidor de e‑mail.
EMAIL_HOST_USER=

# Senha correspondente ao EMAIL_HOST_USER para autenticação no servidor de e‑mail.
EMAIL_HOST_PASSWORD=

# Endereço de e‑mail padrão que aparecerá como remetente nas mensagens enviadas pela aplicação.
DEFAULT_FROM_EMAIL=

# URL base do site (ex: “https://meusite.com”). Usada em links de e‑mail e redirecionamentos.
SITE_URL=

# Diretório onde a aplicação vai armazenar todos os arquivos persistentes:
#   • Arquivos de mídia (uploads de usuário, imagens, PDFs etc.)
#   • Arquivo de banco de dados SQLite (se estiver usando sqlite)
# Cenário de uso: basta montar um volume ou conectar um bucket/storage a esse caminho
# dentro do container, e todos os seus dados ficarão persistidos e isolados ali.
STORAGE_BASE_DIR=
```


### 3. Rodando em modo desenvolvimento

**Backend:**
```bash
cd backend
python manage.py migrate
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
quasar dev
# ou
npx quasar dev
```

Acesse o frontend em http://localhost:9000 e o backend em http://localhost:8000 ou em http://localhost:9000/api/ (no arquivo quasar.config.js, existe um proxy onde as requisições feitas para /api apontam para http://localhost:8000).

Você vai reparar que o quasar vai servir a partir do caminho `/static/`, isso é para que, após o build do frontend, onde o resultado é um arquivo index.html e outros arquivos estáticos, o django consiga servir os arquivos estáticos (css/js/etc) do frontend com o whitenoise. Vamos injetar na nossa aplicação django o resultado do build do quasar. 😁

---

### 3. Rodando com Docker

```bash
docker build -t tutoriais .
docker run --env-file .env -p 8000:8000 tutoriais
```

---

## Contribuindo

- Pull requests são muito bem-vindos!
- Se quiser sugerir melhorias, abrir issues ou ajudar na documentação, fique à vontade.
- O objetivo é que qualquer comunidade possa usar, adaptar e evoluir a plataforma.

---

## Licença

MIT. Use, modifique e compartilhe!

---

## Sobre

Este projeto nasceu para facilitar a organização de eventos técnicos, oferecendo uma experiência simples para participantes e instrutores.

Feito com carinho pela comunidade, para a comunidade, porque conhecimento compartilhado faz toda a diferença! 💜

---

Dúvidas? Sugestões?  
Abra uma issue ou mande um e-mail para philippe@gonzaga.dev

---

**Vamos juntos construir comunidades mais fortes e eventos mais incríveis! 🚀**
