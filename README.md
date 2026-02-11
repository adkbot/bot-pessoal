# 🤖 ADK AGENT — Agente Pessoal Multimodal

> Agente de IA que **vê sua tela**, **ouve sua voz** e **controla seu computador** em tempo real usando a **Gemini Live API**.

---

## ⚡ Como Usar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar API Key
Edite o arquivo `.env` com sua chave do [Google AI Studio](https://aistudio.google.com):
```
GEMINI_API_KEY=sua_chave_aqui
```

### 3. Executar
```bash
python main.py
```

### 4. Usar o Agente
1. Clique em **▶ INICIAR AGENTE**
2. **Fale** pelo microfone — o agente ouve e responde por voz
3. **Digite** mensagens na caixa de texto
4. O agente **vê sua tela** em tempo real
5. Peça qualquer coisa: criar arquivos, instalar programas, abrir apps...

---

## 🔧 Skills Disponíveis

| Skill | Descrição |
|-------|-----------|
| `executar_comando` | Roda qualquer comando no terminal |
| `criar_arquivo` | Cria arquivos com conteúdo |
| `ler_arquivo` | Lê conteúdo de arquivos |
| `editar_arquivo` | Edita trechos de arquivos |
| `deletar_arquivo` | Deleta arquivos e pastas |
| `listar_arquivos` | Lista conteúdo de diretórios |
| `mover_arquivo` | Move/renomeia arquivos |
| `copiar_arquivo` | Copia arquivos e pastas |
| `instalar_pacote_pip` | Instala pacotes Python |
| `instalar_programa` | Instala programas (winget, choco) |
| `info_sistema` | Mostra CPU, RAM, disco |
| `listar_processos` | Lista processos ativos |
| `finalizar_processo` | Fecha processos |
| `abrir_aplicativo` | Abre aplicativos |
| `abrir_url` | Abre URLs no navegador |
| `pesquisar_arquivos` | Busca arquivos por nome |
| `pesquisar_conteudo` | Busca texto dentro de arquivos |
| `criar_pasta` | Cria pastas |
| **🎯 Visão Computacional** | |
| `detectar_texto_tela` | Detecta todos os textos na tela via OCR |
| `localizar_texto` | Encontra texto específico e retorna coordenadas |
| `localizar_elemento` | Localiza ícones/botões por template matching |
| `clicar_em_texto` | Localiza texto via OCR e clica automaticamente |
| `salvar_screenshot_debug` | Salva screenshot com anotações visuais |

---

## 📁 Estrutura

```
agente pessoal/
├── main.py              → Ponto de entrada
├── agent_core.py        → Conexão Gemini Live API
├── screen_capture.py    → Captura de tela (MSS)
├── audio_capture.py     → Microfone + alto-falante (PyAudio)
├── skills.py            → 18 skills de controle do PC
├── gui.py               → Interface dark premium (Tkinter)
├── requirements.txt     → Dependências Python
├── .env                 → Chave da API
└── README.md            → Este arquivo
```
