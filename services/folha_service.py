from fpdf import FPDF
from conexao import conectar_banco


def gerar_contracheque(id_funcionario):

    conn = conectar_banco()

    if conn:
        try:

            cursor = conn.cursor()

            sql = """
                SELECT
                    nome,
                    cargo,
                    salario_base,
                    vale_transporte
                FROM funcionario
                WHERE id = %s
            """

            cursor.execute(sql, (id_funcionario,))

            funcionario = cursor.fetchone()

            if funcionario:

                nome = funcionario[0]
                cargo = funcionario[1]
                salario = float(funcionario[2])
                vt = funcionario[3]

                desconto_vt = 0

                if vt == "S":
                    desconto_vt = salario * 0.06

                desconto_inss = salario * 0.08

                salario_liquido = (
                    salario
                    - desconto_vt
                    - desconto_inss
                )

                print(f"""
===================================
CONTRACHEQUE
===================================

Funcionário: {nome}
Cargo: {cargo}

Salário Base: R$ {salario:.2f}

Desconto VT: R$ {desconto_vt:.2f}
INSS: R$ {desconto_inss:.2f}

-----------------------------------

SALÁRIO LÍQUIDO:
R$ {salario_liquido:.2f}

""")

        except Exception as e:
            print(f"Erro: {e}")

        finally:
            conn.close()

def exportar_relatorio_pdf(
    id_funcionario,
    mes,
    ano
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(
        200,
        10,
        txt=f"Funcionário: {id_funcionario}",
        ln=True
    )

    pdf.cell(
        200,
        10,
        txt=f"Mês: {mes}",
        ln=True
    )

    pdf.cell(
        200,
        10,
        txt=f"Ano: {ano}",
        ln=True
    )

    nome_arquivo = f"relatorio_{id_funcionario}.pdf"

    pdf.output(nome_arquivo)

    print(f"""
PDF EXPORTADO COM SUCESSO!

Arquivo:
{nome_arquivo}
""")