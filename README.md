# AntiGravity Trading System 🚀

Sistema de trading institucional modular com gestão de risco, engine de decisão e suporte multi-plataforma.

## 🏗️ Arquitetura

```
├── main.py                 # Orquestrador central
├── config.yaml            # Configuração do sistema
│
├── core/                  # Núcleo de decisão
│   ├── decision_engine.py # Validação institucional
│   └── state_manager.py   # Gerenciamento de estado
│
├── action/                # Processamento de ações
│   ├── command_parser.py  # Parser de linguagem natural
│   └── action_router.py   # Roteamento de plataformas
│
├── risk/                  # Gestão de risco
│   ├── risk_engine.py     # Engine de risco
│   └── drawdown_guard.py  # Proteção de drawdown
│
├── execution/             # Camada de execução
│   └── trade_executor.py  # Executor de trades
│
├── skills/                # Registros de habilidades
│   ├── tradingview_skill_registry.py
│   ├── binance_skill_registry.py
│   ├── bybit_skill_registry.py
│   ├── mt5_skill_registry.py
│   └── system_skill_registry.py
│
├── profiles/              # Perfis de plataformas
│   ├── tradingview_profile.json
│   ├── binance_profile.json
│   ├── bybit_profile.json
│   └── mt5_profile.json
│
├── memory/                # Memória e tracking
│   ├── trade_journal.py   # Diário de trades
│   └── performance_tracker.py # Rastreamento de performance
│
└── logs/                  # Logs do sistema
```

## 🔥 Fluxo de Execução

1. **Usuário fala** → Comando em linguagem natural
2. **CommandParser** → Estrutura o comando
3. **DecisionEngine** → Valida estrutura e contexto
4. **RiskEngine** → Valida risco e limites
5. **ActionRouter** → Roteia para plataforma
6. **SkillRegistry** → Executa ação específica
7. **TradeExecutor** → Execução unificada

## ⚙️ Configuração

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente
Crie um arquivo `.env` com suas credenciais:

```env
# Binance
BINANCE_API_KEY=sua_api_key
BINANCE_API_SECRET=sua_api_secret

# Bybit
BYBIT_API_KEY=sua_api_key
BYBIT_API_SECRET=sua_api_secret

# MT5
MT5_ACCOUNT=seu_account
MT5_PASSWORD=sua_senha
MT5_SERVER=seu_servidor
```

**⚠️ SEGURANÇA**: O arquivo `.env` está protegido no `.gitignore` e NUNCA será enviado ao GitHub.

### 3. Ajustar config.yaml
Edite `config.yaml` para configurar:
- Limites de risco
- Plataformas ativas
- Parâmetros de decisão

## 🚀 Uso

### Modo Interativo
```bash
python main.py
```

### Exemplos de comandos

```
>> mudar timeframe para H4
>> comprar BTC quantidade 0.01
>> vender ETH
>> desenhar linha de tendência
>> aplicar fibonacci
```

## 🛡️ Gestão de Risco

O sistema possui **3 camadas de proteção**:

1. **DecisionEngine**: Valida estrutura institucional e RR ratio
2. **RiskEngine**: Limita drawdown e posições concorrentes
3. **DrawdownGuard**: Proteção ativa com trailing stops e breakeven

### Limites padrão (config.yaml)
- Risco por trade: 2%
- Drawdown diário máximo: 5%
- Drawdown total máximo: 10%
- Trades concorrentes: 3

## 📊 Tracking e Análise

- **TradeJournal**: Registra todos os trades com detalhes
- **PerformanceTracker**: Métricas em tempo real (win rate, PnL, drawdown)

Dados salvos em `memory/`:
- `trade_journal.json`
- `performance_metrics.json`

## 🔌 Plataformas Suportadas

| Plataforma | Tipo | Status |
|-----------|------|--------|
| TradingView | Charting | ✅ Estruturado |
| Binance | Crypto | ✅ Estruturado |
| Bybit | Futures | ✅ Estruturado |
| MT5 | Forex/CFD | ✅ Estruturado |

**Nota**: As integrações de API estão estruturadas mas requerem implementação final (marcadas com `# TODO`).

## 📝 Próximos Passos

1. Implementar integrações reais de API (Binance, Bybit, MT5)
2. Adicionar automação TradingView (Selenium/Playwright)
3. Integrar com Gemini API para parsing avançado
4. Adicionar backtesting engine
5. Criar dashboard web para monitoramento

## 🔒 Segurança

- ✅ `.env` protegido no `.gitignore`
- ✅ Credenciais nunca hardcoded
- ✅ Emergency stop em caso de drawdown excessivo
- ✅ Validação multicamadas antes de execução

## 📄 Licença

Projeto pessoal - Bot Pessoal (adkbot)
