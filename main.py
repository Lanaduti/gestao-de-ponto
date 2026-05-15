from services.perfil_service import *
from datetime import date, datetime
from menus.menu_admin import *
from menus.menu_funcionario import *
from services.funcionario_service import *
from services.usuario_service import *
from services.ponto_service import *
from services.folha_service import *
from services.justificativa_service import *


def tela_login():

    while True:

        print("""
1 - Login
2 - Esqueci minha senha
0 - Sair
""")

        opcao = input("Escolha uma opção: ")

        # LOGIN
        if opcao == "1":

            email = input("E-mail: ")
            senha = input("Senha: ")

            usuario = login(email, senha)
            
            if usuario:

                print("\nLOGIN REALIZADO COM SUCESSO!")
                
                return usuario
            
            else:

                  print("\nEMAIL OU SENHA INCORRETOS!")
                
        elif opcao == "2":
            
            email = input("Digite seu e-mail (0 para sair): ")
            
            if email == "0":
                continue

            nova_senha = input("Digite sua nova senha: ")

            redefinir_senha(email, nova_senha)

        # SAIR
        elif opcao == "0":

            print("Saindo do sistema...")

            exit()

        else:

            print("Opção inválida!")

def iniciar_sistema():
    
 # Guarda informações do usuário logado 
    usuario_logado = tela_login()

    print(usuario_logado)

    print(f"\nTIPO DE USUÁRIO: {usuario_logado['tipo']}")

