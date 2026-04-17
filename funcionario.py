class Funcionario:
    """Classe que representa um funcionário na empresa."""
    
    def __init__(self, nome, cpf, cargo, setor, salario_base, data_admissao):
        self.nome = nome
        self.cpf = cpf
        self.cargo = cargo
        self.setor = setor
        self.salario_base = float(salario_base)
        self.data_admissao = data_admissao

    def exibir_dados(self):
        """Retorna os dados do funcionário formatados."""

        return (f"Nome: {self.nome} | CPF: {self.cpf} | Cargo: {self.cargo} "
                f"| Setor: {self.setor} | Salário: R${self.salario_base:.2f} "
                f"| Admissão: {self.data_admissao}") 
    
    # Este arquivo vai guardar apenas o modelo do que é um funcionário.
    