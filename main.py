from sistema_rh import SistemaRH

def iniciar_sistema():
    sistema = SistemaRH()

    print("Iniciando o Sistema de RH...\n")

    sistema.cadastrar_funcionario(
        nome="Ana Silva",
        cpf="111.222.333-44",
        cargo="Desenvolvedora Backend",
        setor="TI",
        salario_base=6500.00,
        data_admissao="15/03/2023"
    )

    sistema.cadastrar_funcionario(
        nome="Carlos Oliveira",
        cpf="555.666.777-88",
        cargo="Analista de RH",
        setor="Recursos Humanos",
        salario_base=4200.00,
        data_admissao="10/01/2024"
    )

    sistema.listar_funcionarios()

if __name__ == "__main__":
    iniciar_sistema()

    # É o arquivo que você vai mandar rodar digitando "python main.py" no terminal. 