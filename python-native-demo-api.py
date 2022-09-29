
from flask import request, jsonify,Flask
import logging, psycopg2
import hashlib
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = str(os.environ.get("SECRET_KEY"))


StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}
##########################################################
## DATABASE ACCESS
##########################################################

#def db_connection1():
#    db = psycopg2.connect(
#        user='usertest',
#        password='usertest',
#        host='127.0.0.1',
#        port='5432',
#        database='dbtesting'
#    )
#    return db

def db_connection():
    db = psycopg2.connect(
        user=str(sys.argv[1]),
        password=str(sys.argv[2]),
        host=str(sys.argv[3]),
        port=str(sys.argv[4]),
        database=str(sys.argv[5])
    )
    return db


@app.route('/dbproj')
def landing_page():
    return """
     <!doctype html>
    <html>
    <style>
        body{
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>

    <body>
      Bem vindos à nossa loja!  <br/>
    <br/> Made by:
     Rui Santos/Tomás Dias <br/>
     <br/> BDPROJ 2021/2022 <br/>
     <img src= "https://nloja.com/br/img/loja-responsiva.png" height: auto>
    </body>
    </html>

    <br/>

    """


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'access-token' in request.headers:
            token = request.headers['access-token']
            logger.debug(f'payload: {token}')

        if not token:
            current_id=-1
            return f(current_id,token, *args, **kwargs)
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            id = data["id"]
            current_id = id
        except:
            return jsonify({'status': StatusCodes['api_error'], 'erro': 'token invalido'})
        return f(current_id, token,*args, **kwargs)

    return decorated




