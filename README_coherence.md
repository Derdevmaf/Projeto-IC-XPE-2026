# Métrica de Coerência de Ensino (LO x PBL)

A métrica de Coerência de Ensino quantifica a organização e eficiência pedagógica da estrutura do curso de 0 a 1, onde 1 é o cenário ideal (relacionamento 1-para-1 com progressão perfeitamente linear). 

O cálculo é composto por 3 sub-métricas, cada uma refletindo um aspecto vital do aprendizado baseado em projetos apontado na fundamentação:

1. **$S_{coverage}$ (Cobertura)**: Proporção de Objetivos de Aprendizado (LOs) que são ativamente testados em pelo menos um PBL.
2. **$S_{balance}$ (Equilíbrio e Foco)**: A relação matemática que dita a "saúde" do volume de projetos, penalizando excesso (redundância) ou escassez (sobrecarga no aluno).
3. **$S_{progression}$ (Progressão de Aprendizado)**: Mede o tamanho do maior caminho cumulativo no grafo de dependências entre projetos, premiando estruturas lineares.

---

## 1. Cobertura de Objetivos ($S_{coverage}$)
Uma métrica simples para garantir que a ementa está sendo totalmente contemplada.
Seja:
- $T_{LO}$ = Quantidade total de LOs descritos para a disciplina.
- $U_{LO}$ = Quantidade de LOs únicos que foram mapeados em projetos como "sim" (necessários).

$$ S_{coverage} = \frac{U_{LO}}{T_{LO}} $$

---

## 2. Equilíbrio de Redundância e Sobrecarga ($S_{balance}$)
Se existirem muitos PBLs para poucos LOs, teremos redundância ou mapeamento ineficiente. Se tivermos poucos PBLs para muitos LOs, o aluno enfrentará sobrecarga cognitiva, tentando aprender muitos tópicos simultaneamente no mesmo projeto.

Seja:
- $T_{PBL}$ = Total de projetos mapeados na disciplina.
- $\beta$ (`IDEAL_PBL_PER_LO`) = Fator de complexidade esperado da disciplina (por padrão `1.0` para cenários ideais 1 para 1).
- $I_{PBL}$ = Quantidade ideal de PBLs ($T_{LO} \times \beta$).

A fórmula propõe uma penalidade linear pelo desvio da quantidade ideal, tendo como piso o zero:

$$ S_{balance} = \max\left(0, \ 1 - \frac{|T_{PBL} - I_{PBL}|}{I_{PBL}}\right) $$

**Exemplo:** Se temos 15 LOs e $\beta = 1.0$, o ideal são 15 projetos. Se a disciplina contiver 30 projetos, causará redundância e o desvio será de 15, zerando o score de equilíbrio.

---

## 3. Score de Progressão ($S_{progression}$)
O melhor cenário para a retenção do aluno é quando "cada novo projeto requer as habilidades dos LOs anteriores ($N-1$), criando uma sequência lógica e cumulativa". O código avalia os requisitos de cada PBL mapeando as relações de subconjuntos de LOs exigidos. 

Ao extrair o DAG (Direcioned Acyclic Graph) dos projetos, computamos o tamanho do **Maior Caminho Direcionado** ($L_{max}$), que indica a maior escadinha de dependências lógicas que os alunos devem percorrer.

Seja:
- $L_{max}$ = Quantidade de nós (PBLs) interligados em progressão de pré-requisito sequencial contínua.

$$ S_{progression} = \frac{L_{max}}{T_{PBL}} $$

Para um $S_{progression}$ igual a 1, todos os projetos da disciplina precisam figurar ativamente num único e longínquo caminho causal, atestando uma dependência unificada e linear de fim a fim.

---

## Métrica Final
O Score Coesivo Ponderado (variando de 0.00 a 1.00) se consolida somando ponderadamente cada fator.

$$ \text{Score} = (\omega_1 \times S_{coverage}) + (\omega_2 \times S_{balance}) + (\omega_3 \times S_{progression}) $$

Atualmente configurados como:
- $\omega_1$ (Cobertura) = 0.3
- $\omega_2$ (Equilíbrio) = 0.3
- $\omega_3$ (Progressão) = 0.4

*(A progressão carrega peso ligeiramente superior para garantir que o excesso arbitrário de dependências não lineares, como grafos em formato de "estrela", sejam punidos mais ativamente.)*
