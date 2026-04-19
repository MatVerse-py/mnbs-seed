---
name: matverse-system-analyst
description: Análise de arquitetura de sistemas web, avaliação de superfície de ataque, risco estrutural e prova criptográfica de execução. Use para analisar repositórios, APKs, sistemas distribuídos e infraestruturas de agentes cognitivos (como o MatVerse).
license: MIT
---

# MatVerse System Analyst

Esta skill capacita o Manus a atuar como um analista de arquitetura de sistemas avançados, avaliando superfícies de ataque, risco estrutural e a integridade de sistemas distribuídos, com foco especial em arquiteturas soberanas, pipelines cognitivos e provas criptográficas (como o ecossistema MatVerse).

## Quando usar esta skill

- Quando o usuário fornecer dumps de configuração web, repositórios Git, ou pacotes de aplicativos (APKs/binários) para análise de segurança e arquitetura.
- Para calcular métricas de risco estrutural, entropia de repositórios e integridade de sistemas.
- Para avaliar a consistência entre código-fonte (Git), execução (APK/Binário) e backend (API).
- Para analisar sistemas de agentes cognitivos, pipelines constitucionais (Ω-Gate) e provas determinísticas de execução.

## Princípios de Análise

Ao analisar um sistema, siga esta progressão de fases:

1. **Análise de Superfície (Fase 1):** Identifique endpoints, websockets, CDNs e integrações externas. Calcule o risco baseado na exposição.
2. **Análise Estrutural (Fase 2):** Avalie a entropia do repositório (ex: exposição de `.git`), a presença de segredos e a consistência entre artefatos (Source vs. Archive).
3. **Correlação Total (Fase 3):** Mapeie a ligação entre o cliente (APK), o backend (API) e a camada de skills/agentes. Avalie a presença de um enforcement engine (Ω-Gate).
4. **Prova Criptográfica (Fase 4 e 5):** Verifique se o sistema possui uma cadeia de integridade (hash + replay), ledger local (Merkle) e se a execução é determinística e inevitável.

## Modelos Matemáticos de Avaliação

Utilize os seguintes modelos formais em suas análises:

- **Risco Estrutural (CVaR):** Avalie o risco de eventos extremos (ex: exploração de WS, vazamento de Git).
- **Entropia Estrutural (H):** $H = -\sum p_i \log p_i$. Muita redundância (ex: `.git/objects`) indica baixa entropia real e alta entropia aparente.
- **Consistência Binário ↔ Source:** $\Delta = |Hash_{source} - Hash_{apk}| > 0$ indica quebra de reprodutibilidade.
- **Métrica de Integridade:** $IntegrityScore = \frac{VerifiedLinks}{TotalLinks}$.
- **Métrica de Confiança:** $Trust = P(Reproducibility) \cdot P(Determinism) \cdot P(Integrity)$.
- **Inevitability Score:** $I = \frac{VerifiedExecution}{TotalExecution}$. Meta é $I = 1.0$.

## Ferramentas e Scripts

A skill inclui scripts Python em `scripts/` para automatizar a análise:

- `scripts/config_analyzer.py`: Extrai endpoints de dumps HTML/JS e calcula o risco da superfície web.
- `scripts/archive_scanner.py`: Analisa arquivos ZIP em busca de `.git` exposto, APKs e possíveis segredos.
- `scripts/skill_validator.py`: Avalia o risco de execução de skills (chamadas externas, execução dinâmica, shell).
- `scripts/omega_gate.py`: Simula um enforcement engine (Ω-Gate) para validar contextos de execução de agentes.
- `scripts/proof_engine.py`: Simula a geração de provas criptográficas e um ledger Merkle local.

Para usar os scripts, execute-os via shell passando os arquivos alvo como argumento. Exemplo:
`python /home/ubuntu/skills/matverse-system-analyst/scripts/archive_scanner.py /caminho/para/arquivo.zip`

## Estrutura de Relatório

Ao entregar os resultados ao usuário, estruture o relatório da seguinte forma:

1. **Resumo Trivial:** Diagnóstico direto e objetivo do que foi encontrado.
2. **Matemática Robusta Aplicada:** Formalização do sistema, funções de fluxo, superfície de ataque e risco estrutural.
3. **Comparação e Análise Evolutiva:** Compare o sistema analisado com padrões de mercado (ex: SaaS centralizado vs. Soberano distribuído).
4. **Conclusão e Próximos Passos:** Indique claramente as falhas (ex: "APK não provado", "Backend não vinculado") e sugira a próxima fase de engenharia reversa ou implementação de provas.
