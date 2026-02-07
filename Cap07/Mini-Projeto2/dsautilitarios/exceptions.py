# Data Science Academy
# Mini-Projeto 2 - Aplicação Full-Stack de Sistema Bancário em Python com Programação Orientada a Objetos
# Módulo para exceções customizadas da aplicação.

# Define a exceção para saldo insuficiente em operações de saque
class SaldoInsuficienteError(Exception):

    """Exceção levantada quando uma operação de saque excede o saldo disponível."""

    # Construtor da exceção
    def __init__(self, saldo_atual, valor_saque, mensagem="Saldo insuficiente para realizar o saque."):
        
        # Saldo atual da conta no momento do erro
        self.saldo_atual = saldo_atual
        
        # Valor solicitado para saque
        self.valor_saque = valor_saque
        
        # Mensagem detalhada de erro com saldo atual e valor do saque
        self.mensagem = f"{mensagem} Saldo atual: R${saldo_atual:.2f}, Tentativa de saque: R${valor_saque:.2f}"
        
        # Chama o construtor da classe Exception com a mensagem
        super().__init__(self.mensagem)

# Define a exceção para operações em contas inexistentes
class ContaInexistenteError(Exception):
    
    """Exceção levantada ao tentar operar em uma conta que não existe."""
    
    # Construtor da exceção
    def __init__(self, numero_conta, mensagem="A conta especificada não foi encontrada."):
        
        # Número da conta que não foi encontrada
        self.numero_conta = numero_conta
        
        # Mensagem detalhada de erro com o número da conta
        self.mensagem = f"{mensagem} Número da conta: {numero_conta}"
        
        # Chama o construtor da classe Exception com a mensagem
        super().__init__(self.mensagem)
