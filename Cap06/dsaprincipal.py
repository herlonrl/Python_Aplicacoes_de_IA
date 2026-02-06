
# Conteúdo do arquivo dsaprincipal.py

# Importa o módulo inteiro
import modulodsa

# Usa a função e a variável do módulo
mensagem = modulodsa.dsa_saudacao("Mundo")
print(mensagem)
print(f"O valor de PI do nosso módulo é: {modulodsa.PI}")

# Outra forma: importando itens específicos
from modulodsa import dsa_saudacao, PI

mensagem_direta = dsa_saudacao("Aluno DSA")
print(mensagem_direta)
print(f"Valor de PI importado diretamente: {PI}")
