---
name: matverse-deploy
description: Automação de deploy soberano, formalização de ambiente e análise de risco de implantação para o ecossistema MatVerse. Use para implantar artefatos (APKs, ZIPs, Monorepos) com garantias de integridade e prova criptográfica.
license: MIT
---

# MatVerse Deploy

Esta skill capacita o Manus a realizar implantações (deploys) de alta integridade no ecossistema MatVerse. Ela foca na transição da "Verdade Declarada" (código) para a "Verdade Executável" (runtime), garantindo que o processo seja auditável, determinístico e soberano.

## Quando usar esta skill

- Quando o usuário solicitar o deploy de um sistema, agente ou servidor MatVerse.
- Para validar se um ambiente de destino é seguro e livre de vazamentos estruturais (ex: `.git` exposto).
- Para gerar provas de integridade (hashes) de artefatos antes da implantação.
- Para orquestrar o pipeline de deploy seguindo a lógica ontológica L1 a L5.

## Fluxo de Deploy Soberano

O processo de deploy segue rigorosamente estas fases:

1. **Validação de Ambiente (L1):** Verificação de riscos estruturais e superfícies de ataque no ambiente de destino.
2. **Prova de Integridade (L2):** Geração de hashes determinísticos do artefato para garantir que o que está sendo implantado é exatamente o que foi auditado.
3. **Isolamento de Runtime (L3):** Configuração de contêineres ou ambientes sandbox para execução soberana.
4. **Implantação (L4):** Transferência e ativação do artefato no ambiente.
5. **Ancoragem de Prova (L5):** Registro da prova de deploy (ID + Hash) para auditoria futura.

## Métricas de Deploy

- **Deployment Risk (DR):** Calculado com base na exposição de segredos e histórico de Git.
- **Integrity Gap ($\Delta$):** Diferença entre o hash do código-fonte e o hash do artefato binário. O objetivo é $\Delta = 0$.
- **Sovereignty Score (S):** Grau de independência de infraestruturas SaaS centralizadas.

## Ferramentas e Scripts

A skill inclui scripts Python em `scripts/` para automação:

- `scripts/env_validator.py`: Analisa o diretório atual em busca de riscos de segurança antes do deploy.
- `scripts/sovereign_deployer.py`: Orquestra o pipeline de deploy e gera provas de integridade.

Exemplo de uso:
`python /home/ubuntu/skills/matverse-deploy/scripts/sovereign_deployer.py meu_agente.zip`

## Estrutura de Relatório de Deploy

Ao finalizar um deploy, forneça:

1. **Status do Deploy:** Sucesso/Falha e ID da implantação.
2. **Prova de Integridade:** Hash SHA-256 do artefato implantado.
3. **Análise de Risco:** Resultado do `env_validator.py`.
4. **Próximos Passos:** Recomendações para monitoramento via Ω-Gate ou auditoria forense.
