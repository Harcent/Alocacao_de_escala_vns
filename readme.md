# Alocação de Escalas com Metaheurística VNS

Este projeto aplica a metaheurística **Variable Neighborhood Search (VNS)** para resolver o problema de alocação de escalas mensais de trabalho, respeitando diversas restrições e preferências individuais. A implementação foi realizada em Python como parte do trabalho individual da disciplina **DCA3606 – Inteligência Artificial** (UFRN).

## 🧠 Descrição do Problema

O objetivo é alocar um conjunto de pessoas a turnos de trabalho durante um mês, respeitando:

- Número máximo de pessoas por turno;
- Número mínimo e máximo de turnos por pessoa;
- Restrições de descanso entre turnos consecutivos;
- Limite de turnos consecutivos;
- Preferências individuais por dias disponíveis.

## 🚀 Metaheurística Utilizada

A metaheurística escolhida foi a **Variable Neighborhood Search (VNS)**, implementada em duas variantes:

- `VNS_R`: Solução inicial gerada aleatoriamente.
- `VNS_G`: Solução inicial gerada por uma heurística gulosa.

Ambas variantes exploram diferentes estruturas de vizinhança e utilizam busca local para melhorar a solução corrente.

## 🔧 Requisitos

Certifique-se de ter Python 3.8+ instalado, além das seguintes bibliotecas:

```bash
pip install pandas numpy
```

O código-fonte completo, juntamente com os dados de entrada (arquivos JSON), está disponível no GitHub:

🔗 https://github.com/Harcent/Alocacao_de_escala_vns

## 📊 Resultados Obtidos

A abordagem VNS_G (com solução inicial gulosa) apresentou melhor desempenho em termos de custo e tempo de convergência.

## 💡 Conclusões

A combinação entre uma heurística gulosa de construção e a metaheurística VNS produziu soluções robustas e eficientes para o problema de alocação de escalas. A inicialização gulosa mostrou-se particularmente eficaz, reduzindo o custo final e o tempo computacional.
