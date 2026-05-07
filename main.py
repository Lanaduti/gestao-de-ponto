from datetime import date, datetime
from sistema_rh import  SistemaRH 


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

# Menu princinpal ADM
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

# Menu princinpal funcionários
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

# Submenu de gerenciamento de funcionários
def menu_funcionarios():

    print("\n" + "="*35)
    print("MENU FUNCIONÁRIOS")
    print("="*35)

    print("1 - Cadastrar Funcionário")
    print("2 - Listar Funcionários")
    print("3 - Editar Funcionário")
    print("4 - Excluir Funcionário")
    print("0 - Voltar")

    return input("\nEscolha uma opção: ")

def iniciar_sistema():

    sistema = SistemaRH()
    
 # Guarda informações do usuário logado 
    usuario_logado = tela_login(sistema)

    print(f"\nTIPO DE USUÁRIO: {usuario_logado['tipo']}")

# Verifica o tipo de usuário para liberar menus diferentes
    tipo_usuario = usuario_logado["tipo"]

    while True:

# Exibe menus diferentes dependendo do tipo de usuário  
        if tipo_usuario == "admin":
            opcao = menu_admin()
            
        else:
            opcao = menu_funcionario()

 # Menu de gerenciamento de funcionário
        if opcao == "1":
            
            subopcao = menu_funcionarios()

# Cadastro de funcionário
        if subopcao == "1":

          print("\n--- NOVO CADASTRO ---")

          nome = input("Digite o Nome: ")
          cpf = input("Digite o CPF (só números): ")
          cargo = input("Digite o Cargo: ")
          setor = input("Digite o Setor: ")

          salario = float(input("Digite o Salário Base: "))

          sistema.cadastrar_funcionario(
            nome,
            cpf,
            cargo,
            setor,
            salario,
            date.today()
        )

# Lista funcionários cadastrados
        elif subopcao == "2":

         sistema.listar_funcionarios()

# Editar funcionários
        elif subopcao == "3":

                print("\n--- EDITAR FUNCIONÁRIO ---")

                id_func = int(input("Digite o ID do funcionário: "))

                novo_cargo = input("Novo cargo: ")
                novo_setor = input("Novo setor: ")
                novo_salario = float(input("Novo salário: "))

                sistema.editar_funcionario(
                    id_func,
                    novo_cargo,
                    novo_setor,
                    novo_salario
                )
        
# Excluir funcionários        
        elif subopcao == "4":

                print("\n--- EXCLUIR FUNCIONÁRIO ---")

                id_func = int(input("Digite o ID do funcionário: "))

                sistema.excluir_funcionario(id_func)
                
        elif subopcao == "0":

                continue

        elif opcao == "2":
            print("\n---  BATER PONTO ---")
            try:
                id_func = int(input("Digite o ID do funcionário (apenas o número): "))
                sistema.registrar_ponto(id_func)
            except ValueError:
                print(" ERRO: Por favor, digite apenas números para o ID!")
                
        elif opcao == "3":
            print("\n---  CÁLCULO DE HORAS ---")
            try:
                id_func = int(input("Digite o ID do funcionário (apenas o número): "))
                sistema.calcular_horas_trabalhadas(id_func, date.today())
            except ValueError:
                print(" ERRO: Por favor, digite apenas números para o ID!")

        elif opcao == "4":
            sistema.listar_funcionarios()
            
        elif opcao == "0":
            print("\n Encerrando o sistema... Até logo!\n")
            break

        elif opcao == "5": 
            print ("\n --- Relátorio Mensal ---")
            try: 
                id_func = int(input("Digite o ID do funcionário: "))
                mes = int(input("Digite o Mês (ex: 4 de Abril): "))
                ano  =int(input("Digite o Ano (ex: 2026):"))

                sistema.relatorio_mensal(id_func, mes, ano)
            except ValueError :
                print(" ERRO: Por favor, digite apenas números interios!")

        elif opcao == "6": 
            print("\n --- Exportar Relatório PDF ---")
            try: 
                id_func = int(input("Digite ID do funcionário:"))
                mes = int(input("Digite o Mês (ex: 5 de Maio):"))
                ano = int(input("Digite o ano (ex:2026):"))

                sistema.exportar_relatorio_pdf(id_func, mes, ano)
            except ValueError:
                print("ERRO: Por favor, digite apenas números inteiros!")

        elif opcao == "7":
            print("\n---  ENVIAR JUSTIFICATIVA ---")
            try:
                id_func = int(input("Digite o ID do funcionário: "))
                data_str = input("Digite a data da falta/atraso (DD/MM/AAAA): ")
                data_falta = datetime.strptime(data_str, "%d/%m/%Y").date()
                
                motivo = input("Digite o motivo (ex: Consulta médica, Pneu furado): ")
                comp = input("Haverá compensação de horas? (S/N): ").strip().upper()
                compensacao = "Sim" if comp == "S" else "Não"
                
                sistema.enviar_justificativa(id_func, data_falta, motivo, compensacao)
            except ValueError:
                print(" ERRO: Verifique se o ID é apenas número e se a data está no formato correto (DD/MM/AAAA)!")

        elif opcao == "8":
            print("\n---  ÁREA RESTRITA (ADMINISTRAÇÃO) ---")
            email_admin = input("Digite o e-mail corporativo (Admin): ")
            senha_admin = input("Digite a senha: ")

            if sistema.verificar_admin(email_admin, senha_admin):
                print("\n ACESSO LIBERADO! MODO EDIÇÃO ATIVADO.")
                try:
                    id_func = int(input("Digite o ID do funcionário que será alterado: "))
                    print("\n-- Preencha os novos dados --")
                    novo_cargo = input("Novo Cargo: ")
                    novo_setor = input("Novo Setor: ")
                    novo_salario = float(input("Novo Salário Base (ex: 4500.00): "))
                    
                    sistema.editar_funcionario(id_func, novo_cargo, novo_setor, novo_salario)
                except ValueError:
                    print(" ERRO: O ID e o Salário precisam ser apenas números!")
            else:
                print("\n ACESSO NEGADO: E-mail/Senha incorretos ou perfil sem permissão de Administrador!")

if __name__ == "__main__":
    iniciar_sistema() 