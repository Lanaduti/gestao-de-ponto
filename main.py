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

        # LOGIN: valida email e senha no banco de dados
        if opcao == "1":

            email = input("E-mail: ")
            senha = input("Senha: ")

            #chama o service de usuario para autenticar
            usuario = login(email, senha)
            
            if usuario:

                    print(f"\nBEM-VINDO(A), {usuario['email'].split('@')[0].upper()}! 👋")
                    return usuario
            
            else:

                  print("\nEMAIL OU SENHA INCORRETOS!")

        #REDEFINIÇÃO DE SENHA: criar nova senha pelo email        
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
    """
    Função principal do sistema. 
    Após o login, redireciona o usuário para o menu correto
    com base no seu tipo: admin ou funcionário.
    """
    # Realiza o login e guarda informações do usuário logado 
    usuario_logado = tela_login()

    # Define o tipo de acesso: admin ou funcionário
    tipo_usuario = usuario_logado["tipo"]

    while True:

        subopcao = None

        # Exibe o menu de acordo com o perfil do usuário
        if tipo_usuario == "admin":
            opcao = menu_admin()

        else:
            opcao = menu_funcionario()
  
        # =============================================
        # ÁREA DO ADMINISTRADOR
        # =============================================
    
        if tipo_usuario == "admin":


        # Gestão de Funcionários
            if opcao == "1":

                subopcao = submenu_funcionarios()

                # CADASTRAR
                if subopcao == "1":

                    print("\n--- NOVO CADASTRO ---")

                    nome = input("Digite o Nome: ")
                    while True:
                        cpf = input("Digite o CPF (somente números, 11 dígitos): ").strip()
                        if len(cpf) == 11 and cpf.isdigit():
                            break
                        print("⚠️  CPF inválido! Digite apenas os 11 números.")

                    cargo = input("Digite o Cargo: ")
                    setor = input("Digite o Setor: ")

                    salario_input = input("Novo salário: ")

                    novo_salario = float(salario_input) if salario_input else 0

                    vale_transporte = input(
                        "Utiliza vale transporte? (S/N): "
                    ).strip().upper()

                    while True:
                        email = input("Digite o e-mail do funcionário: ").strip()
                        if "@" in email and "." in email.split("@")[-1]:
                            break
                        print("⚠️  E-mail inválido! Digite um e-mail válido (ex: nome@gmail.com)")

                    # Cadastra o funcionário e recebe o ID gerado pelo banco
                    id_funcionario = cadastrar_funcionario(
                        nome,cpf,cargo,setor,
                        novo_salario,vale_transporte, date.today()
                    )
                    
                    if id_funcionario:
                        # Cria o usuário vinculado ao funcionário cadastrado
                        cadastrar_usuario(email, "", "funcionario", id_funcionario)
                        print("""
Funcionário cadastrado!

O colaborador deverá usar
"Esqueci minha senha"
para criar a senha inicial.
""")
                    
                    else:
                        print("Erro ao cadastrar funcionário!")

                # LISTAR: exibe todos os funcionários cadastrados
                elif subopcao == "2":
                    
                    listar_funcionarios()
                    
                elif subopcao == "3":
                    
                    print("\n--- EDITAR FUNCIONÁRIO ---")
                    
                    id_func = int(input("Digite o ID: "))
                    funcionario = buscar_funcionario(id_func)
                  
                    if funcionario:
  
                        # Mantém o valor atual se nada for digitado
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

                        vt_input = input(
                            f"Utiliza vale transporte (S/N) ({funcionario[5]}): "
                        ).strip().upper() or funcionario[5]

                        editar_funcionario(
                            id_func,
                            novo_nome,
                            novo_cpf,
                            novo_cargo,
                            novo_setor,
                            novo_salario,
                            vt_input
                        )

                    else:
           
                        print("Funcionário não encontrado.")

                # EXCLUIR: remove o funcionário do banco de dados
                elif subopcao == "4":
                
                    print("\n--- EXCLUIR FUNCIONÁRIO ---")
                
                    id_func = int(input("Digite o ID: "))
                
                    excluir_funcionario(id_func)

           # REGISTRO DE PONTO 
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

            # FOLHA DE PAGAMENTO 
            elif opcao == "4":

                subopcao = submenu_folha()

                if subopcao == "1":

                    print("\n--- CONTRACHEQUE ---")

                    id_func = int(input("Digite o ID: "))

                    gerar_contracheque(id_func)

                # Exporta o contracheque em PDF filtrado por período
                elif subopcao == "2":
                     
                    print("\n--- EXPORTAR PDF ---")
                    id_func = int(input("Digite o ID: "))
                    print("Data de início:")
                    dia_i = int(input("  Dia: "))
                    mes_i = int(input("  Mês: "))
                    ano_i = int(input("  Ano: "))
                    print("Data de fim:")
                    dia_f = int(input("  Dia: "))
                    mes_f = int(input("  Mês: "))
                    ano_f = int(input("  Ano: "))
                    exportar_relatorio_pdf(id_func, dia_i, mes_i, ano_i, dia_f, mes_f, ano_f)

            # JUSTIFICATIVAS
            elif opcao == "6":

                subopcao = submenu_justificativas()

                
                if subopcao == "1":

                    listar_justificativas()

                
                elif subopcao == "2":

                    id_just = int(input("Digite o ID da justificativa: "))

                    atualizar_status_justificativa(id_just, "Aprovada")

                
                elif subopcao == "3":

                    id_just = int(input("Digite o ID da justificativa: "))

                    atualizar_status_justificativa(id_just, "Rejeitada")

            #  PERFIL DO ADMINISTRADOR 
            elif opcao == "8":
                print(f"""
            ===========================
            MEU PERFIL
            ===========================
            E-mail: {usuario_logado['email']}
            Tipo: Administrador
            ===========================
            """)
                                
            elif opcao == "0":

                print("\nENCERRANDO SISTEMA...")
                     
                break

            # Funcionalidades previstas mas ainda não implementadas
            elif opcao in ["5", "7", "9"]:

                print("\nFUNÇÃO AINDA EM DESENVOLVIMENTO.")

        # =============================================
        # ÁREA DO FUNCIONÁRIO
        # =============================================

        else:

            # REGISTRO DE PONTO
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

                # CONSULTAR STATUS  DAS JUSTIFICATIVAS ENVIADAS   
                elif subopcao == "2":
                    id_func = int(input("Digite seu ID: "))
                    ver_status_justificativa(id_func)

            # MEU PERFIL      
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