# adicionar utilizadores
@app.route("/dbproj/user", methods=['POST'])
@token_required
def add_user(current_id,token):
    logger.info("registar um utilizador")
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')

    verifica = """ SELECT count(utilizador_id) from administrador where utilizador_id=%s"""
    verifica_values = current_id

    statement1 = """
                  INSERT INTO utilizador(username,password)
                  VALUES(%s, %s);"""
    id = """
                  select id from utilizador where username=%s and password=%s;"""


    val_pass = hashlib.sha256(payload["password"].encode()).hexdigest()
    logger.info(payload["username"])

    values = (payload["username"], val_pass)
    valuesid = (payload["username"],val_pass)
    if(current_id==-1):
        if "username" not in payload or "password" not in payload or "email" not in payload or "cidade" not in payload or "rua" not in payload:
            return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})
        valuesuser = [payload["email"], payload["cidade"], payload["rua"]]
        statement = """
                      INSERT INTO cliente(email,cidade, rua, utilizador_id)
                      VALUES(%s, %s, %s, %s);"""
    else:
        if "username" not in payload or "password" not in payload or "nif" not in payload or "email" not in payload or "cidade" not in payload or "rua" not in payload:
            if "username" not in payload or "password" not in payload or "salario" not in payload or "temposervico" not in payload or "nome" not in payload:
                return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})
            else:
                valuesuser = [payload["salario"], payload["temposervico"], payload["nome"]]
                statement = """
                              INSERT INTO administrador(salario, temposervico,nome, utilizador_id)
                              VALUES(%s, %s, %s, %s);"""
        else:
            valuesuser = [payload["nif"], payload["email"], payload["cidade"], payload["rua"]]
            statement = """
                          INSERT INTO vendedor(nif,email, cidade, rua, utilizador_id)
                          VALUES(%s, %s, %s, %s, %s);"""
    try:
        if(current_id!=-1):
            cur.execute(verifica,verifica_values)
            eadmin=cur.fetchall()[0][0]
            if(eadmin==0):
                return jsonify({'status': StatusCodes['api_error'], 'errors': "Precisa ser administrador para adicionar vendedores/admins"})

        cur.execute(statement1, values)
        cur.execute(id, valuesid)
        id = cur.fetchall()
        valuesuser.append(id[0][0])
        cur.execute(statement, valuesuser)
        cur.execute('commit')
        result = {'status': StatusCodes['success'], 'results': id[0][0]}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'POST /dbproj/user - error: {error}')
        result = {'status': StatusCodes['api_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)



@app.route("/dbproj/user", methods=['PUT'])
def login():
    logger.info("---LOGIN--")
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    logger.debug(f'payload: {payload}')
    try:
        password = str(hashlib.sha256(payload["password"].encode()).hexdigest())
        #password = payload["password"]
        cur.execute("SELECT password from utilizador where username=%s",(payload["username"],))
        pwd = cur.fetchall()
        if(len(pwd)==0):
            response = {'status': StatusCodes['api_error'], 'erro': 'LOGIN INVALIDO'}
            return jsonify(response)
        elif pwd[0][0] != password and pwd[0][0] !=  payload["password"]:
            response = {'status': StatusCodes['api_error'],'erro': 'LOGIN INVALIDO'}
            return jsonify(response)
        elif pwd[0][0] == password:
            cur.execute("SELECT id from utilizador where username=%s and password=%s", (payload["username"],password,))
        elif pwd[0][0] == payload["password"]:
            cur.execute("SELECT id from utilizador where username=%s and password=%s", (payload["username"], payload["password"],))

        id = cur.fetchall()
        token=jwt.encode({'id':id[0], 'exp': datetime.utcnow()+timedelta(minutes=60)}, app.config['SECRET_KEY'], algorithm="HS256")
        response = {'status': StatusCodes['success'], 'auth_token':token}
        cur.execute('commit')
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'PUT /dbproj/user - error: {error}')
        response = {'status': StatusCodes['api_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()


    return jsonify(response)



@app.route("/dbproj/product/<produto_id>", methods=['PUT'])
@token_required
def update_product(current_id, token, produto_id):
    logger.info("update a um produto")
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()

    logger.info(payload)

    verifica_vendedor=""" select count(utilizador_id) from vendedor where vendedor.utilizador_id=%s;"""
    values_verifica = current_id

    cur.execute(verifica_vendedor, values_verifica)
    res = cur.fetchall()[0][0]
    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'precisa de ser um vendedor para efetuar esta operação'}
        return jsonify(response)

    verifica = """ SELECT count(*) from produto where vendedor_utilizador_id=%s and produtoid=%s"""
    verifica_values = [current_id[0], produto_id]


    verifica_tv = """select count(*) from televisao where produto_produtoid=%s;"""
    verifica_smartphone = """select count(*) from smartphone where produto_produtoid=%s;"""
    verifica_pc = """select count(*) from computador where produto_produtoid=%s;"""

    statement = """
                  INSERT into produto(produtoid, descricao, preco, stock, versao, vendedor_utilizador_id)
                  values( %s, %s, %s, %s, %s, %s);
                  """
    values = [produto_id, payload["descricao"],payload["preco"],payload["stock"]]

    statementversao = """select max(versao) from produto where produtoid=%s;"""
    values_versao = str(produto_id)

    try:
        cur.execute(verifica,verifica_values)
        exists = cur.fetchall()[0][0]
        if(exists==0):
            result = {'status': StatusCodes['api_error'], 'errors': "Este produto não existe ou não é seu"}
            return jsonify(result)
        else:
            cur.execute(verifica_tv,current_id)
            if cur.fetchall()[0][0]==0:
                cur.execute(verifica_pc, current_id)
                if cur.fetchall()[0][0] == 0:
                    cur.execute(verifica_smartphone, current_id)
                    if "descricao" not in payload or "preco" not in payload or "stock" not in payload or "processador" not in payload or "memoria" not in payload or "bateria" not in payload or "camara" not in payload:
                        return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})
                    else:
                        statement1 = """ INSERT INTO smartphone(processador,memoria,bateria,camara,produto_versao, produto_produtoid) 
                        VALUES(%s, %s, %s, %s, %s, %s)"""
                        values1 = [payload["processador"], payload["memoria"], payload["bateria"], payload["camara"]]
                else:
                    if "descricao" not in payload or "preco" not in payload or "stock" not in payload or "grafica" not in payload or "ram" not in payload or "bateria" not in payload or "tamanhoecra" not in payload:
                        return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})
                    else:
                        statement1 = """ INSERT INTO computador(grafica,ram,bateria,tamanhoecra,produto_versao, produto_produtoid) 
                        VALUES(%s, %s, %s, %s, %s, %s)"""
                        values1 = [payload["grafica"], payload["ram"], payload["bateria"], payload["tamanhoecra"]]
            else:
                if "descricao" not in payload or "preco" not in payload or "stock" not in payload or "tamanho" not in payload or "definicao" not in payload:
                    return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})
                else:
                    statement1 = """ INSERT INTO televisao(tamanho,definicao,produto_versao, produto_produtoid) 
                    VALUES(%s, %s, %s, %s)"""
                    values1 = [payload["tamanho"], payload["definicao"]]
        cur.execute(statementversao,values_versao)
        v = cur.fetchall()[0][0]
        values.append(v+1)
        values.append(current_id[0])
        cur.execute(statement,values)
        values1.append(v+1)
        values1.append(produto_id)
        cur.execute(statement1,values1)
        cur.execute('commit')
        result = {'status': StatusCodes['success']}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'PUT /dbproj/product/<produto_id> - error: {error}')
        result = {'status': StatusCodes['api_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)

@app.route('/dbproj/product', methods=['POST'])
@token_required
def insert_products(current_id,token):
    logger.info("inserir um produto")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.debug(f'payload: {payload}')

    verifica_vendedor=""" select count(utilizador_id) from vendedor where vendedor.utilizador_id=%s;"""
    values_verifica = current_id

    cur.execute(verifica_vendedor, values_verifica)
    res = cur.fetchall()[0][0]
    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'precisa de ser um vendedor para efetuar esta operação'}
        return jsonify(response)

    id = """
            select count(produtoid) from produto;
            """

    new_id= """select max(produtoid) from produto;"""

    statement = """
                  INSERT into produto(produtoid, descricao, preco, stock, versao, vendedor_utilizador_id) 
                  values( %s, %s, %s, %s, %s, %s);
                  """

    values = [-1, payload["descricao"],payload["preco"],payload["stock"],1, current_id[0]]

    try:
        if "descricao" not in payload or "preco" not in payload or "stock" not in payload or "tamanho" not in payload or "definicao" not in payload:
            if "descricao" not in payload or "preco" not in payload or "stock" not in payload or "processador" not in payload or "memoria" not in payload or "bateria" not in payload or "camara" not in payload:
                if "descricao" not in payload or "preco" not in payload or "stock" not in payload or "grafica" not in payload or "ram" not in payload or "bateria" not in payload or "tamanhoecra" not in payload:
                    return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})
                else:
                    statement1 = """ INSERT INTO computador(grafica,ram,bateria,tamanhoecra, produto_produtoid, produto_versao) 
                    VALUES(%s, %s, %s, %s, %s,%s)"""
                    values1 = [payload["grafica"], payload["ram"],payload["bateria"],payload["tamanhoecra"]]
            else:
                statement1 = """ INSERT INTO smartphone(processador,memoria,bateria,camara, produto_produtoid, produto_versao) 
                VALUES(%s, %s, %s, %s, %s,%s)"""
                values1 = [payload["processador"], payload["memoria"], payload["bateria"], payload["camara"]]
        else:
            statement1 = """ INSERT INTO televisao(tamanho,definicao, produto_produtoid, produto_versao) 
            VALUES(%s, %s, %s,%s)"""
            values1 = [payload["tamanho"], payload["definicao"]]

        cur.execute(id)
        nextid = cur.fetchall()[0][0]
        values[0]=nextid+1
        cur.execute(statement, values)
        cur.execute(new_id)
        id=cur.fetchall()[0][0]
        values1.append(id)
        values1.append(1)
        cur.execute(statement1,values1)
        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': nextid+1}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'POST /dbproj/product - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)




