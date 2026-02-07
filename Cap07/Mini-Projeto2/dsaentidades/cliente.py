# Data Science Academy
# Mini-Projeto 2 - Aplicação Full-Stack de Sistema Bancário em Python com Programação Orientada a Objetos
# Módulo da Entidade Cliente

# Define a classe Cliente
class Cliente:

    # Método construtor que inicializa os atributos da classe
    def __init__(self, nome: str, cpf: str):
        
        # Atributo para armazenar o nome do cliente
        self.nome = nome
        
        # Atributo para armazenar o CPF do cliente
        self.cpf = cpf
        
        # Lista vazia para armazenar as contas associadas ao cliente
        self.contas = [] 

    # Método para adicionar uma conta à lista de contas do cliente
    def adicionar_conta(self, conta):
        
        # Insere o objeto conta na lista de contas
        self.contas.append(conta)

    # Método especial que define a representação em string do objeto
    def __str__(self):
        
        # Retorna uma string formatada com nome e CPF do cliente
        return f"Cliente: {self.nome} (CPF: {self.cpf})"






