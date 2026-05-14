def menu_funcionario():

    print("\n" + "="*35)
    print("MENU FUNCIONÁRIO")
    print("="*35)

    print("1 - Registro de Ponto")
    print("2 - Banco de Horas")
    print("3 - Contracheque")
    print("4 - Justificativas")
    print("5 - Meu Perfil")
    print("6 - Férias")
    print("7 - Ajuda")
    print("0 - Sair")

    return input("\nEscolha uma opção: ")


def submenu_ponto_funcionario():

    print("\n" + "="*35)
    print("PONTO")
    print("="*35)

    print("1 - Bater Ponto")
    print("2 - Ver Horas Trabalhadas")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")


def submenu_banco_horas_funcionario():

    print("\n" + "="*35)
    print("BANCO DE HORAS")
    print("="*35)

    print("1 - Ver Minhas Horas")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")


def submenu_contracheque_funcionario():

    print("\n" + "="*35)
    print("CONTRACHEQUE")
    print("="*35)

    print("1 - Ver Contracheque")
    print("2 - Exportar PDF")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")


def submenu_justificativa_funcionario():

    print("\n" + "="*35)
    print("JUSTIFICATIVAS")
    print("="*35)

    print("1 - Enviar Justificativa")
    print("2 - Ver Status")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")