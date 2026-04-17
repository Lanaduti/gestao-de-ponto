# Importa a ferramenta de data do próprio Python
from datetime import date
from sistema_rh import SistemaRH

def iniciar_sistema():
    sistema = SistemaRH()

    print("Iniciando o Sistema de RH...\n")

    data_hoje = date.today()

    sistema.cadastrar_funcionario(
        nome="Alana Reis",
        cpf="99988877766",
        cargo="Estagiário",
        setor="Desenvolvimento",
        salario_base=1500.00,
        data_admissao=data_hoje 
    )

if __name__ == "__main__":
    iniciar_sistema()