# Memória de Cálculo

Este repositório contém o código que exemplifica como criar um documento de memória de cálculo a partir do cômputo do IEER e do ISR. Usamos exemplo de uma empresa para calcular o IEER e o ISR. Para criação do documento, usamos o pandoc que cria um pdf a partir do output do terminal:

```bash
python compute.py | pandoc -o memoria_calculo.pdf
```