@app.route("/dbproj/order", methods=['POST'])
@token_required
def buy_product(current_id, token):
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    logger.debug(f'payload: {payload}')
    if 'cart' not in payload:
        return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})

    verifica_utilizador =""" select count(utilizador_id) from cliente where cliente.utilizador_id=%s;"""
    values_verifica = current_id

    cur.execute(verifica_utilizador, values_verifica)
    res = cur.fetchall()[0][0]
    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'o cliente não existe'}
        return jsonify(response)

    verifica_id = """ select count(produtoid) from produto where produtoid = %s and versao=(select max(versao) from produto where produtoid=%s) and stock>=%s;"""

    nova_encomenda = """insert into encomenda(data, precototal, cliente_utilizador_id) values(%s, %s, %s) returning encomendaid"""
    values_encomenda=[datetime.utcnow(), 0, current_id[0]]

    insere="""insert into carrinho(quantidade, produto_produtoid, produto_versao,encomenda_encomendaid) values(%s,%s,(select max(versao) from produto where produtoid=%s), %s)"""
    update_stock = """update produto set stock = %s where produtoid=%s and versao=(select max(versao) from produto where produtoid=%s)"""
    old_stock="""select stock from produto where produtoid=%s and versao = (select max(versao) from produto where produtoid=%s);"""
    preco = """select preco from produto where produtoid = %s and versao = (select max(versao) from produto where produtoid=%s);"""
    update_preco_encomenda = """update encomenda set precototal=%s where encomendaid=%s"""
    try:
        precototal=0
        cur.execute(nova_encomenda, values_encomenda)
        idencomenda=cur.fetchall()[0][0]
        for i in payload['cart']:
            values1 = [i[0], i[0], i[1]]
            cur.execute(verifica_id,values1)
            exist = cur.fetchall()[0][0]
            if(exist==None):
                cur.execute('rollback')
                response = {'status': StatusCodes['api_error'], 'erro': 'o produto não existe ou nao tem stock'}
                return jsonify(response)
            else:
                values = [i[1],i[0],i[0],idencomenda]
                cur.execute(insere, values)
                values2 = [i[0], i[0]]
                cur.execute(old_stock, values2)
                stock=cur.fetchall()[0][0]
                values_stock=[stock-i[1], i[0],i[0]]
                cur.execute(update_stock,values_stock)
                cur.execute(preco, values2)
                precototal+=cur.fetchall()[0][0]*i[1]
        values_update_encomenda=[precototal, idencomenda]
        cur.execute(update_preco_encomenda, values_update_encomenda)
        cur.execute('commit')
        response={'status': StatusCodes['success'], 'results': idencomenda}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'POST /dbproj/order - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return jsonify(response)






