# Sistema de Registro de Ponto

## Descrição

Este projeto consiste no desenvolvimento de um sistema de registro de ponto eletrônico com integração à folha de pagamento, como atividade acadêmica do curso de Ciência da Computação.

O sistema tem como objetivo registrar a jornada de trabalho dos colaboradores, calcular as horas trabalhadas e gerar informações relacionadas à folha salarial.

---

## Funcionalidades

* Registro de ponto (entrada, saída e intervalos)
* Cálculo de horas trabalhadas
* Geração de relatórios mensais
* Cadastro de funcionários
* Sistema de autenticação (empregado e administrador)
* Registro de justificativas (faltas, atrasos e atestados)
* Controle de banco de horas
* Cálculo da folha de pagamento
* Geração de contracheque
* Aplicação de descontos (INSS, FGTS, vale transporte)
* Controle de férias e 13º salário

---

## Banco de Dados

O sistema utiliza o PostgreSQL como banco de dados relacional.

A estrutura foi definida a partir de um modelo entidade-relacionamento (DER), contemplando as seguintes entidades:

* Funcionário
* Usuário
* Registro de Ponto
* Justificativa
* Folha de Pagamento
* Desconto
* Banco de Horas

O script de criação das tabelas está disponível no arquivo:

database.sql

---

## Tecnologias Utilizadas

* Python (back-end)
* PostgreSQL (banco de dados)
* Git e GitHub (versionamento)
* HTML e CSS (interface em desenvolvimento)

---

## Metodologia

O projeto está sendo desenvolvido com base em conceitos de metodologias ágeis, utilizando Sprints para organização das entregas e um quadro Kanban para acompanhamento das atividades.

---

## Equipe

* Alana Kelly Reis da Silva
* Jayane Ellen
* João Victor

Estudantes de Ciência da Computação

---
## Documentação
- Requisitos Funcionais: docs/requisitos_funcionais.md
---
## Status do Projeto

Em desenvolvimento

