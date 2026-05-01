from datetime import date 
from sistema_rh import  SistemaRH 

def iniciar_sistema():
    sistema = SistemaRH()

    while True: 
        print("\n" + "="*35)
        print("SISTEMA DE RECURSOS HUMANOS - MENU PRINCIPAL")
        print("="*35)
        print("1 - Cadastrar novo funcionário")
        print("2 - Registrar ponto (Entrada/Saída/Intervalo)")
        print("3 - Calcular Horas Trabalhadas do Dia")
        print("4 - Ver lista de funcionários (Descobrir IDs)")
        print("5 - Relatório Mensal de Ponto")
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
                
if __name__ == "__main__":
    iniciar_sistema()
   