@app.route("/dbproj/questions/<product_id>", methods=['POST'])
@token_required
def comment(current_id,token, product_id):
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    logger.debug(f'payload: {payload}')
    if 'question' not in payload:
        return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})

    verifica_utilizador =""" select count(utilizador_id) from cliente where cliente.utilizador_id=%s;"""
    values_verifica = current_id

    verifica_produto="""select count(*) from produto where produtoid=%s"""

    inserecomentario="""insert into coment(coment, utilizador_id, produto_produtoid, produto_versao) values(%s, %s, %s, (select max(versao) from produto where produtoid=%s)) returning commentid"""

    cur.execute(verifica_utilizador, values_verifica)
    res = cur.fetchall()[0][0]
    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'o cliente não existe'}
        return jsonify(response)

    cur.execute(verifica_produto, product_id)
    res1 = cur.fetchall()[0][0]
    if res1 == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'o produto nao existe'}
        return jsonify(response)

    try:
        values_insere=[payload["question"], current_id[0], product_id, product_id]
        cur.execute(inserecomentario, values_insere)
        comment_id=cur.fetchall()[0][0]
        cur.execute('commit')
        response={'status': StatusCodes['success'], 'results': comment_id}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'POST /dbproj/questions/<product_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()
    return jsonify(response)



