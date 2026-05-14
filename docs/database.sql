CREATE TABLE IF NOT EXISTS funcionario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100)NOT NULL,
    cpf VARCHAR(11)NOT NULL,
    cargo VARCHAR(50),
    setor VARCHAR(50),
    salario_base DECIMAL(10,2),
    data_admissao DATE
);

CREATE TABLE IF NOT EXISTS usuario (
     id SERIAL PRIMARY KEY,
	 email VARCHAR(100)NOT NULL,
	 senha VARCHAR(200)NOT NULL,
	 tipo VARCHAR(50),
	 id_funcionario INT,

	 
	 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id)
);

CREATE TABLE IF NOT EXISTS registro_ponto (

     id SERIAL PRIMARY KEY,
	 id_funcionario INT,
	 data_registro DATE NOT NULL,
	 entrada TIME,
	 saida_intervalo TIME,
	 volta_intervalo TIME,
	 saida TIME,
	 localizacao VARCHAR(100),

	 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id)
);

CREATE TABLE IF NOT EXISTS justificativa (
     id SERIAL PRIMARY KEY,
	 id_funcionario INT,
	 data_justificativa DATE,
	 tipo VARCHAR(50),
	 descricao TEXT,
	 horas_compensadas BOOLEAN,
	 quantidade_horas DECIMAL(5,2),

	 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id)
);

CREATE TABLE IF NOT EXISTS folha_pagamento (
     id SERIAL PRIMARY KEY,
	 id_funcionario INT,
	 mes INT,
	 ano INT,
	 salario_bruto DECIMAL(10,2),
	 descontos DECIMAL(10,2),
	 salario_liquido DECIMAL(10,2),

	 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id)
);

CREATE TABLE IF NOT EXISTS desconto (
     id SERIAL PRIMARY KEY,
	 id_funcionario INT,
	 tipo VARCHAR(100),
	 valor DECIMAL(10,2),

	 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id)
);

CREATE TABLE IF NOT EXISTS banco_horas (
     id SERIAL PRIMARY KEY,
	 id_funcionario INT,
	 horas_extras DECIMAL(5,2),
	 horas_devidas DECIMAL(5,2),

	 FOREIGN KEY (id_funcionario) REFERENCES funcionario(id)
);
