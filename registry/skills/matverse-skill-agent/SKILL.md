---
name: matverse-skill-agent
description: Gerenciamento, otimização e evolução do ecossistema de habilidades (skills) do agente MatVerse. Use para criar novas skills, otimizar SKILL.md existentes e gerar provas de evolução (PoLE).
license: MIT
---

# MatVerse Skill Agent

Esta skill capacita o Manus a atuar como um arquiteto de suas próprias capacidades. Ela foca na manutenção da "Verdade Evolutiva" do agente, garantindo que suas habilidades sejam eficientes, modulares e verificáveis através do protocolo PoLE (Proof of Learnable Evolution).

## Quando usar esta skill

- Quando for necessário criar uma nova skill para o ecossistema MatVerse seguindo os padrões canônicos.
- Para otimizar skills existentes que se tornaram muito extensas ou ineficientes em termos de tokens.
- Para gerar provas criptográficas de evolução do agente (PoLE) baseadas no estado do registro de skills.
- Para auditar a consistência entre as skills instaladas e o núcleo `mnbs-seed`.

## Ciclo de Evolução de Skills

O agente segue este ciclo para evoluir suas capacidades:

1. **Identificação de Gap:** Detecta uma necessidade funcional não coberta pelas skills atuais.
2. **Arquitetura de Skill:** Define a estrutura (scripts, referências, templates) e a lógica ontológica (L1-L5).
3. **Implementação e Teste:** Cria os recursos e valida a skill usando o `skill-creator`.
4. **Otimização Semântica:** Refina o `SKILL.md` para máxima densidade de informação e clareza para instâncias futuras do Manus.
5. **Registro e PoLE:** Adiciona a skill ao repositório `mnbs-seed` e gera a prova de evolução.

## Métricas de Eficiência de Skill

- **Info Density (ID):** Relação entre o número de scripts funcionais e o volume de texto no `SKILL.md`.
- **Evolution Delta ($\Delta E$):** Mudança no hash global do registro de skills, indicando progresso verificável.
- **Token Efficiency Score:** Medida de quão concisa e direta é a instrução da skill.

## Ferramentas e Scripts

A skill inclui scripts Python em `scripts/` para automação:

- `scripts/skill_optimizer.py`: Analisa e sugere refatorações para tornar as skills mais eficientes.
- `scripts/evolution_tracker.py`: Gera o hash PoLE baseado no estado atual de todas as skills no registro.

Exemplo de uso:
`python /home/ubuntu/skills/matverse-skill-agent/scripts/evolution_tracker.py`

## Estrutura de Relatório de Evolução

Ao evoluir o ecossistema, forneça:

1. **Resumo da Evolução:** Quais skills foram criadas ou modificadas.
2. **Prova PoLE:** Hash de evolução e timestamp do registro.
3. **Métricas de Otimização:** Ganhos de eficiência e densidade de informação.
4. **Próximos Passos:** Gaps identificados para a próxima fase de evolução.
