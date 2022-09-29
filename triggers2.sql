create or replace function triger2()
returns trigger
language plpgsql
as $$
declare
    cur cursor for select quantidade, produto_produtoid from carrinho where encomenda_encomendaid=new.encomendaid;
    iduser integer;

begin
    insert into notificacoes(mensagem, utilizador_id)
    values('A sua encomenda de id '|| new.encomendaid ||' foi recebida. Aguarde o envio', new.cliente_utilizador_id);
        
    for r in cur
        loop
            select distinct(vendedor_utilizador_id) into iduser from produto
            where produtoid=r.produto_produtoid;
            insert into notificacoes(mensagem, utilizador_id)
            values('O produto de id ' || r.produto_produtoid || ' foi comprado na quantidade '|| r.quantidade || ' pelo utilizador ' || new.cliente_utilizador_id, iduser);
            
        end loop;
return null;
end;
$$;


create or replace trigger notifica after update on encomenda for each row
execute function triger2()

