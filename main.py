from datetime import date
from sistema_rh import SistemaRH

def iniciar_sistema():
    sistema = SistemaRH()

    print(" Iniciando o Sistema de RH...\n")

    data_hoje = date.today()

    id_novo_funcionario = sistema.cadastrar_funcionario(
        nome="Vitruviano", 
        cpf="11122233344",          
        cargo="Analista Pleno",
        setor="TI",
        salario_base=5000.00,
        data_admissao=data_hoje
    )
    if id_novo_funcionario:
        sistema.cadastrar_usuario(
            email="vitruviano999@gmail.com",
            senha="senha123",
            tipo="Admin",
            id_funcionario=id_novo_funcionario
        )

    sistema.login(email="vitruviano999@gmail.com", senha="senha_errada") # Vai negar
    sistema.login(email="vitruviano999@gmail.com", senha="senha123")        # Vai aceitar
    sistema.registrar_ponto(id_funcionario= id_novo_funcionario)
    sistema.registrar_ponto(id_funcionario= id_novo_funcionario)
    sistema.registrar_ponto(id_funcionario= id_novo_funcionario)
    sistema.registrar_ponto(id_funcionario= id_novo_funcionario)
    sistema.registrar_ponto(id_funcionario= id_novo_funcionario)

# O botão de ligar do sistema:
if __name__ == "__main__":
    iniciar_sistema()