@app.route("/dbproj/questions/<product_id>/<parent_question_id>", methods=['POST'])
@token_required
def comment_comment(current_id,token, product_id,parent_question_id):
    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()
    logger.debug(f'payload: {payload}')
    if 'question' not in payload:
        return jsonify({'status': StatusCodes['api_error'], 'erro': 'Payload errado'})


    verifica_comentario="""select count(*) from coment where commentid=%s and produto_produtoid=%s"""
    values = [parent_question_id, product_id]

    cur.execute(verifica_comentario, values)
    res = cur.fetchall()[0][0]
    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'o cliente não existe'}
        return jsonify(response)

    verifica_utilizador = """ select count(utilizador_id) from cliente where cliente.utilizador_id=%s;"""
    values_verifica = current_id

    verifica_produto = """select count(*) from produto where produtoid=%s"""

    inserecomentario = """insert into coment(coment, utilizador_id, produto_produtoid, produto_versao) values(%s, %s, %s, (select max(versao) from produto where produtoid=%s)) returning commentid"""

    find_user = """select utilizador_id from coment where commentid=%s"""

    insere_coment_coment = """insert into coment_coment(coment_commentid, coment_utilizador_id, coment_commentid1, coment_utilizador_id1) values (%s,%s, %s, %s)"""

    cur.execute(verifica_utilizador, values_verifica)
    res = cur.fetchall()[0][0]
    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'o cliente não existe'}
        return jsonify(response)

    cur.execute(verifica_produto, product_id)
    res1 = cur.fetchall()[0][0]
    if res1 == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'o produto nao existe'}
        return jsonify(response)


    try:
        values_insere = [payload["question"], current_id[0], product_id, product_id]
        cur.execute(inserecomentario, values_insere)
        comment_id = cur.fetchall()[0][0]
        cur.execute(find_user, parent_question_id)
        user = cur.fetchall()[0][0]
        values = [comment_id, current_id[0], parent_question_id, user]
        cur.execute(insere_coment_coment, values)
        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': comment_id}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'POST /dbproj/questions/<product_id>/<parent_question_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)



@app.route("/dbproj/rating/<produto_id>", methods=['POST'])
@token_required
def rating(current_id, token, produto_id):
    logger.info("deixar rating")
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()
    print(current_id)
    logger.debug(f'payload: {payload}')
    verifica_cliente = """ select count(utilizador_id) from cliente where utilizador_id=%s;"""

    cur.execute(verifica_cliente, current_id)
    res = cur.fetchall()[0][0]

    if res == 0:
        response = {'status': StatusCodes['api_error'], 'erro': 'precisa de ser um cliente para efetuar esta operação'}
        return jsonify(response)

    if 'rating' not in payload or 'comment' not in payload:
        response = {'status': StatusCodes['api_error'], 'erro': 'Payload errado'}
        return jsonify(response)

    if payload["rating"]>5 or payload["rating"]<1:
        response = {'status': StatusCodes['api_error'], 'erro': 'Classificacao inválida'}
        return jsonify(response)

    retira_prod = """select max(encomendaid) from encomenda where cliente_utilizador_id = %s;"""
    retira_versao = """select produto_versao from carrinho where encomenda_encomendaid = %s and produto_produtoid = %s """
    cria_rating = """ insert into rating(classificacao,comentario,produto_produtoid,produto_versao,cliente_utilizador_id) values(%s,%s,%s,%s,%s);"""

    try:
        cur.execute(retira_prod, current_id)
        id_encomenda = cur.fetchall()[0][0]
        if cur is None:
            response = {'status': StatusCodes['api_error'],
                        'erro': 'o cliente não comprou nenhum produto'}
            return jsonify(response)
        else:
            values1 = [id_encomenda, produto_id]
            cur.execute(retira_versao, values1)
            versao = cur.fetchall()[0][0]
            if versao is None:
                response = {'status': StatusCodes['api_error'],
                            'erro': 'o produto não foi comprado'}
                return jsonify(response)
            values2 = [payload["rating"], payload["comment"], produto_id, versao, current_id[0]]
            cur.execute(cria_rating, values2)
            cur.execute('commit')

    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'POST /dbproj/rating/<produto_id> - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        return jsonify(response)
    finally:
        if conn is not None:
            conn.close()

    response = {'status': StatusCodes['success']}
    return jsonify(response)



