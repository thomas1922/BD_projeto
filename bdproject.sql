CREATE TABLE utilizador (
	id	 SERIAL,
	username VARCHAR(512) NOT NULL,
	password VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE administrador (
	salario	 FLOAT(8) NOT NULL,
	temposervico	 INTEGER NOT NULL,
	nome		 VARCHAR(512) NOT NULL,
	utilizador_id INTEGER,
	PRIMARY KEY(utilizador_id)
);

CREATE TABLE vendedor (
	nif		 INTEGER UNIQUE NOT NULL,
	email	 VARCHAR(512) NOT NULL,
	cidade	 VARCHAR(512) NOT NULL,
	rua		 VARCHAR(512) NOT NULL,
	utilizador_id INTEGER,
	PRIMARY KEY(utilizador_id)
);

CREATE TABLE cliente (
	email	 VARCHAR(512) NOT NULL,
	cidade	 VARCHAR(512) NOT NULL,
	rua		 VARCHAR(512) NOT NULL,
	utilizador_id INTEGER,
	PRIMARY KEY(utilizador_id)
);

CREATE TABLE produto (
	produtoid		 INTEGER NOT NULL,
	descricao		 VARCHAR(512) NOT NULL,
	preco			 FLOAT(8) NOT NULL,
	stock			 INTEGER NOT NULL,
	versao		 INTEGER NOT NULL,
	vendedor_utilizador_id INTEGER NOT NULL,
	PRIMARY KEY(produtoid,versao)
);

CREATE TABLE encomenda (
	encomendaid		 SERIAL,
	data			 TIMESTAMP NOT NULL,
	precototal		 FLOAT(8) NOT NULL,
	cliente_utilizador_id INTEGER NOT NULL,
	PRIMARY KEY(encomendaid)
);

CREATE TABLE carrinho (
    quantidade         INTEGER NOT NULL,
    produto_produtoid     INTEGER NOT NULL,
    produto_versao     INTEGER NOT NULL,
    encomenda_encomendaid INTEGER NOT NULL
);


CREATE TABLE smartphone (
	processador	 VARCHAR(512) NOT NULL,
	memoria		 VARCHAR(512) NOT NULL,
	bateria		 VARCHAR(512) NOT NULL,
	camara		 VARCHAR(512) NOT NULL,
	produto_produtoid INTEGER NOT NULL,
	produto_versao	 INTEGER NOT NULL,
	PRIMARY KEY(produto_produtoid,produto_versao)
);

CREATE TABLE televisao (
	tamanho		 INTEGER NOT NULL,
	definicao	 VARCHAR(512) NOT NULL,
	produto_produtoid INTEGER NOT NULL,
	produto_versao	 INTEGER NOT NULL,
	PRIMARY KEY(produto_produtoid,produto_versao)
);

CREATE TABLE computador (
	grafica		 VARCHAR(512) NOT NULL,
	ram		 VARCHAR(512) NOT NULL,
	bateria		 VARCHAR(512) NOT NULL,
	tamanhoecra	 VARCHAR(512) NOT NULL,
	produto_produtoid INTEGER NOT NULL,
	produto_versao	 INTEGER NOT NULL,
	PRIMARY KEY(produto_produtoid,produto_versao)
);

CREATE TABLE coment (
	commentid	 SERIAL,
	coment		 VARCHAR(512),
	utilizador_id	 INTEGER,
	produto_produtoid INTEGER NOT NULL,
	produto_versao	 INTEGER NOT NULL,
	PRIMARY KEY(commentid,utilizador_id)
);

CREATE TABLE rating (
	classificacao	 INTEGER NOT NULL,
	comentario		 VARCHAR(512) NOT NULL,
	produto_produtoid	 INTEGER NOT NULL,
	produto_versao	 INTEGER NOT NULL,
	cliente_utilizador_id INTEGER NOT NULL
);

CREATE TABLE notificacoes (
    mensagem     VARCHAR(512),
    utilizador_id INTEGER NOT NULL
);

CREATE TABLE coment_coment (
	coment_commentid	 INTEGER,
	coment_utilizador_id	 INTEGER,
	coment_commentid1	 INTEGER NOT NULL,
	coment_utilizador_id1 INTEGER NOT NULL,
	PRIMARY KEY(coment_commentid,coment_utilizador_id)
);

ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE vendedor ADD CONSTRAINT vendedor_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE cliente ADD CONSTRAINT cliente_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE produto ADD CONSTRAINT produto_fk1 FOREIGN KEY (vendedor_utilizador_id) REFERENCES vendedor(utilizador_id);
ALTER TABLE encomenda ADD CONSTRAINT encomenda_fk1 FOREIGN KEY (cliente_utilizador_id) REFERENCES cliente(utilizador_id);
ALTER TABLE carrinho ADD CONSTRAINT carrinho_fk1 FOREIGN KEY (produto_produtoid,produto_versao) REFERENCES produto(produtoid,versao);
ALTER TABLE carrinho ADD CONSTRAINT carrinho_fk3 FOREIGN KEY (encomenda_encomendaid) REFERENCES encomenda(encomendaid);
ALTER TABLE smartphone ADD CONSTRAINT smartphone_fk1 FOREIGN KEY (produto_produtoid,produto_versao) REFERENCES produto(produtoid,versao);
ALTER TABLE televisao ADD CONSTRAINT televisao_fk1 FOREIGN KEY (produto_produtoid,produto_versao) REFERENCES produto(produtoid,versao);
ALTER TABLE computador ADD CONSTRAINT computador_fk1 FOREIGN KEY (produto_produtoid,produto_versao) REFERENCES produto(produtoid,versao);
ALTER TABLE coment ADD CONSTRAINT coment_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE coment ADD CONSTRAINT coment_fk2 FOREIGN KEY (produto_produtoid,produto_versao) REFERENCES produto(produtoid,versao);
ALTER TABLE rating ADD CONSTRAINT rating_fk1 FOREIGN KEY (produto_produtoid,produto_versao) REFERENCES produto(produtoid,versao);
ALTER TABLE rating ADD CONSTRAINT rating_fk3 FOREIGN KEY (cliente_utilizador_id) REFERENCES cliente(utilizador_id);
ALTER TABLE notificacoes ADD CONSTRAINT notificacoes_fk1 FOREIGN KEY (utilizador_id) REFERENCES utilizador(id);
ALTER TABLE coment_coment ADD CONSTRAINT coment_coment_fk1 FOREIGN KEY (coment_commentid,coment_utilizador_id) REFERENCES coment(commentid,utilizador_id);
ALTER TABLE coment_coment ADD CONSTRAINT coment_coment_fk3 FOREIGN KEY (coment_commentid1,coment_utilizador_id1) REFERENCES coment(commentid,utilizador_id);
