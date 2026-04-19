---
name: matverse-antifragility-regen
description: Capacidade de regeneração de estado a partir de provas e análise de antifragilidade do sistema MatVerse. Use para reconstruir código/estado de ledgers causais e testar a resistência do sistema sob estresse (convexidade negativa).
license: MIT
---

# MatVerse Antifragility & Regeneration

Esta skill capacita o Manus a gerenciar a resiliência extrema do ecossistema MatVerse. Ela foca em dois pilares: a **Regeneração** (capacidade de reconstruir a "Verdade Executável" a partir de provas criptográficas e históricos de ledger) e a **Antifragilidade** (a propriedade de melhorar ou manter a estabilidade sob estresse e perturbação).

## Quando usar esta skill

- Quando houver corrupção de estado ou perda de código e for necessário reconstruir o sistema a partir de um `CausalLedger` ou objetos `.git`.
- Para realizar testes de estresse (Chaos Engineering) e medir a resposta do Ω-Gate.
- Para calcular a métrica formal de antifragilidade ($\partial^2\Omega/\partial\sigma^2$).
- Para validar se o sistema está operando em um regime de convexidade negativa (antifrágil).

## Princípios de Regeneração e Antifragilidade

### 1. Regeneração de Estado (Regen)
A regeneração é o processo de restaurar a integridade do sistema sem depender de backups centralizados.
- **Prova de Raiz (Merkle Root):** O estado é reconstruído aplicando-se a sequência de eventos do ledger e validando o hash final contra a raiz Merkle ancorada.
- **Reconstrução Git:** Recuperação de código-fonte a partir de objetos brutos em diretórios `.git` expostos ou arquivados.

### 2. Antifragilidade ($\partial^2\Omega/\partial\sigma^2 < 0$)
Um sistema é antifrágil se ele se beneficia da desordem. No MatVerse, isso é medido pela convexidade da função de governança Ω em relação ao estresse σ.
- **Injeção de Caos:** Introdução de latência, ruído semântico e falhas de integridade para observar a resposta do sistema.
- **Convexidade Negativa:** Se o score Ω cai menos do que o esperado (ou sobe) sob estresse crescente, o sistema é considerado antifrágil.

## Ferramentas e Scripts

A skill inclui scripts Python em `scripts/` para automação:

- `scripts/chaos_injector.py`: Injeta ruído controlado no estado do sistema para simular estresse.
- `scripts/state_reconstructor.py`: Valida provas Merkle e reconstrói o estado a partir de eventos.
- `scripts/convexity_analyzer.py`: Calcula a segunda derivada de Ω para determinar o grau de antifragilidade.

Exemplo de uso:
`python /home/ubuntu/skills/matverse-antifragility-regen/scripts/convexity_analyzer.py`

## Estrutura de Relatório de Resiliência

Ao realizar uma análise de regeneração ou antifragilidade, forneça:

1. **Diagnóstico de Regeneração:** Status da validação da prova (Merkle/Git) e integridade do estado reconstruído.
2. **Métrica de Antifragilidade:** Valor de $\partial^2\Omega/\partial\sigma^2$ e classificação (Frágil, Linear ou Antifrágil).
3. **Análise de Resposta ao Caos:** Como o sistema se comportou sob diferentes níveis de intensidade de ruído.
4. **Recomendações de Evolução:** Sugestões para ajustar os pesos do Ω-Gate ou fortalecer o `CausalLedger`.