@app.route("/dbproj/report/year", methods=['GET'])
def report():
    logger.info("Estatisticas anuais")
    conn = db_connection()
    cur = conn.cursor()

    statement= """ select sum(encomenda.precototal), count(encomendaid), date_part('years',AGE(now(),cast(data as DATE)))*12+date_part('month',AGE(now(),cast(data as DATE))) as months from encomenda 
                   where date_part('years',AGE(now(),cast(data as DATE)))*12+date_part('month',AGE(now(),cast(data as DATE)))< 12 
                   group by months;"""
    try:
        cur.execute(statement)
        rows = cur.fetchall()
        results = []
        for row in rows:
            results.append({"month": int(row[2]), "total_value": row[0], "orders": row[1]})
        cur.execute('commit')
        response = {'status': StatusCodes['success'], 'results': results}
    except (Exception, psycopg2.DatabaseError) as error:
        cur.execute('rollback')
        logger.error(f'GET /dbproj/report/year - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)


@app.route("/dbproj/product/<produto_id>", methods=['GET'])
def info_genericas(produto_id):
    logger.info("info")
    conn = db_connection()
    cur = conn.cursor()

    one_query = """ select descricao, stock,(select (avg(classificacao)) from rating where rating.produto_produtoid=%s),(select array_agg(preco) from produto where produtoid=%s), (select array_agg(coment.coment) from coment where coment.produto_produtoid=%s) from produto where versao=(select max(versao) from produto where produtoid=%s);
              """
    list_prodid = [produto_id for _ in range(4)]
    try:
        cur.execute(one_query,list_prodid)
        res_query = cur.fetchall()
        if len(res_query) == 0:
            response = {'status': StatusCodes['api_error'],
                        'erro': 'o produto nao existe'}
            return jsonify(response)

        resultado = res_query[0]

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/product - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        return jsonify(response)

    finally:
        if conn is not None:
            conn.close()
    response = {'status':StatusCodes['success'],'error':0,'results':{'product_description':resultado[0],'prices':resultado[3],'rating':resultado[2],'comments':resultado[4],'stock':resultado[1] }}
    return jsonify(response)


@app.route("/dbproj/notification", methods=['GET'])
@token_required
def show_notifications(current_id,token):
    logger.info("notifications ")
    conn = db_connection()
    cur = conn.cursor()
    verifica = """ SELECT count(id) from utilizador where id=%s;"""
    show = """ select array_agg(mensagem) from notificacoes where utilizador_id =%s;"""
    try:
        print(current_id)
        cur.execute(verifica,current_id)
        print("aqui")
        res = cur.fetchall()[0][0]
        if res == 0:
            response = {'status': StatusCodes['api_error'],
                        'erro': 'precisa de estar registado para ter notificações'}
            return jsonify(response)
        cur.execute(show,current_id)
        notificoes = cur.fetchall()[0][0]
        if notificoes is None:
            response = {'status': StatusCodes['api_error'],
                        'erro': 'ainda não possui notificações'}
            return jsonify(response)

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f'GET /dbproj/notification - error: {error}')
        response = {'status': StatusCodes['internal_error'], 'errors': str(error)}
        return jsonify(response)

    finally:
        if conn is not None:
            conn.close()

    response = {'status': StatusCodes['success'], 'erro': 0, 'notification(s)': notificoes}
    return jsonify(response)

## MAIN
##########################################################
if __name__ == "__main__":
    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.1 online: http://{host}:{port}')



