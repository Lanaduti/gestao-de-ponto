from datetime import date, datetime
from sistema_rh import  SistemaRH 

def tela_login(sistema):
    print("\n=== ACESSO AO SISTEMA ===")

    while True:
        email = input("Email: ")
        senha = input("Senha: ")

        if sistema.login(email, senha):
            print("\nLogin realizado com sucesso!")
            break
        else:
            print("\nEmail ou senha incorretos!")

def iniciar_sistema():
    sistema = SistemaRH()
    
    tela_login(sistema)

    while True: 
        print("\n" + "="*35)
        print("SISTEMA DE RECURSOS HUMANOS - MENU PRINCIPAL")
        print("="*35)
        print("1 - Cadastrar novo funcionário")
        print("2 - Registrar ponto (Entrada/Saída/Intervalo)")
        print("3 - Calcular Horas Trabalhadas do Dia")
        print("4 - Ver lista de funcionários (Descobrir IDs)")
        print("5 - Relatório Mensal de Ponto (Ver na tela)")
        print("6 - Gerar relatório Mensal em PDF (Salvar arquivo)")
        print("7 - Enviar Justificativa (Falta/Atraso)")
        print("8 - Editar Dados do funcionário (Apenas Admin)")
        print("0 - Sair do Sistema")
        print("-" * 35)
        
        opcao = input(" Escolha uma opção: ")

        if opcao == "1":
            print("\n---  NOVO CADASTRO ---")
            nome = input("Digite o Nome: ")
            cpf = input("Digite o CPF (só números): ")
            cargo = input("Digite o Cargo: ")
            setor = input("Digite o Setor: ")
            salario = float(input("Digite o Salário Base (ex: 3500.00): ")) 
            
            sistema.cadastrar_funcionario(nome, cpf, cargo, setor, salario, date.today())
        
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