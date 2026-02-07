# Data Science Academy
# Mini-Projeto 2 - Aplicação Full-Stack de Sistema Bancário em Python com Programação Orientada a Objetos
# Módulo que define as classes de Conta (Abstrata, Corrente e Poupança).

# Importa a classe base abstrata e o decorador para métodos abstratos
from abc import ABC, abstractmethod

# Importa a classe datetime para registrar data e hora das transações
from datetime import datetime

# Importa exceção personalizada para saldo insuficiente
from dsautilitarios.exceptions import SaldoInsuficienteError

# Define a classe abstrata Conta, que serve como base para outros tipos de contas
class Conta(ABC):
    
    """
    Classe base abstrata para contas bancárias.
    Demonstra Herança e Encapsulamento.
    """

    # Atributo de classe que calcula quantas contas foram criadas
    _total_contas = 0

    # Construtor da classe
    def __init__(self, numero: int, cliente):
        
        # Número da conta (atributo protegido)
        self._numero = numero
        
        # Saldo da conta, inicializado em 0.0 (atributo protegido)
        self._saldo = 0.0
        
        # Referência ao cliente dono da conta
        self._cliente = cliente
        
        # Lista para armazenar histórico de transações
        self._historico = []
        
        # Incrementa o total de contas criadas
        Conta._total_contas += 1

    # Propriedade para acessar o saldo de forma controlada
    @property
    def saldo(self):

        """Getter para o saldo, permitindo acesso controlado."""
        return self._saldo

    # Método de classe para consultar o número total de contas
    @classmethod
    def get_total_contas(cls):

        """Método de classe para obter o número total de contas criadas."""

        return cls._total_contas

    # Método para realizar depósitos
    def depositar(self, valor: float):

        # Adiciona um valor ao saldo da conta.
        if valor > 0:

            # Incrementa o saldo
            self._saldo += valor

            # Registra a transação no histórico com data e hora
            self._historico.append((datetime.now(), f"Depósito de R${valor:.2f}"))
            print(f"Depósito de R${valor:.2f} realizado com sucesso.")
        
        else:
            
            print("Valor de depósito inválido.")

    # Método abstrato que deve ser implementado pelas subclasses
    @abstractmethod
    def sacar(self, valor: float):

        """Método abstrato para sacar um valor. Deve ser implementado pelas subclasses."""

        pass

    # Método para exibir o extrato da conta
    def extrato(self):

        """Exibe o extrato da conta."""
        print(f"\n--- Extrato da Conta Nº {self._numero} ---")
        print(f"Cliente: {self._cliente.nome}")
        print(f"Saldo atual: R${self._saldo:.2f}")
        print("Histórico de transações:")

        # Caso não haja transações registradas
        if not self._historico:
            print("Nenhuma transação registrada.")

        # Percorre o histórico e exibe cada transação
        for data, transacao in self._historico:
            print(f"- {data.strftime('%d/%m/%Y %H:%M:%S')}: {transacao}")
        print("--------------------------------------\n")

# Define a subclasse ContaCorrente
class ContaCorrente(Conta):

    """
    Subclasse que representa uma conta corrente.
    Demonstra Polimorfismo ao sobrescrever o método sacar.
    """

    # Construtor com limite padrão de cheque especial
    def __init__(self, numero: int, cliente, limite: float = 500.0):

        # Chama o construtor da classe base
        super().__init__(numero, cliente)

        # Define o limite de cheque especial
        self.limite = limite

    # Implementação do método sacar com cheque especial
    def sacar(self, valor: float):

        """Permite saque utilizando o saldo da conta mais o limite (cheque especial)."""

        if valor <= 0:
            print("Valor de saque inválido.")
            return

        # Calcula o saldo disponível (saldo + limite)
        saldo_disponivel = self._saldo + self.limite

        # Caso o valor do saque ultrapasse o saldo disponível
        if valor > saldo_disponivel:
            raise SaldoInsuficienteError(saldo_disponivel, valor, "Saldo e limite insuficientes.")
        
        # Deduz o valor do saque do saldo
        self._saldo -= valor

        # Registra a transação no histórico
        self._historico.append((datetime.now(), f"Saque de R${valor:.2f}"))
        print(f"Saque de R${valor:.2f} realizado com sucesso.")

# Define a subclasse ContaPoupanca
class ContaPoupanca(Conta):

    """Subclasse que representa uma conta poupança."""

    # Construtor da poupança, herda do construtor base
    def __init__(self, numero: int, cliente):
        super().__init__(numero, cliente)

    # Implementação do método sacar apenas com saldo disponível
    def sacar(self, valor: float):

        # Permite saque apenas se houver saldo suficiente na conta.
        if valor <= 0:
            print("Valor de saque inválido.")
            return

        # Verifica se há saldo suficiente
        if valor > self._saldo:
            raise SaldoInsuficienteError(self._saldo, valor)
            
        # Deduz o valor do saldo
        self._saldo -= valor
        
        # Registra a transação no histórico
        self._historico.append((datetime.now(), f"Saque de R${valor:.2f}"))
        print(f"Saque de R${valor:.2f} realizado com sucesso.")



