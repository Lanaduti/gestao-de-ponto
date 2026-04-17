from funcionario import Funcionario

class SistemaRH:
    """Classe que gerencia o cadastro e a lista de funcionários."""
    
    def __init__(self):
        self.funcionarios = []

    def cadastrar_funcionario(self, nome, cpf, cargo, setor, salario_base, data_admissao):
        for f in self.funcionarios:
            if f.cpf == cpf:
                print(f"Erro: O CPF {cpf} já está cadastrado no sistema.")
                return False
            
        novo_funcionario = Funcionario(nome, cpf, cargo, setor, salario_base, data_admissao)
        self.funcionarios.append(novo_funcionario)
        print(f"✅ Funcionário(a) '{nome}' cadastrado(a) com sucesso!")
        return True

    def listar_funcionarios(self):
        print("\n--- Lista de Funcionários Cadastrados ---")
        if not self.funcionarios:
            print("Nenhum funcionário cadastrado no momento.")
        else:
            for f in self.funcionarios:
                print(f.exibir_dados())
        print("-" * 40)

        # Este arquivo importa o Funcionario e cuida de toda a lógica do sistema (cadastrar, listar, etc). 