from datetime import date, datetime
from sistema_rh import  SistemaRH 
from menus.menu_admin import *
from menus.menu_funcionario import *


# Login do sistema 
def tela_login(sistema):

    print("\n===== LOGIN DO SISTEMA =====")

    while True:

        email = input("E-mail: ")
        senha = input("Senha: ")

        usuario = sistema.login(email, senha)

        if usuario:

            print("\nLOGIN REALIZADO COM SUCESSO!")

            return usuario

        else:
            print("\nEMAIL OU SENHA INCORRETOS!")


def iniciar_sistema():

    sistema = SistemaRH()
    
 # Guarda informações do usuário logado 
    usuario_logado = tela_login(sistema)

    print(f"\nTIPO DE USUÁRIO: {usuario_logado['tipo']}")

# Verifica o tipo de usuário para liberar menus diferentes
    tipo_usuario = usuario_logado["tipo"]

    while True:

        # MOSTRA MENU CONFORME O TIPO
        if tipo_usuario == "admin":
            opcao = menu_admin()

        else:
            opcao = menu_funcionario()
  
        # ADMINISTRADOR
    
        if tipo_usuario == "admin":

            # FUNCIONÁRIOS
            if opcao == "1":

                subopcao = submenu_funcionarios()

                # CADASTRAR
                if subopcao == "1":

                    print("\n--- NOVO CADASTRO ---")

                    nome = input("Digite o Nome: ")
                    cpf = input("Digite o CPF: ")
                    cargo = input("Digite o Cargo: ")
                    setor = input("Digite o Setor: ")

                    salario = float(input("Digite o Salário Base: "))

                    vale_transporte = input(
                        "Utiliza vale transporte? (S/N): "
                    ).strip().upper()

                    sistema.cadastrar_funcionario(
                        nome,
                        cpf,
                        cargo,
                        setor,
                        salario,
                        vale_transporte,
                        date.today()
                    )

                # LISTAR
                elif subopcao == "2":

                    sistema.listar_funcionarios()

                # EDITAR
                elif subopcao == "3":

                    print("\n--- EDITAR FUNCIONÁRIO ---")

                    id_func = int(input("Digite o ID: "))

                    novo_nome = input("Novo nome: ")
                    novo_cpf = input("Novo CPF: ")
                    novo_cargo = input("Novo cargo: ")
                    novo_setor = input("Novo setor: ")
                    novo_salario = float(input("Novo salário: "))

                    sistema.editar_funcionario(
                        id_func,
                        novo_nome,
                        novo_cpf,
                        novo_cargo,
                        novo_setor,
                        novo_salario
                    )

                # EXCLUIR
                elif subopcao == "4":

                    print("\n--- EXCLUIR FUNCIONÁRIO ---")

                    id_func = int(input("Digite o ID: "))

                    sistema.excluir_funcionario(id_func)

            # PONTO
            elif opcao == "2":

                subopcao = submenu_ponto()

                if subopcao == "1":

                    print("\n--- BATER PONTO ---")

                    id_func = int(input("Digite o ID: "))

                    sistema.registrar_ponto(id_func)

                elif subopcao == "2":

                    print("\n--- HORAS TRABALHADAS ---")

                    id_func = int(input("Digite o ID: "))

                    sistema.calcular_horas_trabalhadas(
                        id_func,
                        date.today()
                    )

            # BANCO DE HORAS
            elif opcao == "3":

                subopcao = submenu_banco_horas_admin()

                if subopcao == "1":

                    print("\n--- CONSULTAR HORAS ---")

                    id_func = int(input("Digite o ID: "))

                    sistema.calcular_horas_trabalhadas(
                        id_func,
                        date.today()
                    )

            # FOLHA
            elif opcao == "4":

                subopcao = submenu_folha()

                if subopcao == "1":

                    print("\n--- CONTRACHEQUE ---")

                    id_func = int(input("Digite o ID: "))

                    sistema.gerar_contracheque(id_func)

                elif subopcao == "2":

                    print("\n--- EXPORTAR PDF ---")

                    id_func = int(input("Digite o ID: "))
                    mes = int(input("Digite o mês: "))
                    ano = int(input("Digite o ano: "))

                    sistema.exportar_relatorio_pdf(
                        id_func,
                        mes,
                        ano
                    )

            # JUSTIFICATIVAS
            elif opcao == "6":

                subopcao = submenu_justificativas()

                # LISTAR
                if subopcao == "1":

                    sistema.listar_justificativas()

                # APROVAR
                elif subopcao == "2":

                    id_just = int(input("Digite o ID da justificativa: "))

                    sistema.atualizar_status_justificativa(
                        id_just,
                        "Aprovada"
                    )

                # REJEITAR
                elif subopcao == "3":

                    id_just = int(input("Digite o ID da justificativa: "))

                    sistema.atualizar_status_justificativa(
                        id_just,
                        "Rejeitada"
                    )

            elif opcao == "0":

                print("\nENCERRANDO SISTEMA...")

                break

            elif opcao in ["5", "7", "8", "9"]:

                print("\nFUNÇÃO AINDA EM DESENVOLVIMENTO.")

        # FUNCIONÁRIO

        else:

            # PONTO
            if opcao == "1":

                subopcao = submenu_ponto_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    sistema.registrar_ponto(id_func)

                elif subopcao == "2":

                    id_func = int(input("Digite seu ID: "))

                    sistema.calcular_horas_trabalhadas(
                        id_func,
                        date.today()
                    )

            # BANCO DE HORAS
            elif opcao == "2":

                subopcao = submenu_banco_horas_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    sistema.calcular_horas_trabalhadas(
                        id_func,
                        date.today()
                    )

            # CONTRACHEQUE
            elif opcao == "3":

                subopcao = submenu_contracheque_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    sistema.gerar_contracheque(id_func)

            # JUSTIFICATIVA
            elif opcao == "4":

                subopcao = submenu_justificativa_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    data_str = input("Digite a data: ")

                    data_falta = datetime.strptime(
                        data_str,
                        "%d/%m/%Y"
                    ).date()

                    motivo = input("Digite o motivo: ")

                    comp = input(
                        "Haverá compensação? (S/N): "
                    ).strip().upper()

                    compensacao = "Sim" if comp == "S" else "Não"

                    sistema.enviar_justificativa(
                        id_func,
                        data_falta,
                        motivo,
                        compensacao
                    )

            elif opcao == "0":

                print("\nENCERRANDO SISTEMA...")

                break

            elif opcao in ["5", "6", "7"]:

                print("\nFUNÇÃO AINDA EM DESENVOLVIMENTO.")

if __name__ == "__main__":
    iniciar_sistema()