# Verifica o tipo de usuário para liberar menus diferentes
    tipo_usuario = usuario_logado["tipo"]

    while True:

        subopcao = None

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

                    salario_input = input("Novo salário: ")

                    novo_salario = float(salario_input) if salario_input else 0

                    vale_transporte = input(
                        "Utiliza vale transporte? (S/N): "
                    ).strip().upper()

                    email = input("Digite o e-mail do funcionário: ")

                    id_funcionario = cadastrar_funcionario(
                        nome,cpf,cargo,setor,
                        novo_salario,vale_transporte, date.today()
                    )

                    print("DEBUG ID GERADO:", id_funcionario)
                    
                    if id_funcionario:
                        cadastrar_usuario(email, "", "funcionario", id_funcionario)
                        print("""
Funcionário cadastrado!

O colaborador deverá usar
"Esqueci minha senha"
para criar a senha inicial.
""")
                    
                    else:
                        print("Erro ao cadastrar funcionário!")
    
                elif subopcao == "2":
                    
                    listar_funcionarios()
                    
                elif subopcao == "3":
                    
                    print("\n--- EDITAR FUNCIONÁRIO ---")
                    
                    id_func = int(input("Digite o ID: "))
                    funcionario = buscar_funcionario(id_func)
                    
                    if funcionario:

                        novo_nome = input(
                            f"Novo nome ({funcionario[0]}): "
                        ) or funcionario[0]

                        novo_cpf = input(
                            f"Novo CPF ({funcionario[1]}): "
                        ) or funcionario[1]

                        novo_cargo = input(
                            f"Novo cargo ({funcionario[2]}): "
                        ) or funcionario[2]

                        novo_setor = input(
                            f"Novo setor ({funcionario[3]}): "
                        ) or funcionario[3]

                        salario_input = input(
                            f"Novo salário ({funcionario[4]}): "
                        )
 
                        novo_salario = (
                            float(salario_input)
                            if salario_input
                            else funcionario[4]
                        )

                        editar_funcionario(
                            id_func,
                            novo_nome,
                            novo_cpf,
                            novo_cargo,
                            novo_setor,
                            novo_salario
                        )

                    else:
           
                        print("Funcionário não encontrado.")

                # EXCLUIR
                elif subopcao == "4":
                
                    print("\n--- EXCLUIR FUNCIONÁRIO ---")
                
                    id_func = int(input("Digite o ID: "))
                
                    excluir_funcionario(id_func)

            # PONTO
            elif opcao == "2":

                subopcao = submenu_ponto()

                if subopcao == "1":

                    print("\n--- BATER PONTO ---")

                    id_func = int(input("Digite o ID: "))

                    registrar_ponto(id_func)

                elif subopcao == "2":

                    print("\n--- HORAS TRABALHADAS ---")

                    id_func = int(input("Digite o ID: "))

                    calcular_horas_trabalhadas(id_func, date.today())

            # BANCO DE HORAS
            elif opcao == "3":

                subopcao = submenu_banco_horas_admin()

                if subopcao == "1":

                    print("\n--- CONSULTAR HORAS ---")

                    id_func = int(input("Digite o ID: "))

                    calcular_horas_trabalhadas(id_func, date.today())

                elif subopcao == "2":

                   id_func = int(input("Digite o ID: "))

                   ver_banco_horas(id_func)

            # FOLHA
            elif opcao == "4":

                subopcao = submenu_folha()

                if subopcao == "1":

                    print("\n--- CONTRACHEQUE ---")

                    id_func = int(input("Digite o ID: "))

                    gerar_contracheque(id_func)

                elif subopcao == "2":

                    print("\n--- EXPORTAR PDF ---")

                    id_func = int(input("Digite o ID: "))
                    mes = int(input("Digite o mês: "))
                    ano = int(input("Digite o ano: "))

                    exportar_relatorio_pdf(id_func, mes, ano)

            # JUSTIFICATIVAS
            elif opcao == "6":

                subopcao = submenu_justificativas()

                # LISTAR
                if subopcao == "1":

                    listar_justificativas()

                # APROVAR
                elif subopcao == "2":

                    id_just = int(input("Digite o ID da justificativa: "))

                    atualizar_status_justificativa(id_just, "Aprovada")

                # REJEITAR
                elif subopcao == "3":

                    id_just = int(input("Digite o ID da justificativa: "))

                    atualizar_status_justificativa(id_just, "Rejeitada")

                elif opcao == "8":
                    
                    id_func = usuario_logado["id_funcionario"]
                    
                    visualizar_perfil(id_func)
                                
                elif opcao == "0":

                    print("\nENCERRANDO SISTEMA...")
                     
                    break

                elif opcao in ["5", "7", "9"]:

                    print("\nFUNÇÃO AINDA EM DESENVOLVIMENTO.")

        # FUNCIONÁRIO

        else:

            # PONTO
            if opcao == "1":

                subopcao = submenu_ponto_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    registrar_ponto(id_func)

                elif subopcao == "2":

                    id_func = int(input("Digite seu ID: "))

                    calcular_horas_trabalhadas(id_func, date.today())

            # BANCO DE HORAS
            elif opcao == "2":

                subopcao = submenu_banco_horas_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    calcular_horas_trabalhadas(id_func, date.today())

            # CONTRACHEQUE
            elif opcao == "3":

                subopcao = submenu_contracheque_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    gerar_contracheque(id_func)

            # JUSTIFICATIVA
            elif opcao == "4":

                subopcao = submenu_justificativa_funcionario()

                if subopcao == "1":

                    id_func = int(input("Digite seu ID: "))

                    data_str = input("Digite a data: ")

                    data_falta = datetime.strptime(
                        data_str,"%d/%m/%Y"
                    ).date()

                    motivo = input("Digite o motivo: ")

                    comp = input(
                        "Haverá compensação? (S/N): "
                    ).strip().upper()

                    compensacao = "Sim" if comp == "S" else "Não"

                    enviar_justificativa(
                        id_func,
                        data_falta,
                        motivo,
                        compensacao
                    )
                    
            elif opcao == "5":
                
                id_func = usuario_logado["id_funcionario"]
                visualizar_perfil(id_func)
                                
            elif opcao == "8":
                
                print("\nFUNÇÃO AINDA EM DESENVOLVIMENTO")
                
                                
            elif opcao == "0":
                
                print("\nENCERRANDO SISTEMA...")
                     
                break


            elif opcao in ["6", "7"]:

                print("\nFUNÇÃO AINDA EM DESENVOLVIMENTO.")

if __name__ == "__main__":
    iniciar_sistema()
