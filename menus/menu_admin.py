def menu_admin():

    print("\n" + "="*35)
    print("MENU ADMINISTRADOR")
    print("="*35)

    print("1 - Funcionários")
    print("2 - Registro de Ponto")
    print("3 - Banco de Horas")
    print("4 - Folha de Pagamento")
    print("5 - Escalas")
    print("6 - Justificativas")
    print("7 - Férias")
    print("8 - Meu Perfil")
    print("9 - Ajuda")
    print("0 - Sair")

    return input("\nEscolha uma opção: ")

def submenu_funcionarios():

    print("\n" + "="*35)
    print("FUNCIONÁRIOS")
    print("="*35)

    print("1 - Cadastrar Funcionário")
    print("2 - Listar Funcionários")
    print("3 - Editar Funcionário")
    print("4 - Excluir Funcionário")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")

def submenu_ponto():

    print("\n" + "="*35)
    print("REGISTRO DE PONTO")
    print("="*35)

    print("1 - Registrar Ponto")
    print("2 - Ver Horas Trabalhadas")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")

def submenu_folha():

    print("\n" + "="*35)
    print("FOLHA DE PAGAMENTO")
    print("="*35)

    print("1 - Gerar Contracheque")
    print("2 - Exportar PDF")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")

def submenu_justificativas():

    print("\n" + "="*35)
    print("JUSTIFICATIVAS")
    print("="*35)

    print("1 - Listar Justificativas")
    print("2 - Aprovar Justificativa")
    print("3 - Rejeitar Justificativa")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")

def submenu_banco_horas_admin():

    print("\n" + "="*35)
    print("BANCO DE HORAS")
    print("="*35)

    print("1 - Calcular Horas Trabalhadas")
    print("2 - Ver Banco de Horas")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")